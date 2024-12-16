from datetime import datetime, timezone
import logging
from copy import deepcopy
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from tomo.core.events import EventUnion, UserUttered, BotUttered
from tomo.core.models import SessionStatus
from tomo.shared.slots import Slot


logger = logging.getLogger(__name__)


class Session(BaseModel):
    """
    This class tracks the state of a conversation for a particular session.
    It stores information such as intents, entities, and user messages.
    """

    session_id: str
    slots: Dict[str, Slot]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: SessionStatus = Field(default=SessionStatus.ACTIVE)
    events: List["EventUnion"] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def active(self):
        return self.status in (
            SessionStatus.ACTIVE,
            self.status == SessionStatus.PENDING,
        )

    def get_conversation_events(self) -> List["Event"]:
        """Get all conversation message events"""
        return [
            event
            for event in self.events
            if event.type in ["user_uttered", "bot_uttered"]
        ]

    def copy(self) -> "Session":
        return deepcopy(self)

    def _reset_slots(self) -> None:
        """Set all the slots to their initial value."""
        for slot in self.slots.values():
            slot.reset()

    def set_slot(self, key: str, value: Any) -> None:
        slot: Slot = self.slots.get(key)
        if slot is None:
            logger.error("Slot setting failed, cannot find slot {key} from session.")
            return
        slot.set_value(value)

    def unset_slot(self, key: str) -> None:
        slot: Slot = self.slots.get(key)
        if slot is None:
            logger.error("Slot setting failed, cannot find slot {key} from session.")
            return
        slot.reset()

    def last_user_uttered_event(self) -> Optional["Event"]:
        """Get the most recent UserUttered event"""
        for event in reversed(self.events):
            if isinstance(event, UserUttered):
                return event
        return None

    def has_bot_replied(self) -> bool:
        """Check if the bot has replied since the last user message"""
        for event in reversed(self.events):
            if isinstance(event, BotUttered):
                return True
            if isinstance(event, UserUttered):
                return False
        return False

    def get_events_after(self, timestamp: datetime) -> List["Event"]:
        """
        Get all events after a specific timestamp

        Args:
            timestamp: The timestamp to filter events

        Returns:
            List of events after the timestamp
        """
        return [event for event in self.events if event.timestamp > timestamp]

    def get_conversation_messages(self) -> List[Dict]:
        """
        Get conversation messages in a format suitable for chat interfaces

        Returns:
            List of message dictionaries
        """
        messages = []
        for event in self.events:
            if isinstance(event, (UserUttered, BotUttered)):
                message = {
                    "text": event.text,
                    "timestamp": event.timestamp,
                    "type": "user" if isinstance(event, UserUttered) else "bot",
                }
                messages.append(message)
        return messages
