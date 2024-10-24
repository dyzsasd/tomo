# src/chatbot_service/event_system/event.py

import abc
import time
import json
import typing

from .nlu import Entity
from .nlu import Intent

from .utils.json import JSONSerializableBase

if typing.TYPE_CHECKING:
    from .sessions import Session  # Forward declaration for Event


class Event(abc.ABC, JSONSerializableBase):
    """
    Base class for events that occur during a session.

    Events represent any significant occurrences in the conversation,
    such as a user message, bot response, or slot being set. Each event
    carries metadata and can be applied to the session to update its state.
    """

    timestamp: typing.Optional[float]
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
        pass

    def as_dict(self) -> typing.Dict[str, typing.Any]:
        """Convert the event to a dictionary format for serialization."""
        return self.to_json()

    def __eq__(self, other: typing.Any) -> bool:
        """Compare two events for equality based on their dictionary representation."""
        return isinstance(other, Event) and self.as_dict() == other.as_dict()

    def __hash__(self) -> int:
        """Generate a hash value for the event, used for storing events in sets or dicts."""
        return hash(json.dumps(self.as_dict()))


class SessionShutdown(Event):
    """
    Event indicating that the session has been shutdown.

    This event deactivates the session when applied.
    """

    def apply_to(self, session: "Session") -> None:
        """Deactivate the session."""
        session.deactivate()


class UserUttered(Event):
    """
    Event representing the user sending a message to the bot.

    This event captures the user's message, intent, and any detected entities.
    It updates the session to reflect the user's input.
    """

    message_id: str
    text: str
    input_channel: str  # TODO: create enum for input channel
    intent: typing.Optional[Intent] = None
    entities: typing.Optional[typing.List[Entity]] = None

    def apply_to(self, session: "Session") -> None:
        """
        Update the session's state based on the user message.

        Args:
            session: The session that will be updated with the user's message.
        """
        session.latest_message = self.text

    @property
    def intent_name(self) -> typing.Optional[typing.Text]:
        """
        Returns the intent name or `None` if no intent was detected.

        This property is used to access the name of the user's intent.
        """
        return self.intent or self.intent.name


class BotUttered(Event):
    """
    Event representing the bot sending a message to the user.

    This event captures the bot's response, which can be plain text or contain
    more complex data such as buttons, images, or custom JSON responses.

    Args:
        text: The plain text message sent by the bot.
        data: Additional data for more complex utterances (e.g., buttons, attachments).
        timestamp: When the event was created.
        metadata: Additional metadata related to the event.
    """

    text: typing.Optional[typing.Text] = None
    data: typing.Optional[typing.Dict] = None

    def apply_to(self, session: "Session") -> None:
        """
        Update the session's state based on the bot's message.

        Args:
            session: The session that will be updated with the bot's utterance.
        """
        session.latest_bot_utterance = self


class SlotSet(Event):
    """
    Event representing a slot being set by the user or bot.

    Slots store important information such as user preferences or extracted entities.
    This event updates the value of a specific slot in the session.

    Args:
        key: The name of the slot being set.
        value: The value to assign to the slot (can be `None` to clear the slot).
    """

    key: typing.Text
    value: typing.Optional[typing.Any] = None

    def apply_to(self, session: "Session") -> None:
        """
        Update the session by setting the specified slot value.

        Args:
            session: The session where the slot value will be updated.
        """
        session.set_slot(self.key, self.value)


class ActionExecuted(Event):
    """
    Event representing an action executed by the bot.

    This event captures the action name and any policies that triggered the action.

    Args:
        action_name: The name of the action that was executed.
        policy: The policy that predicted this action (optional).
    """

    action_name: str
    policy: typing.Optional[typing.Text] = None

    def apply_to(self, session: "Session") -> None:
        """
        Update the session to reflect the action taken by the bot.

        Args:
            session: The session where the action was executed.
        """
        session.latest_action = self.action_name


class ActionFailed(Event):
    action_name: str
    policy: typing.Optional[typing.Text] = None
    
    def apply_to(self, session: "Session") -> None:
        # TODO: thinking about how to handle the failed action
        pass


class SessionStarted(Event):
    """
    Event representing the start of a new session.

    This event resets the session to its initial state when applied.
    """

    def apply_to(self, session: "Session") -> None:
        """
        Reset the session at the start of a new session.

        Args:
            session: The session that will be reset.
        """
        session.reset()

class SessionDisabled(Event):
    """
    Event to disable a session.

    """

    def apply_to(self, session: "Session") -> None:
        """
        Reset the session at the start of a new session.

        Args:
            session: The session that will be reset.
        """
        session.active = False
