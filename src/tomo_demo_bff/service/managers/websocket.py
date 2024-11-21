import asyncio
import logging
from typing import Dict, Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for each session"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> bool:
        """
        Connect a new WebSocket for a session_id

        Args:
            session_id: The unique session identifier
            websocket: The WebSocket connection

        Returns:
            bool: True if connection was successful, False if session already has a connection
        """
        if session_id in self.active_connections:
            return False

        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.locks[session_id] = asyncio.Lock()
        logger.info(f"New WebSocket connection established for session {session_id}")
        return True

    def disconnect(self, session_id: str):
        """
        Disconnect and cleanup a WebSocket

        Args:
            session_id: The session to disconnect
        """
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.locks:
            del self.locks[session_id]
        logger.info(f"WebSocket connection closed for session {session_id}")

    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """
        Send a message to a specific session's WebSocket

        Args:
            session_id: The target session
            message: The message to send
        """
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)
            logger.debug(f"Message sent to session {session_id}")
