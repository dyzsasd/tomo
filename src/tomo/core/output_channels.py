from typing import Text, Any, List, Dict, Optional

from tomo.shared.output_channel import OutputChannel
from tomo.shared.bot_message import BotMessage


class CollectingOutputChannel(OutputChannel):
    """An output channel that collects messages in a list."""

    def __init__(self) -> None:
        """Initialize the message collector."""
        self.messages: List[BotMessage] = []

    @classmethod
    def name(cls) -> Text:
        """Return the name of the channel."""
        return "collector"

    @staticmethod
    def _create_message(
        recipient_id: Text,
        text: Optional[Text] = None,
        image: Optional[Text] = None,
        buttons: Optional[List[Dict[Text, Any]]] = None,
        attachment: Optional[Text] = None,
        custom: Optional[Dict[Text, Any]] = None,
        quick_replies: Optional[List[Dict[Text, Any]]] = None,
        elements: Optional[List[Dict[Text, Any]]] = None,
        additional_properties: Optional[Dict[Text, Any]] = None,
    ) -> BotMessage:
        """Create a BotMessage object to store."""
        if additional_properties is None:
            additional_properties = {}
        return BotMessage(
            recipient_id=recipient_id,
            text=text,
            image=image,
            buttons=buttons,
            attachment=attachment,
            custom=custom,
            quick_replies=quick_replies,
            elements=elements,
            additional_properties=additional_properties
        )

    async def _persist_message(self, message: BotMessage) -> None:
        """Save the message to the message list."""
        self.messages.append(message)

    async def send_text_message(self, text: Text, recipient_id: Text = None, **kwargs: Any) -> None:
        """Send a text message and persist it."""
        for message_part in text.strip().split("\n\n"):
            message = self._create_message(
                recipient_id,
                text=message_part,
                additional_properties=kwargs
            )
            await self._persist_message(message)

    async def send_image_url(self, recipient_id: Text, image: Text, **kwargs: Any) -> None:
        """Send an image URL and persist it."""
        message = self._create_message(
            recipient_id,
            image=image,
            additional_properties=kwargs
        )
        await self._persist_message(message)

    async def send_attachment(self, recipient_id: Text, attachment: Text, **kwargs: Any) -> None:
        """Send an attachment and persist it."""
        message = self._create_message(
            recipient_id,
            attachment=attachment,
            additional_properties=kwargs
        )
        await self._persist_message(message)

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        **kwargs: Any
    ) -> None:
        """Send a message with buttons and persist it."""
        message = self._create_message(
            recipient_id,
            text=text,
            buttons=buttons,
            additional_properties=kwargs
        )
        await self._persist_message(message)

    async def send_quick_replies(
        self,
        recipient_id: Text,
        text: Text,
        quick_replies: List[Dict[Text, Any]],
        **kwargs: Any
    ) -> None:
        """Send quick replies and persist them."""
        message = self._create_message(
            recipient_id,
            text=text,
            quick_replies=quick_replies,
            additional_properties=kwargs
        )
        await self._persist_message(message)

    async def send_elements(
        self,
        recipient_id: Text,
        elements: List[Dict[Text, Any]],
        **kwargs: Any
    ) -> None:
        """Send elements as part of a carousel or other structure and persist them."""
        message = self._create_message(
            recipient_id,
            elements=elements,
            additional_properties=kwargs
        )
        await self._persist_message(message)

    async def send_custom_json(
        self,
        recipient_id: Text,
        json_message: Dict[Text, Any],
        **kwargs: Any
    ) -> None:
        """Send a custom JSON message and persist it."""
        message = self._create_message(
            recipient_id,
            custom=json_message,
            additional_properties=kwargs
        )
        await self._persist_message(message)
