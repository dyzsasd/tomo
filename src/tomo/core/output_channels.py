from typing import Any, Dict, List, Optional

from tomo.shared.bot_message import BotMessage
from tomo.shared.output_channel import OutputChannel


class CollectingOutputChannel(OutputChannel):
    """An output channel that collects messages in a list."""

    def __init__(self) -> None:
        """Initialize the message collector."""
        self.messages: List[BotMessage] = []

    @classmethod
    def name(cls) -> str:
        """Return the name of the channel."""
        return "collector"

    @staticmethod
    def _create_message(
        recipient_id: str,
        text: Optional[str] = None,
        image: Optional[str] = None,
        buttons: Optional[List[Dict[str, Any]]] = None,
        attachment: Optional[str] = None,
        custom: Optional[Dict[str, Any]] = None,
        quick_replies: Optional[List[Dict[str, Any]]] = None,
        elements: Optional[List[Dict[str, Any]]] = None,
        additional_properties: Optional[Dict[str, Any]] = None,
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
            additional_properties=additional_properties,
        )

    async def _persist_message(self, message: BotMessage) -> None:
        """Save the message to the message list."""
        self.messages.append(message)

    async def send_text_message(
        self, text: str, recipient_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Send a text message and persist it."""
        for message_part in text.strip().split("\n\n"):
            message = self._create_message(
                recipient_id, text=message_part, additional_properties=kwargs
            )
            await self._persist_message(message)

    async def send_image_url(
        self, image: str, recipient_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Send an image URL and persist it."""
        message = self._create_message(
            recipient_id, image=image, additional_properties=kwargs
        )
        await self._persist_message(message)

    async def send_attachment(
        self, attachment: str, recipient_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Send an attachment and persist it."""
        message = self._create_message(
            recipient_id, attachment=attachment, additional_properties=kwargs
        )
        await self._persist_message(message)

    async def send_text_with_buttons(
        self,
        text: str,
        buttons: List[Dict[str, Any]],
        recipient_id: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Send a message with buttons and persist it."""
        message = self._create_message(
            recipient_id, text=text, buttons=buttons, additional_properties=kwargs
        )
        await self._persist_message(message)

    async def send_quick_replies(
        self,
        text: str,
        quick_replies: List[Dict[str, Any]],
        recipient_id: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Send quick replies and persist them."""
        message = self._create_message(
            recipient_id,
            text=text,
            quick_replies=quick_replies,
            additional_properties=kwargs,
        )
        await self._persist_message(message)

    async def send_elements(
        self,
        elements: List[Dict[str, Any]],
        recipient_id: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Send elements as part of a carousel or other structure and persist them."""
        message = self._create_message(
            recipient_id, elements=elements, additional_properties=kwargs
        )
        await self._persist_message(message)

    async def send_custom_json(
        self,
        json_message: Dict[str, Any],
        recipient_id: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Send a custom JSON message and persist it."""
        message = self._create_message(
            recipient_id, custom=json_message, additional_properties=kwargs
        )
        await self._persist_message(message)
