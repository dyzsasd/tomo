import logging
from typing import List, Optional, Dict, Text, Union, Any

from tomo.core.output_channels import OutputChannel
from tomo.core.user_message import UserMessage
from tomo.core.nlg.generator import NaturalLanguageGenerator
from tomo.shared.sessions import Session
from tomo.events import ActionExecuted, UserUttered, Event
from tomo.lock_store import LockStore
from tomo.actions import action_for_name_or_text, ActionExecutionRejected, PolicyPrediction

logger = logging.getLogger(__name__)

class MessageProcessor:
    """The message processor is responsible for processing incoming messages, running actions, 
    and managing conversation state via sessions."""

    def __init__(
        self,
        session_store: "SessionStore",
        lock_store: LockStore,
        message_parser: Optional["MessageParser"] = None,
        generator: Optional[NaturalLanguageGenerator] = None,
        action_endpoint: Optional["EndpointConfig"] = None,
        max_number_of_predictions: int = 10,
    ):
        """Initializes the message processor with a model, session store, and lock store."""
        self.session_store = session_store
        self.lock_store = lock_store
        self.message_parser = message_parser
        self.nlg = generator
        self.action_endpoint = action_endpoint
        self.max_number_of_predictions = max_number_of_predictions

    async def handle_message(self, message: UserMessage) -> Optional[List[Dict[Text, Any]]]:
        """Process a single message and handle conversation actions."""
        session = await self.log_message(message)
        session = await self.run_action_extract_slots(message.output_channel, session)
        await self._run_prediction_loop(message.output_channel, session)
        await self.save_session(session)

        if isinstance(message.output_channel, OutputChannel):
            return message.output_channel.messages
        return None

    async def log_message(self, message: UserMessage) -> Session:
        """Log the incoming user message into the session."""
        session = await self.get_session(message.session_id)
        await self._handle_message_with_session(message, session)
        return session

    async def get_session(self, sender_id: Text) -> Session:
        """Retrieve the session for the given sender ID."""
        return await self.session_store.get_or_create_session(sender_id)

    async def run_action_extract_slots(
        self, output_channel: OutputChannel, session: Session
    ) -> Session:
        """Run the action to extract slots and update the session accordingly."""
        action = action_for_name_or_text("action_extract_slots", self.action_endpoint)
        extraction_events = await action.run(output_channel, self.nlg, session)
        session.update_with_events(extraction_events)
        return session

    async def _run_prediction_loop(
        self, output_channel: OutputChannel, session: Session
    ) -> None:
        """Run the action prediction loop until a listening action is predicted."""
        should_predict_another_action = True
        while should_predict_another_action:
            action, prediction = self.predict_next_action(session)
            should_predict_another_action = await self._run_action(action, session, output_channel, prediction)

    def predict_next_action(
        self, session: Session
    ) -> PolicyPrediction:
        """Predict the next action based on the session state."""
        prediction = PolicyPrediction.for_action_name("action_name", "policy_name", 0.99)
        action = action_for_name_or_text("action_name", self.action_endpoint)
        return action, prediction

    async def _run_action(
        self,
        action: "Action",
        session: Session,
        output_channel: OutputChannel,
        prediction: PolicyPrediction,
    ) -> bool:
        """Execute an action and update the session state."""
        try:
            events = await action.run(output_channel, self.nlg, session)
        except ActionExecutionRejected as e:
            logger.error(f"Action {action.name()} rejected: {e}")
            events = [ActionExecutionRejected(action.name())]
        
        session.update_with_events(events)
        await self.save_session(session)
        return action.name() != "action_listen"

    async def save_session(self, session: Session) -> None:
        """Persist the session state to the session store."""
        await self.session_store.save(session)

    async def _handle_message_with_session(self, message: UserMessage, session: Session) -> None:
        """Log the user message and update the session."""
        parse_data = await self.parse_message(message)
        session.update(UserUttered(message.text, parse_data.get("intent"), parse_data.get("entities")))
        logger.info(f"Updated session with new user message: {message.text}")

    async def parse_message(self, message: UserMessage) -> Dict[Text, Any]:
        """Parse the incoming user message to extract intent and entities."""
        if self.message_parser:
            return await self.message_parser.parse(message.text)
        else:
            # Mock message parsing process
            return {"intent": {"name": "greet", "confidence": 1.0}, "entities": []}
