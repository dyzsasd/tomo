from typing import Text, Dict, Any, List, Optional
import json


class OutputChannel:
    """Base class for output channels, providing an interface for sending responses."""

    @classmethod
    def name(cls) -> Text:
        """Every output channel needs a name to identify it."""
        return cls.__name__

    async def send_response(self, recipient_id: Text, message: Dict[Text, Any]) -> None:
        """Send a message to the recipient based on the message type."""
        if message.get("quick_replies"):
            await self.send_quick_replies(
                recipient_id,
                message.pop("text"),
                message.pop("quick_replies"),
                **message,
            )
        elif message.get("buttons"):
            await self.send_text_with_buttons(
                recipient_id, message.pop("text"), message.pop("buttons"), **message
            )
        elif message.get("text"):
            await self.send_text_message(recipient_id, message.pop("text"), **message)

        if message.get("custom"):
            await self.send_custom_json(recipient_id, message.pop("custom"), **message)

        if message.get("image"):
            await self.send_image_url(recipient_id, message.pop("image"), **message)

        if message.get("attachment"):
            await self.send_attachment(recipient_id, message.pop("attachment"), **message)

        if message.get("elements"):
            await self.send_elements(recipient_id, message.pop("elements"), **message)

    async def send_text_message(self, recipient_id: Text, text: Text, **kwargs: Any) -> None:
        """Send a plain text message."""
        raise NotImplementedError(
            "Output channel needs to implement a send message for simple texts."
        )

    async def send_image_url(self, recipient_id: Text, image: Text, **kwargs: Any) -> None:
        """Send an image by URL."""
        await self.send_text_message(recipient_id, f"Image: {image}")

    async def send_attachment(self, recipient_id: Text, attachment: Text, **kwargs: Any) -> None:
        """Send an attachment."""
        await self.send_text_message(recipient_id, f"Attachment: {attachment}")

    async def send_text_with_buttons(
        self, recipient_id: Text, text: Text, buttons: List[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        """Send a message with buttons."""
        await self.send_text_message(recipient_id, text)
        for idx, button in enumerate(buttons):
            button_message = f"Button {idx + 1}: {button.get('title')}"
            await self.send_text_message(recipient_id, button_message)

    async def send_quick_replies(
        self, recipient_id: Text, text: Text, quick_replies: List[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        """Send quick replies."""
        await self.send_text_with_buttons(recipient_id, text, quick_replies)

    async def send_elements(self, recipient_id: Text, elements: List[Dict[Text, Any]], **kwargs: Any) -> None:
        """Send elements as part of a carousel or other structure."""
        for element in elements:
            element_message = f"{element.get('title', '')} : {element.get('subtitle', '')}"
            await self.send_text_with_buttons(
                recipient_id, element_message, element.get("buttons", [])
            )

    async def send_custom_json(self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any) -> None:
        """Send a custom JSON message."""
        await self.send_text_message(recipient_id, json.dumps(json_message))


class CollectingOutputChannel(OutputChannel):
    """An output channel that collects messages in a list."""

    def __init__(self) -> None:
        """Initialize the message collector."""
        self.messages: List[Dict[Text, Any]] = []

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
    ) -> Dict:
        """Create a message object to store."""
        return {
            "recipient_id": recipient_id,
            "text": text,
            "image": image,
            "buttons": buttons,
            "attachment": attachment,
            "custom": custom,
        }

    async def _persist_message(self, message: Dict[Text, Any]) -> None:
        """Save the message to the message list."""
        self.messages.append(message)

    async def send_text_message(self, recipient_id: Text, text: Text, **kwargs: Any) -> None:
        """Send a text message and persist it."""
        for message_part in text.strip().split("\n\n"):
            await self._persist_message(self._create_message(recipient_id, text=message_part))

    async def send_image_url(self, recipient_id: Text, image: Text, **kwargs: Any) -> None:
        """Send an image URL and persist it."""
        await self._persist_message(self._create_message(recipient_id, image=image))

    async def send_attachment(self, recipient_id: Text, attachment: Text, **kwargs: Any) -> None:
        """Send an attachment and persist it."""
        await self._persist_message(self._create_message(recipient_id, attachment=attachment))

    async def send_text_with_buttons(
        self, recipient_id: Text, text: Text, buttons: List[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        """Send a message with buttons and persist it."""
        await self._persist_message(self._create_message(recipient_id, text=text, buttons=buttons))

    async def send_custom_json(self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any) -> None:
        """Send a custom JSON message and persist it."""
        await self._persist_message(self._create_message(recipient_id, custom=json_message))
