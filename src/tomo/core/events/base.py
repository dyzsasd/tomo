import abc
from datetime import datetime, timezone
import typing

from pydantic import BaseModel, Field

if typing.TYPE_CHECKING:
    from tomo.core.session import Session  # Forward declaration


class Event(BaseModel):
    """
    Base class for events that occur during a session.

    Events represent any significant occurrences in the conversation,
    such as a user message, bot response, or slot being set. Each event
    carries metadata and can be applied to the session to update its state.
    """

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = Field(description="event type")

    @abc.abstractmethod
    def apply_to(self, session: "Session") -> None:
        """
        Apply the event to the session.

        This method is responsible for modifying the session's state based
        on the event. Subclasses must implement this to define the specific
        behavior for each type of event.

        Args:
            session: The session to which the event will be applied.
        """

    @property
    def type(self):
        return self.__class__.__name__

    @property
    @abc.abstractmethod
    def name(self):
        pass
