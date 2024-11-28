import abc
import logging
from collections import deque
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Deque, Dict, List, Optional

from tomo.shared.slots import Slot

if TYPE_CHECKING:
    from tomo.shared.event import Event  # Forward declaration for Event


logger = logging.getLogger(__name__)


class Session(abc.ABC):
    """
    This class tracks the state of a conversation for a particular session.
    It stores information such as intents, entities, and user messages.
    """

    def __init__(
        self,
        session_id: str,
        max_event_history: Optional[int] = None,
        slots: Optional[Dict[str, Slot]] = None,
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
        self.slots: Dict[str, Slot] = slots or {}

        # Stores the most recent message sent by the user
        self.active = True

    def copy(self) -> "Session":
        return deepcopy(self)

    def _reset(self) -> None:
        """
        Reset session to initial state - doesn't delete events though!.

        Internal methods for the modification of the session state. Should
        only be called by events, not directly. Rather update the session
        with an event that in its ``apply_to`` method modifies the session.
        """
        self._reset_slots()
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

    @abc.abstractmethod
    def last_user_uttered_event(self) -> Optional["Event"]:
        pass

    @abc.abstractmethod
    def has_bot_replied(self) -> bool:
        pass
