
import abc
from collections import deque
from enum import Enum
import logging
import time
from typing import Any
from typing import Deque
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Text
from typing import Type
from typing import TYPE_CHECKING
from typing import Tuple
from typing import Union
from typing import cast

from .constants import ACTION_LISTEN_NAME
from .constants import ACTION_NAME
from .constants import ACTION_TEXT
from .constants import FOLLOWUP_ACTION
from .exceptions import BadParameter
from .events import ActionExecuted
from .events import BotUttered
from .events import UserUttered
from .slots import Slot
from .utils.json import JsonFormat

if TYPE_CHECKING:
    from .events import Event  # Forward declaration for Event
    from tomo.core.actions.actions import Action


logger = logging.getLogger(__name__)


class EventVerbosity(Enum):
    """Filter on which events to include in session dumps."""
    
    # no events will be included
    NONE = 1

    # include every logged event
    ALL = 2


class Session():
    """
    This class tracks the state of a conversation for a particular session.
    It stores information such as intents, entities, and user messages.
    """

    def __init__(self, session_id: str, max_event_history: Optional[int] = None) -> None:
        """
        Initialize a new session with a unique session ID.

        Args:
            session_id: Unique identifier for the session (e.g., user ID or conversation ID).
            max_event_history: Maximum number of events to store in history.
        """
        self.session_id = session_id
        self.max_event_history = max_event_history
        self.events: Deque["Event"] = deque(maxlen=max_event_history)
        self.slots: Dict[str, Slot] = {}

        self.followup_action: Optional[Text] = ACTION_LISTEN_NAME
        self.latest_action: Optional[Dict[Text, Text]] = None
        # Stores the most recent message sent by the user
        self.latest_message: Optional[Text] = None
        self.latest_bot_utterance: Optional[Text] = None
        self.active = True
        self._reset()

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "max_event_history": self.max_event_history,
            "events": [JsonFormat.to_json(event) for event in self.events],
            "slots": {key: JsonFormat.to_json(slot) for key, slot in self.slots.items()},
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
            raise BadParameter("session id is missing, cannot read the session from dict")
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
        # TODO: avoid using seriliazation and deserialization
        js_object = self.to_dict()
        _session = Session.from_dict(js_object)
        return _session

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
    
    def clear_followup_action(self) -> None:
        """Clears follow up action when it was executed."""
        self.followup_action = None

    def _events_for_verbosity(
        self, event_verbosity: EventVerbosity
    ) -> Optional[List["Event"]]:
        if event_verbosity == EventVerbosity.ALL:
            return list(self.events)
        
        return None

    def current_slot_values(self) -> Dict[Text, Any]:
        """Return the currently set values of the slots."""
        return {key: slot.value for key, slot in self.slots.items()}

    def get_latest_input_channel(self) -> Optional[Text]:
        """Get the name of the input_channel of the latest UserUttered event."""
        for e in reversed(self.events):
            if isinstance(e, UserUttered):
                return e.input_channel
        return None
    
    def latest_action_name(self) -> Optional[Text]:
        """Get the name of the previously executed action

        Returns: name of the previously executed action
        """
        if self.latest_action is None:
            return None

        return self.latest_action.get(ACTION_NAME) or self.latest_action.get(
            ACTION_TEXT
        )

    def current_state(
        self, event_verbosity: EventVerbosity = EventVerbosity.NONE
    ) -> Dict[Text, Any]:
        """Returns the current session state as an object."""
        events = self._events_for_verbosity(event_verbosity)
        events_as_dict = [e.as_dict() for e in events] if events is not None else None
        latest_event_time = None
        if len(self.events) > 0:
            latest_event_time = self.events[-1].timestamp

        return {
            "session_id": self.session_id,
            "slots": self.current_slot_values(),
            "latest_message": self.latest_message,
            "latest_event_time": latest_event_time,
            FOLLOWUP_ACTION: self.followup_action,
            "events": events_as_dict,
            "latest_input_channel": self.get_latest_input_channel(),
            "latest_action": self.latest_action,
            "latest_action_name": self.latest_action_name,
        }

    def current_slot_values(self) -> Dict[Text, Any]:
        """Return the currently set values of the slots."""
        return {key: slot.value for key, slot in self.slots.items()}
        
    def has_bot_message_after_latest_user_message(self) -> bool:
        """Checks if there is a bot message after the most recent user message.

        Returns:
            `True` if there is an action after the most recent user message.
        """
        for event in self.events:
            if isinstance(event, BotUttered):
                return True
            elif isinstance(event, UserUttered):
                return False
        return False
    
    def has_action_after_latest_user_message(self) -> bool:
        """Check if there is an action after the most recent user message.

        Returns:
            `True` if there is an action after the most recent user message.
        """
        for event in reversed(self.events):
            if isinstance(event, ActionExecuted):
                return True
            elif isinstance(event, UserUttered):
                return False
        return False

    def get_latest_entity_values(self) -> Iterator[Text]:
        """Get entity values found for the passed entity type and optional role and
        group in latest message.

        If you are only interested in the first entity of a given type use
        `next(tracker.get_latest_entity_values(`"`my_entity_name`"`), None)`.
        If no entity is found `None` is the default result.

        Args:
            entity_type: the entity type of interest
            entity_role: optional entity role of interest
            entity_group: optional entity group of interest

        Returns:
            Entity values.
        """
        if self.latest_message is None:
            return iter([])

        return (
            cast(Text, x)
            for x in self.latest_message.entities
        )
    
    def get_latest_input_channel(self) -> Optional[Text]:
        """Get the name of the input_channel of the latest UserUttered event."""
        for e in reversed(self.events):
            if isinstance(e, UserUttered):
                return e.input_channel
        return None

    def replay_events(self) -> None:
        """Update the session based on a list of events."""
        for event in self.events:
            event.apply_to(self)

    def update_with_event(self, event: "Event") -> None:
        """
        Add a new event to the session's event history and update the session state.

        Args:
            event: An instance of an Event, such as a user utterance or bot action.
        """
        self.events.append(event)
        event.apply_to(self)

    def update_with_events(
        self,
        new_events: List["Event"],
        override_timestamp: bool = True,
    ) -> None:
        """Adds multiple events to the session.

        Args:
            new_events: Events to apply.
            override_timestamp: If `True` refresh all timestamps of the events. As the
                events are usually created at some earlier point, this makes sure that
                all new events come after any current session events.
        """
        for e in new_events:
            if override_timestamp:
                e.timestamp = time.time()
            self.update_with_event(e)

    def _reset_slots(self) -> None:
        """Set all the slots to their initial value."""
        for slot in self.slots.values():
            slot.reset()

    def get_slot(self, key: Text) -> Optional[Any]:
        """Retrieves the value of a slot."""
        if key in self.slots:
            return self.slots[key].value
        else:
            logger.info(f"Tried to access non existent slot '{key}'")
            return None

    def set_slot(self, key: str, value: Slot) -> None:
        """
        Set a value for a slot in the session.

        Args:
            key: The name of the slot.
            value: The value to set in the slot.
        """
        self.slots[key].set_value(value)

    def is_active(self) -> bool:
        """Check if the session is active."""
        return self.active

    def deactivate(self) -> None:
        """Deactivate the session (e.g., after a conversation ends)."""
        self.active = False

    def get_event_history(self) -> List[Dict[str, Any]]:
        """Return a list of all the events in the session."""
        return [event.as_dict() for event in self.events]

    def get_last_event_for(
        self,
        event_type: Union[Type["EventTypeAlias"], Tuple[Type["EventTypeAlias"], ...]],
        action_names_to_exclude: Optional[List[Text]] = None,
        skip: int = 0,
        event_verbosity: EventVerbosity = EventVerbosity.ALL,
    ) -> Optional["EventTypeAlias"]:
        """Gets the last event of a given type which was actually applied.

        Args:
            event_type: The type of event you want to find.
            action_names_to_exclude: Events of type `ActionExecuted` which
                should be excluded from the results. Can be used to skip
                `action_listen` events.
            skip: Skips n possible results before return an event.
            event_verbosity: Which `EventVerbosity` should be used to search for events.

        Returns:
            event which matched the query or `None` if no event matched.
        """
        to_exclude = action_names_to_exclude or []

        def filter_function(e: "Event") -> bool:
            has_instance = isinstance(e, event_type)
            excluded = isinstance(e, ActionExecuted) and e.action_name in to_exclude
            return has_instance and not excluded

        filtered = filter(
            filter_function, reversed(self._events_for_verbosity(event_verbosity) or [])
        )

        for i in range(skip):
            next(filtered, None)

        return next(filtered, None)


