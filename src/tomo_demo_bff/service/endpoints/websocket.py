import logging

from fastapi import WebSocket, WebSocketDisconnect

from tomo.core.user_message import TextUserMessage

from ..channels.websocket import WebSocketOutputChannel
from ..managers.websocket import WebSocketManager
from ..core import TomoService


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
            message = await websocket.receive_text()
            logger.debug(f"processing message: {message}")

            # Get lock for this session
            async with websocket_manager.locks[session_id]:
                user_message = TextUserMessage(
                    text=message,
                    output_channel=output_channel,
                    session_id=session_id,
                    input_channel="websocket",
                )
                await tomo_service.message_processor.handle_message(user_message)
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}", exc_info=True)
        websocket_manager.disconnect(session_id)
        await websocket.close(code=1011, reason="Internal server error")
