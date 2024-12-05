import abc
import uuid
from typing import Any, Dict, Optional

from tomo.shared.output_channel import OutputChannel


class UserMessage(abc.ABC):
    """Represents an incoming message, including the channel for sending responses."""

    parse_data: Optional[dict] = None

    @property
    @abc.abstractmethod
    def text(self) -> str:
        pass

    def __init__(self, session_id: str, output_channel: Optional[OutputChannel]):
        self.session_id = session_id
        self.output_channel = output_channel


class TextUserMessage(UserMessage):
    """Represents an incoming message, including the channel for sending responses."""

    @property
    def text(self) -> str:
        return self._text

    def __init__(
        self,
        session_id: Optional[str] = None,
        output_channel: OutputChannel = None,
        text: Optional[str] = None,
        parse_data: Optional[Dict[str, Any]] = None,
        input_channel: Optional[str] = None,
        message_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        """Creates a ``UserMessage`` object.

        Args:
            text: the message text content.
            output_channel: the output channel to use for bot responses.
            session_id: the ID of the conversation session.
            parse_data: rasa data about the message.
            input_channel: the name of the channel that received the message.
            message_id: ID of the message (auto-generated if not provided).
            metadata: additional metadata for this message.
        """
        super().__init__(session_id, output_channel)
        # Initialize message attributes
        self._text = text.strip() if text else text
        self.message_id = str(message_id) if message_id else uuid.uuid4().hex
        self.input_channel = input_channel
        self.parse_data = parse_data
        self.metadata = metadata
        self.headers = kwargs.get("headers", None)
