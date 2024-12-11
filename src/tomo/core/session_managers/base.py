import abc
from datetime import datetime, timezone
import logging
from enum import Enum
from typing import Optional, TYPE_CHECKING, List

from tomo.shared.exceptions import TomoFatalException

if TYPE_CHECKING:
    from tomo.core.events import Event  # Forward declaration
    from tomo.core.session import Session

logger = logging.getLogger(__name__)


class EventVerbosity(Enum):
    """Filter on which events to include in session dumps."""

    # no events will be included
    NONE = 1

    # include every logged event
    ALL = 2


class SessionManager(abc.ABC):
    async def update_with_event(self, session_id: str, event: "Event") -> "Session":
        session: "Session" = await self.get_session(session_id)
        if session is None:
            raise TomoFatalException(f"Cannot find the session {session_id}")

        event.apply_to(session)
        session.events.append(event)
        logger.debug(
            f"Event {event.__class__.__name__} has been applied to session {session_id}"
        )

        persisted_session = await self.save(session)
        return persisted_session

    async def update_with_events(
        self,
        session_id: str,
        new_events: List["Event"],
        override_timestamp: bool = True,
    ) -> "Session":
        session: "Session" = await self.get_session(session_id)
        if session is None:
            raise TomoFatalException(f"Cannot find the session {session_id}")

        for e in new_events:
            if override_timestamp:
                e.timestamp = datetime.now(timezone.utc)
            e.apply_to(session)
            session.events.append(e)

        persisted_session = await self.save(session)
        return persisted_session

    @abc.abstractmethod
    async def create_session(self, session_id: Optional[str] = None) -> "Session":
        pass

    @abc.abstractmethod
    async def get_session(self, session_id: str) -> Optional["Session"]:
        pass

    @abc.abstractmethod
    async def delete_session(self, session_id: str) -> None:
        pass

    @abc.abstractmethod
    async def save(self, session: str) -> "Session":
        pass

    @abc.abstractmethod
    async def list_sessions(self) -> list[str]:
        pass
