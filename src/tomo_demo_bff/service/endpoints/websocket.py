import logging

from fastapi import WebSocket, WebSocketDisconnect

from tomo.core.user_message import TextUserMessage

from ..channels.websocket import WebSocketOutputChannel
from ..managers.websocket import WebSocketManager
from ..core import TomoService
from ..models import WebSocketMessage, MessageType


logger = logging.getLogger(__name__)


async def handle_websocket(
    websocket: WebSocket,
    session_id: str,
    websocket_manager: WebSocketManager,
    tomo_service: TomoService,
):
    """Handle WebSocket connection and messages for a session"""

    # Try to connect the WebSocket
    if not await websocket_manager.connect(session_id, websocket):
        await websocket.close(
            code=1008, reason="Session already has an active connection"
        )
        return

    try:
        output_channel = WebSocketOutputChannel(websocket, session_id)

        while True:
            raw_message = await websocket.receive_json()
            message = WebSocketMessage.model_validate(raw_message)

            logger.debug(f"processing message: {message}")

            text = "\n".join(
                [
                    content.value
                    for content in message.contents
                    if content.content_type == MessageType.TEXT
                ]
            )

            if len(text) == 0:
                raise ValueError("text content is empty")

            # Get lock for this session
            async with websocket_manager.locks[session_id]:
                user_message = TextUserMessage(
                    text=text,
                    session_id=session_id,
                    output_channel=output_channel,
                    input_channel="websocket",
                    timestamp=message.timestamp,
                )
                await tomo_service.message_processor.handle_message(user_message)
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}", exc_info=True)
        websocket_manager.disconnect(session_id)
        await websocket.close(code=1011, reason="Internal server error")
