import abc
import logging
from enum import Enum
from typing import Optional

from tomo.shared.session import Session

logger = logging.getLogger(__name__)


class EventVerbosity(Enum):
    """Filter on which events to include in session dumps."""

    # no events will be included
    NONE = 1

    # include every logged event
    ALL = 2


class SessionManager(abc.ABC):
    @abc.abstractmethod
    async def get_or_create_session(
        self, session_id: str, max_event_history: Optional[int] = None
    ) -> Session:
        pass

    @abc.abstractmethod
    async def get_session(self, session_id: str) -> Optional[Session]:
        pass

    @abc.abstractmethod
    async def delete_session(self, session_id: str) -> None:
        pass

    @abc.abstractmethod
    async def save(self, session: str) -> Session:
        pass
