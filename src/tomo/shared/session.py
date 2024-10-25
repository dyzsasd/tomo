import abc
import logging
from collections import deque
from copy import deepcopy
from typing import TYPE_CHECKING, Deque, Dict, List, Optional

from tomo.shared.constants import ACTION_LISTEN_NAME
from tomo.shared.exceptions import BadParameter
from tomo.shared.slots import Slot
from tomo.utils.json import JsonFormat

if TYPE_CHECKING:
    from tomo.shared.event import Event  # Forward declaration for Event


logger = logging.getLogger(__name__)


class Session(abc.ABC):
    """
    This class tracks the state of a conversation for a particular session.
    It stores information such as intents, entities, and user messages.
    """

    def __init__(
        self, session_id: str, max_event_history: Optional[int] = None
    ) -> None:
        """
        Initialize a new session with a unique session ID.

        Args:
            session_id: Unique identifier for the session (e.g., user ID or conversation ID).
            max_event_history: Maximum number of events to store in history.
        """
        self.session_id: str = session_id
        self.max_event_history: int = max_event_history
        self.events: Deque["Event"] = deque(maxlen=max_event_history)
        self.slots: Dict[str, Slot] = {}

        self.followup_action: Optional[str] = ACTION_LISTEN_NAME
        self.latest_action: Optional[Dict[str, str]] = None
        # Stores the most recent message sent by the user
        self.latest_message: Optional[str] = None
        self.latest_bot_utterance: Optional[str] = None
        self.active = True
        self._reset()

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "max_event_history": self.max_event_history,
            "events": [JsonFormat.to_json(event) for event in self.events],
            "slots": {
                key: JsonFormat.to_json(slot) for key, slot in self.slots.items()
            },
            "followup_action": self.followup_action,
            "latest_action": self.latest_action,
            "latest_message": self.latest_message,
            "latest_bot_utterance": self.latest_bot_utterance,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: dict):
        session_id = data.get("session_id")
        if session_id is None:
            raise BadParameter(
                "session id is missing, cannot read the session from dict"
            )
        session = Session(session_id)

        session.max_event_history = data.get("max_event_history")
        session.events = deque(maxlen=session.max_event_history)
        for event in data.get("events", []):
            session.events.append(JsonFormat.from_json(event))

        session.slots = {
            key: JsonFormat.from_json(slot)
            for key, slot in data.get("slots", {}).items()
        }
        session.followup_action = data.get("followup_action")
        session.latest_action = data.get("latest_action")
        session.latest_message = data.get("latest_message")
        session.latest_bot_utterance = data.get("latest_bot_utterance")
        session.active = data.get("active", True)

        return session

    def copy(self) -> "Session":
        deepcopy(self)

    def _reset(self) -> None:
        """
        Reset session to initial state - doesn't delete events though!.

        Internal methods for the modification of the session state. Should
        only be called by events, not directly. Rather update the session
        with an event that in its ``apply_to`` method modifies the session.
        """
        self._reset_slots()
        self.latest_action = {}
        self.latest_message = None
        self.latest_bot_utterance = None
        self.followup_action = ACTION_LISTEN_NAME
        self.active = True

    @abc.abstractmethod
    async def update_with_event(self, event: "Event") -> "Session":
        """
        Update session by event, and the session should be persisted after updating.

        Args:
            event: An instance of an Event, such as a user utterance or bot action.
        """

    @abc.abstractmethod
    async def update_with_events(
        self,
        new_events: List["Event"],
        override_timestamp: bool = True,
    ) -> "Session":
        """
        Update session by events, and the session should be persisted after updating.

        Args:
            new_events: Events to apply.
            override_timestamp: If `True` refresh all timestamps of the events. As the
                events are usually created at some earlier point, this makes sure that
                all new events come after any current session events.
        """

    def _reset_slots(self) -> None:
        """Set all the slots to their initial value."""
        for slot in self.slots.values():
            slot.reset()
