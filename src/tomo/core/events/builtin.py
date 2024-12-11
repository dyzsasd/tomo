from dataclasses import field
import logging
import typing

from tomo.nlu.models import Entity, IntentExtraction
from tomo.core.events.base import Event
from tomo.core.models import SessionStatus

if typing.TYPE_CHECKING:
    from tomo.core.session import Session


logger = logging.getLogger(__name__)


class SessionShutdown(Event):
    """
    Event indicating that the session has been shutdown.

    This event deactivates the session when applied.
    """

    name: typing.ClassVar[str] = "shut down conversation"

    def apply_to(self, session: "Session") -> None:
        """Deactivate the session."""
        session.deactivate()


class UserUttered(Event):
    """
    Event representing the user sending a message to the bot.

    This event captures the user's message, intent, and any detected entities.
    It updates the session to reflect the user's input.
    """

    name: typing.ClassVar[str] = "user talked"

    message_id: str = field(default="")
    text: str = field(default="")
    input_channel: str = field(default="")
    intent: typing.Optional[IntentExtraction] = None
    entities: typing.Optional[typing.List[Entity]] = None

    def apply_to(self, session: "Session") -> None:
        """
        Update the session's state based on the user message.

        Args:
            session: The session that will be updated with the user's message.
        """
        session.latest_message = self.text

    @property
    def intent_name(self) -> typing.Optional[str]:
        """
        Returns the intent name or `None` if no intent was detected.

        This property is used to access the name of the user's intent.
        """
        return self.intent and self.intent.name


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

    name: typing.ClassVar[str] = "Bot talked"

    text: typing.Optional[str] = None
    data: typing.Optional[typing.Dict] = None

    def apply_to(self, session: "Session") -> None:
        """
        Update the session's state based on the bot's message.

        Args:
            session: The session that will be updated with the bot's utterance.
        """
        return


class SlotSet(Event):
    """
    Event representing a slot being set by the user or bot.

    Slots store important information such as user preferences or extracted entities.
    This event updates the value of a specific slot in the session.

    Args:
        key: The name of the slot being set.
        value: The value to assign to the slot (can be `None` to clear the slot).
    """

    key: str = ""
    value: typing.Optional[typing.Any] = None

    def apply_to(self, session: "Session") -> None:
        """
        Update the session by setting the specified slot value.

        Args:
            session: The session where the slot value will be updated.
        """
        session.set_slot(self.key, self.value)

    @property
    def name(self):
        return f"Set slot {self.key} value"


class SlotUnset(Event):
    """
    Event representing a slot being unset by the user or bot.

    Slots store important information such as user preferences or extracted entities.
    This event updates the value of a specific slot in the session.

    Args:
        key: The name of the slot being set.
    """

    key: str = ""

    def apply_to(self, session: "Session") -> None:
        """
        Update the session by setting the specified slot value.

        Args:
            session: The session where the slot value will be updated.
        """
        session.unset_slot(self.key)

    @property
    def name(self):
        return f"Unset slot {self.key} value"


class ActionExecuted(Event):
    """
    Event representing an action executed by the bot.

    This event captures the action name and any policies that triggered the action.

    Args:
        action_name: The name of the action that was executed.
        policy: The policy that predicted this action (optional).
    """

    action_name: str = ""
    policy: typing.Optional[str] = None

    def apply_to(self, session: "Session") -> None:
        """
        Update the session to reflect the action taken by the bot.

        Args:
            session: The session where the action was executed.
        """
        session.latest_action = self.action_name

    @property
    def name(self):
        return f"Action {self.action_name} executed"


class ActionFailed(Event):
    action_name: str = ""
    policy: typing.Optional[str] = None

    def apply_to(self, session: "Session") -> None:
        # TODO: thinking about how to handle the failed action
        pass

    @property
    def name(self):
        return f"Action {self.action_name} failed"


class SessionStarted(Event):
    """
    Event representing the start of a new session.

    This event resets the session to its initial state when applied.
    """

    name: typing.ClassVar[str] = "session started"

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

    name: typing.ClassVar[str] = "session disabled"

    def apply_to(self, session: "Session") -> None:
        """
        Reset the session at the start of a new session.

        Args:
            session: The session that will be reset.
        """
        session.status = SessionStatus.ARCHIVED
