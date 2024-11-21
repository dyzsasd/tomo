import logging

from fastapi import WebSocket, WebSocketDisconnect

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
        while True:
            # Wait for messages
            message = await websocket.receive_text()

            # Get lock for this session
            async with websocket_manager.locks[session_id]:
                # Process message
                responses = await tomo_service.handle_message(session_id, message)

                # Send responses
                for response in responses:
                    await websocket_manager.send_message(session_id, response)

    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}", exc_info=True)
        websocket_manager.disconnect(session_id)
        await websocket.close(code=1011, reason="Internal server error")