class SessionManager(abc.ABC):
    @abc.abstractmethod
    async def get_or_create_session(self, session_id: str, max_event_history: Optional[int] = None) -> Session:
        pass

    @abc.abstractmethod
    async def get_session(self, session_id: str) -> Optional[Session]:
        pass

    @abc.abstractmethod
    async def delete_session(self, session_id: str) -> None:
        pass

    @abc.abstractmethod
    async def save(self, session: str) -> None:
        pass


class InMemorySessionManager:
    """
    A simple in-memory session manager that stores session objects in memory.
    """

    def __init__(self) -> None:
        """Initialize an empty dictionary to store active sessions."""
        self.sessions: Dict[str, Session] = {}

    async def get_or_create_session(self, session_id: str, max_event_history: Optional[int] = None) -> Session:
        """
        Retrieve an existing session or create a new one if it doesn't exist.

        Args:
            session_id: The unique identifier for the session (e.g., user ID or conversation ID).
            max_event_history: Maximum number of events to store in the session.

        Returns:
            The session object.
        """
        if session_id not in self.sessions:
            session = Session(session_id, max_event_history)
            self.sessions[session_id] = session
        return self.sessions[session_id]

    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve a session by its session ID.

        Args:
            session_id: The unique identifier for the session.

        Returns:
            The session object or None if no session is found.
        """
        return self.sessions.get(session_id)

    async def delete_session(self, session_id: str) -> None:
        """
        Remove a session from the session manager.

        Args:
            session_id: The session ID to delete.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    async def save(self, session: Session) -> None:
        self.sessions[session.session_id] = session
