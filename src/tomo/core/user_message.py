import uuid
from typing import Optional, Text, Dict, Any

from tomo.shared.constants import DEFAULT_SESSION_ID
from tomo.shared.output_channel import OutputChannel

class UserMessage():
    """Represents an incoming message, including the channel for sending responses."""

    def __init__(
        self,
        text: Optional[Text] = None,
        output_channel: Optional[OutputChannel] = None,
        session_id: Optional[Text] = None,
        parse_data: Optional[Dict[Text, Any]] = None,
        input_channel: Optional[Text] = None,
        message_id: Optional[Text] = None,
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
        # Initialize message attributes
        self.text = text.strip() if text else text
        self.message_id = str(message_id) if message_id else uuid.uuid4().hex
        self.output_channel = output_channel
        self.session_id = str(session_id) if session_id else DEFAULT_SESSION_ID
        self.input_channel = input_channel
        self.parse_data = parse_data
        self.metadata = metadata
        self.headers = kwargs.get("headers", None)
