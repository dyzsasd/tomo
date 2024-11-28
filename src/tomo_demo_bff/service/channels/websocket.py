import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import WebSocket

from tomo.shared.output_channel import OutputChannel


logger = logging.getLogger(__name__)


class WebSocketOutputChannel(OutputChannel):
    """Output channel that sends messages directly through WebSocket"""

    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id

    @classmethod
    def name(cls) -> str:
        return "websocket"

    async def _send_message(self, message: Dict[str, Any]):
        """Send message through WebSocket with error handling"""
        try:
            await self.websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message via WebSocket: {e}")
            raise

    async def send_text_message(
        self, text: str, recipient_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        await self._send_message(
            {"type": "bot", "text": text, "timestamp": time.time(), "metadata": kwargs}
        )

    async def send_image_url(
        self, image: str, recipient_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        await self._send_message({"type": "image", "url": image, "metadata": kwargs})

    async def send_text_with_buttons(
        self,
        text: str,
        buttons: List[Dict[str, Any]],
        recipient_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        await self._send_message(
            {"type": "buttons", "text": text, "buttons": buttons, "metadata": kwargs}
        )

    async def send_custom_json(
        self,
        json_message: Dict[str, Any],
        recipient_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        await self._send_message(
            {"type": "custom", "content": json_message, "metadata": kwargs}
        )
