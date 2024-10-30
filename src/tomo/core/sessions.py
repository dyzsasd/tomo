import logging
import time
from typing import Dict, List, Optional

from tomo.core.events import UserUttered
from tomo.shared.event import Event
from tomo.shared.exceptions import TomoFatalException
from tomo.shared.session import Session
from tomo.shared.session_manager import SessionManager


logger = logging.getLogger(__name__)


class InMemorySession(Session):
    def __init__(
        self,
        session_manager: SessionManager,
        session_id: str,
        max_event_history: Optional[int] = None,
    ) -> None:
        super().__init__(session_id=session_id, max_event_history=max_event_history)
        self.session_manager: SessionManager = session_manager

    async def update_with_event(self, event: Event, immediate_persist=True) -> None:
        """
        Add a new event to the session's event history and update the session state.

        Args:
            event: An instance of an Event, such as a user utterance or bot action.
        """
        if getattr(self, "session_manager") is None:
            raise TomoFatalException(
                "session_manager isn't defined in this instance, event cannot be applied."
            )

        event.apply_to(self)
        self.events.append(event)
        logger.debug(f"Event {event.__class__} has been applied.")
        if immediate_persist:
            persisted_sesson = await self.session_manager.save(self)
            return persisted_sesson
        return self

    async def update_with_events(
        self,
        new_events: List[Event],
        override_timestamp: bool = True,
    ) -> Session:
        # TODO: add lock mecanism in update event and update events for saving session object.
        if getattr(self, "session_manager") is None:
            raise TomoFatalException(
                "session_manager isn't defined in this instance, event cannot be applied."
            )

        for e in new_events:
            if override_timestamp:
                e.timestamp = time.time()
            await self.update_with_event(e, immediate_persist=False)

        persisted_sesson = await self.session_manager.save(self)
        return persisted_sesson

    def last_user_uttered_event(self) -> Optional["Event"]:
        for event in reversed(self.events):
            if isinstance(event, UserUttered):
                return event
        return None


class InMemorySessionManager:
    """
    A simple in-memory session manager that stores session objects in memory.
    """

    def __init__(self) -> None:
        """Initialize an empty dictionary to store active sessions."""
        self.sessions: Dict[str, Session] = {}

    async def get_or_create_session(
        self, session_id: str, max_event_history: Optional[int] = None
    ) -> Session:
        """
        Retrieve an existing session or create a new one if it doesn't exist.

        Args:
            session_id: The unique identifier for the session (e.g., user ID or conversation ID).
            max_event_history: Maximum number of events to store in the session.

        Returns:
            The session object.
        """
        if session_id not in self.sessions:
            session = InMemorySession(self, session_id, max_event_history)
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

    async def save(self, session: Session) -> Session:
        self.sessions[session.session_id] = session
        return session
