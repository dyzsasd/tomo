from typing import Dict, Optional, List, Any
import logging

from tomo.core.output_channels import CollectingOutputChannel
from tomo.core.policies import LocalPolicyManager
from tomo.core.processor import MessageProcessor
from tomo.core.sessions import FileSessionManager
from tomo.core.user_message import TextUserMessage
from tomo.shared.action_executor import ActionExector
from tomo.shared.session_manager import SessionManager
from tomo.config import AssistantConfigLoader
from tomo.assistant import Assistant

from .models import Event


logger = logging.getLogger(__name__)


def event_detail(event: Event) -> str:
    logger.debug(str(event))
    return "<div>detail placeholder</div>"


def event_data(event: Event) -> Dict[str, Any]:
    logger.debug(str(event))
    return {}


class TomoService:
    """Core service for handling Tomo chatbot operations"""

    def __init__(self, config_path: str):
        """
        Initialize the Tomo service with configuration

        Args:
            config_path: Path to the configuration file
        """
        # Load configuration and initialize components
        config_loader = AssistantConfigLoader(config_path)
        assistant_config = config_loader.load()
        self.assistant = Assistant(config=assistant_config)

        # Initialize core components
        self.session_manager: SessionManager = FileSessionManager(
            assistant=self.assistant
        )
        self.policy_manager = LocalPolicyManager(policies=self.assistant.policies)
        self.action_executor = ActionExector()
        self.nlu_parser = self.assistant.nlu_parser

        # Initialize message processor
        self.message_processor = MessageProcessor(
            session_manager=self.session_manager,
            policy_manager=self.policy_manager,
            action_exector=self.action_executor,
            nlu_parser=self.nlu_parser,
        )

        logger.info("Tomo service initialized successfully")

    async def handle_message(
        self, session_id: str, message_text: str
    ) -> List[Dict[str, Any]]:
        """
        Process a message and return bot responses

        Args:
            session_id: The session identifier
            message_text: The user's message text

        Returns:
            List of bot response messages
        """
        output_channel = CollectingOutputChannel()

        user_message = TextUserMessage(
            text=message_text,
            output_channel=output_channel,
            session_id=session_id,
            input_channel="websocket",
        )

        await self.message_processor.handle_message(user_message)
        return [msg.as_dict() for msg in output_channel.messages]

    async def get_session_events(
        self, session_id: str, after_timestamp: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Get events for a session, optionally filtered by timestamp

        Args:
            session_id: The session identifier
            after_timestamp: Optional timestamp to filter events

        Returns:
            List of session events
        """
        session = await self.session_manager.get_session(session_id)
        if not session:
            return []

        events = []
        for event in session.events:
            if after_timestamp is None or event.timestamp > after_timestamp:
                event = Event(
                    type=event.type,
                    timestamp=event.timestamp,
                    name=event.name,
                    detail=event_detail(event),
                    data=event_data(event),
                    metadata=event.metadata,
                )
                events.append(event)
        return events

    async def get_conversation_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation messages in a format suitable for chat interface

        Args:
            session_id: The session identifier

        Returns:
            List of conversation messages
        """
        session = await self.session_manager.get_session(session_id)
        if not session:
            return []

        messages = []
        for event in session.events:
            if hasattr(event, "text"):
                message = {
                    "text": event.text,
                    "timestamp": event.timestamp,
                    "type": "user" if hasattr(event, "input_channel") else "bot",
                }
                messages.append(message)
        return messages

    async def get_session_slots(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all slots and their values for a session

        Args:
            session_id: The session identifier

        Returns:
            List of slot information including name, value, and description
        """
        session = await self.session_manager.get_session(session_id)
        if not session:
            return []

        slots = []
        for slot_name, slot in session.slots.items():
            slots.append(
                {
                    "name": slot_name,
                    "value": slot.value,
                    "description": slot.description,
                    "extractable": slot.extractable,
                }
            )
        return slots
