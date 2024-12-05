import abc
import json
import typing

from tomo.utils.json import JSONSerializableBase, JsonFormat

if typing.TYPE_CHECKING:
    from tomo.core.session import Session  # Forward declaration


class Event(abc.ABC, JSONSerializableBase):
    """
    Base class for events that occur during a session.

    Events represent any significant occurrences in the conversation,
    such as a user message, bot response, or slot being set. Each event
    carries metadata and can be applied to the session to update its state.
    """

    timestamp: float
    metadata: typing.Optional[typing.Dict[str, typing.Any]]

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

    def as_dict(self) -> typing.Dict[str, typing.Any]:
        """Convert the event to a dictionary format for serialization."""
        return JsonFormat.to_json(self)

    def __eq__(self, other: typing.Any) -> bool:
        """Compare two events for equality based on their dictionary representation."""
        return isinstance(other, Event) and self.as_dict() == other.as_dict()

    def __hash__(self) -> int:
        """Generate a hash value for the event, used for storing events in sets or dicts."""
        return hash(json.dumps(self.as_dict()))
