from copy import deepcopy
import logging
from typing import Dict, Optional

from tomo.assistant import Assistant
from tomo.core.session import Session

from .base import SessionManager


logger = logging.getLogger(__name__)


class InMemorySessionManager(SessionManager):
    """
    A simple in-memory session manager that stores session objects in memory.
    """

    def __init__(self, assistant: Assistant) -> None:
        """Initialize an empty dictionary to store active sessions."""
        self.assistant = assistant
        self.sessions: Dict[str, Session] = {}

    async def list_sessions(self) -> list[str]:
        return list(self.sessions.keys())

    async def get_or_create_session(self, session_id: str) -> Session:
        """
        Retrieve an existing session or create a new one if it doesn't exist.

        Args:
            session_id: The unique identifier for the session (e.g., user ID or conversation ID).

        Returns:
            The session object.
        """
        if session_id not in self.sessions:
            slots = {slot.name: deepcopy(slot) for slot in self.assistant.slots}
            session = Session(session_id, slots=slots)
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
