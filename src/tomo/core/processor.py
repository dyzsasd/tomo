import asyncio
import logging
import os
import time
import typing

from tomo.core.actions import (
    Action,
    ActionDisableSession,
    ActionExtractSlots,
    ActionListen,
    ActionSessionStart,
)
from tomo.core.events import ActionFailed, Event, Session, UserUttered
from tomo.core.policies.manager import PolicyManager
from tomo.core.policies.policy import PolicyPrediction
from tomo.core.user_message import UserMessage
from tomo.nlu.parser import NLUParser
from tomo.shared.action_executor import ActionExector
from tomo.shared.exceptions import TomoFatalException
from tomo.shared.output_channel import OutputChannel
from tomo.shared.session_manager import SessionManager

logger = logging.getLogger(__name__)
MAX_NUMBER_OF_PREDICTIONS = int(os.environ.get("MAX_NUMBER_OF_PREDICTIONS", "100"))


class MessageProcessor:
    """The message processor is interface for communicating with a bot model."""

    async def _run_action(
        self,
        action: Action,
        session: Session,
        output_channel: OutputChannel,
        policy_name: typing.Optional[str],
    ) -> typing.List[Event]:
        # events and return values are used to update
        # the session state after an action has been taken
        try:
            # Use temporary session as we might need to discard the policy events in
            # case of a rejection.
            temporary_session = session.copy()
            events = await action.run(output_channel, temporary_session)

        except Exception:
            logger.exception(
                f"Encountered an exception while running action '{action.name}'."
                "Bot will continue, but the actions events are lost. "
                "Please check the logs of your action server for "
                "more information."
            )
            events = [
                ActionFailed(
                    action_name=action.name,
                    policy=policy_name,
                    timestamp=time.time(),
                    metadata=None,
                )
            ]

        return events

    def __init__(
        self,
        session_manager: SessionManager,
        policy_manager: PolicyManager,
        action_exector: typing.Optional[ActionExector] = None,
        max_number_of_predictions: int = MAX_NUMBER_OF_PREDICTIONS,
        on_circuit_break: typing.Optional[typing.Callable] = None,
        nlu_parser: typing.Optional[NLUParser] = None,
        session_expiration: int = 86400 * 3,  # three days in second
    ) -> None:
        """Initializes a `MessageProcessor`."""
        self.session_manager = session_manager
        self.max_number_of_predictions = max_number_of_predictions
        self.on_circuit_break = on_circuit_break
        self.action_executor = action_exector
        self.nlu_parser = nlu_parser
        self.session_expiration = session_expiration
        self.policy_manager = policy_manager

    async def start_new_session(
        self, session_id: str, output_channel: typing.Optional[OutputChannel]
    ) -> Session:
        session = await self.get_session(session_id, output_channel=output_channel)
        return session

    async def handle_message(self, message: UserMessage) -> None:
        """Handle a single message with this processor.

        1. Get the session and update the session with UserUttered event
        2. Run prediction and actions according to user's message until listen to user action.
        """
        session: Session = await self.log_message(message)

        await self._run_prediction_loop(message.output_channel, session.session_id)

    # save message in session
    async def log_message(self, message: UserMessage) -> Session:
        """Log `message` on session belonging to the message's session_id.

        1. Fetch the session from session store, it doesn't exist, then create a new one and run
           the session start action.
        2. Process user message and then apply user uterance event.
        3. update session slot according to user message entities.
        4. Save the update session with session manager.

        """
        session: Session = await self.get_session(
            message.session_id, message.output_channel
        )

        await self._handle_message_with_session(message, session)

        action_extract_slots: Action = Action.action_for_name_or_text(
            ActionExtractSlots.name, self.action_executor
        )

        events = await self._run_action(
            action_extract_slots, session, message.output_channel, None
        )
        await session.update_with_events(events)

        return session

    async def get_session(
        self,
        session_id: str,
        output_channel: typing.Optional[OutputChannel] = None,
    ) -> Session:
        """Fetches session for `session_id` and updates it.

        If a new session is created, `action_session_start` is run.

        Args:
            session_id: Conversation ID for which to fetch the tracker.
            output_channel: Output channel associated with the incoming user message.
            metadata: Data sent from client associated with the incoming user message.

        Returns:
              session for `session_id`.
        """
        session: Session = await self.session_manager.get_or_create_session(
            session_id, max_event_history=None
        )

        # if the session is new created, which means event list is empty, then session start
        # action should be executed
        if (not session.events) and session.active:
            logger.debug(
                f"Starting a new session for session ID '{session.session_id}'."
            )

            action_session_start = ActionSessionStart("Hi, I'm your assistant Tomo")

            events = await self._run_action(
                action=action_session_start,
                session=session,
                output_channel=output_channel,
                policy_name=None,
            )

            await session.update_with_events(events)

        return session

    async def _handle_message_with_session(
        self, message: UserMessage, session: Session
    ) -> None:
        # ATTENTION: parsed_data is here
        if message.parse_data:
            parse_data = message.parse_data
        else:
            parse_data = await self.nlu_parser.parse(message, session)

        # don't ever directly mutate the tracker
        # - instead pass its events to log
        await session.update_with_event(
            UserUttered(
                message_id=message.message_id,
                text=message.text,
                input_channel=message.input_channel,
                intent=parse_data["intent"],
                entities=parse_data["entities"],
                timestamp=time.time(),
                metadata=None,
            ),
        )

        logger.debug(
            f"Logged UserUtterance - tracker now has {len(session.events)} events."
        )

    async def save_session(self, session: Session) -> None:
        """Save the given tracker to the tracker store.

        Args:
            tracker: Tracker to be saved.
        """
        await self.session_manager.save(session)

    # Prediction and action execution
    async def _run_prediction_loop(
        self, output_channel: OutputChannel, session_id: str
    ):
        async def _process(prediction: PolicyPrediction):
            # TODO: Add lock
            events = self._handle_prediction_with_session(
                prediction, output_channel, session_id
            )
            return events

        async def _should_continue_loop(prediction: PolicyPrediction) -> bool:
            return not ActionListen.name in prediction.action_names

        continue_loop = True
        while continue_loop:
            # TODO: Add lock
            session = await self.session_manager.get_session(session_id)
            tasks: typing.List[asyncio.Task] = []
            loop_continue_tests: typing.List[asyncio.Task] = []
            async for prediction in self.policy_manager.run(session):
                task = asyncio.create_task(_process(prediction))
                tasks.append(task)
                loop_continue_tests.append(
                    asyncio.create_task(_should_continue_loop(prediction))
                )
            events = await asyncio.gather(*tasks)
            events = [_event for _events in events for _event in _events]

            await session.update_with_events(events)

            continue_loop = all(loop_continue_tests) and len(events) > 0

    async def _handle_prediction_with_session(
        self,
        prediction: PolicyPrediction,
        output_channel: OutputChannel,
        session_id: str,
    ):
        actions = prediction.actions
        if actions is None or len(actions) == 0:
            return []

        session = self.session_manager.get_session(session_id)
        if session is None:
            raise TomoFatalException(
                "Session cannot be found in processing prediction."
            )

        if not session.active:
            logger.warning("session is disabled, action execution is skipped.")
            return []

        # If there is an action to disable the session, run it immediately
        for action in actions:
            if not isinstance(action, ActionDisableSession):
                continue
            events = await self._run_action(
                action,
                session,
                output_channel=output_channel,
                policy_name=prediction.policy_name,
            )
            return events

        events = []
        for action in actions:
            _events = await self._run_action(
                action,
                session,
                output_channel=output_channel,
                policy_name=prediction.policy_name,
            )
            events.extend(_events)

        return events
