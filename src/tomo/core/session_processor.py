import asyncio
import logging
import os
import typing

from tomo.core.actions import (
    Action,
    ActionDisableSession,
    Listen,
)
from tomo.core.events import ActionFailed, ActionExecuted, Event, AddPendingActions
from tomo.core.session import Session, SessionStatus
from tomo.core.policies import PolicyManager
from tomo.core.policies import PolicyPrediction
from tomo.core.policies.models import ExtractedAction
from tomo.shared.exceptions import TomoFatalException
from tomo.shared.output_channel import OutputChannel
from tomo.core.session_managers.base import SessionManager

logger = logging.getLogger(__name__)
MAX_NUMBER_OF_PREDICTIONS = int(os.environ.get("MAX_NUMBER_OF_PREDICTIONS", "100"))


class SessionProcessor:
    """The message processor is interface for communicating with a bot model."""

    def __init__(
        self,
        session_manager: SessionManager,
        policy_manager: PolicyManager,
        max_number_of_predictions: int = MAX_NUMBER_OF_PREDICTIONS,
    ) -> None:
        """Initializes a `MessageProcessor`."""
        self.session_manager = session_manager
        self.policy_manager = policy_manager
        self.max_number_of_predictions = max_number_of_predictions
        self._session_locks = {}

    async def evolve_session(self, session_id, output_channel: OutputChannel):
        session_lock = self._session_locks.get(session_id)
        if session_lock is None:
            session_lock = asyncio.Lock()
            self._session_locks[session_id] = session_lock
        async with session_lock:
            return await self._evolve_session(session_id, output_channel)

    async def _evolve_session(self, session_id, output_channel: OutputChannel):
        session: Session = await self.session_manager.get_session(session_id)
        if session is None:
            raise ValueError(f"session {session_id} not exist")

        should_wait_for_user = False
        if len(session.pending_actions) > 0:
            pending_actions = [
                Action.create(action.name, **(action.arguments or {}))
                for action in session.pending_actions
            ]
            should_wait_for_user = Listen.action_name() in [
                action.name for action in session.pending_actions
            ]
            events = []
            for action in pending_actions:
                _events = await self._run_action(
                    action,
                    session,
                    output_channel=output_channel,
                    policy_name=None,
                )
                events.extend(_events or [])
            session = await self.session_manager.update_with_events(
                session.session_id, events
            )
            session.pending_actions = []
            if should_wait_for_user:
                session.status = SessionStatus.WAITING
            else:
                session.status = SessionStatus.ACTIVE
            await self.session_manager.save(session)

        if not should_wait_for_user:
            await self._run_prediction_loop(session_id, output_channel)

    # Prediction and action execution
    async def _run_prediction_loop(
        self,
        session_id: str,
        output_channel: OutputChannel,
    ):
        async def _process(prediction: PolicyPrediction):
            session = await self.session_manager.get_session(session_id)
            events = await self._handle_prediction_with_session(
                prediction, output_channel, session
            )
            session = await self.session_manager.update_with_events(
                session.session_id, events
            )
            return events

        async def _should_continue_loop(prediction: PolicyPrediction) -> bool:
            does_not_contain_listen = (
                Listen.action_name() not in prediction.action_names
            )
            all_actions_approved = not any(
                action.need_approval() for action in prediction.actions
            )

            return does_not_contain_listen and all_actions_approved

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

            await asyncio.gather(*tasks)
            test_results = await asyncio.gather(*loop_continue_tests)

            continue_loop = len(test_results) > 0 and all(test_results)

        session = await self.session_manager.get_session(session_id)
        if len(session.pending_actions) > 0:
            session.status = SessionStatus.PENDING
        else:
            session.status = SessionStatus.WAITING
        self.session_manager.save(session)

    async def _handle_prediction_with_session(
        self,
        prediction: PolicyPrediction,
        output_channel: OutputChannel,
        session: Session,
    ):
        logger.debug(f"processing prediction with actions: {prediction.action_names}")
        actions = prediction.actions
        if actions is None or len(actions) == 0:
            return []

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
            events.extend(_events or [])

        return events

    async def _run_action(
        self,
        action: Action,
        session: Session,
        output_channel: OutputChannel,
        policy_name: typing.Optional[str],
    ) -> typing.List[Event]:
        if action.need_approval():
            arguments = action.model_dump(mode="python") or None
            return [
                AddPendingActions(
                    actions=ExtractedAction(
                        name=action.action_name(), arguments=arguments
                    )
                )
            ]
        # events and return values are used to update
        # the session state after an action has been taken
        try:
            events = await action.run(output_channel, session) or []
            events.append(
                ActionExecuted(
                    action_name=action.action_name(),
                    policy=policy_name,
                )
            )
        except Exception:
            logger.exception(
                f"Encountered an exception while running action '{action.action_name()}'."
                "Bot will continue, but the actions events are lost. "
                "Please check the logs of your action server for "
                "more information."
            )
            events = [
                ActionFailed(
                    action_name=action.action_name(),
                    policy=policy_name,
                )
            ]

        return events
