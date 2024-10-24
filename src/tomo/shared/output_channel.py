import abc
import json
from typing import Text, Any, List, Dict

from tomo.shared.bot_message import BotMessage


class OutputChannel(abc.ABC):
    """Base class for output channels, providing an interface for sending responses."""

    @classmethod
    def name(cls) -> Text:
        """Every output channel needs a name to identify it."""
        return cls.__name__

    async def send_response(self, recipient_id: Text, message: BotMessage) -> None:
        """Send a message to the recipient based on the message type."""
        if message.quick_replies:
            await self.send_quick_replies(
                recipient_id,
                message.text,
                message.quick_replies,
                **message.additional_properties,
            )
        if message.buttons:
            await self.send_text_with_buttons(
                recipient_id, message.text, message.buttons, **message.additional_properties
            )
        if message.text:
            await self.send_text_message(recipient_id, message.text, **message.additional_properties)

        if message.custom:
            await self.send_custom_json(recipient_id, message.custom, **message.additional_properties)

        if message.image:
            await self.send_image_url(recipient_id, message.image, **message.additional_properties)

        if message.attachment:
            await self.send_attachment(recipient_id, message.attachment, **message.additional_properties)

        if message.elements:
            await self.send_elements(recipient_id, message.elements, **message.additional_properties)

    @abc.abstractmethod
    async def send_text_message(self, recipient_id: Text, text: Text, **kwargs: Any) -> None:
        """Send a plain text message."""
        raise NotImplementedError(
            "Output channel needs to implement a send message for simple texts."
        )

    async def send_image_url(self, recipient_id: Text, image: Text, **kwargs: Any) -> None:
        """Send an image by URL."""
        await self.send_text_message(recipient_id, f"Image: {image}", **kwargs)

    async def send_attachment(self, recipient_id: Text, attachment: Text, **kwargs: Any) -> None:
        """Send an attachment."""
        await self.send_text_message(recipient_id, f"Attachment: {attachment}", **kwargs)

    async def send_text_with_buttons(
        self, recipient_id: Text, text: Text, buttons: List[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        """Send a message with buttons."""
        await self.send_text_message(recipient_id, text, **kwargs)
        for idx, button in enumerate(buttons):
            button_message = f"Button {idx + 1}: {button.get('title')}"
            await self.send_text_message(recipient_id, button_message, **kwargs)

    async def send_quick_replies(
        self, recipient_id: Text, text: Text, quick_replies: List[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        """Send quick replies."""
        await self.send_text_with_buttons(recipient_id, text, quick_replies, **kwargs)

    async def send_elements(
        self, recipient_id: Text, elements: List[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        """Send elements as part of a carousel or other structure."""
        for element in elements:
            element_message = f"{element.get('title', '')} : {element.get('subtitle', '')}"
            await self.send_text_with_buttons(
                recipient_id, element_message, element.get("buttons", []), **kwargs
            )

    async def send_custom_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Send a custom JSON message."""
        await self.send_text_message(recipient_id, json.dumps(json_message), **kwargs)
