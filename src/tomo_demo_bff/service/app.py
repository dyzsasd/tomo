from typing import Optional

from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware

from .core import TomoService
from .managers.websocket import WebSocketManager
from .endpoints.websocket import handle_websocket
from .endpoints.events import get_session_events
from .endpoints.conversations import get_conversations
from .endpoints.slots import get_slots


def create_app(config_path: str) -> FastAPI:
    """Create and configure the FastAPI application"""

    app = FastAPI()

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Modify this in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize services
    websocket_manager = WebSocketManager()
    tomo_service = TomoService(config_path)

    # WebSocket endpoint
    @app.websocket("/api/v1/ws/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str):
        await handle_websocket(websocket, session_id, websocket_manager, tomo_service)

    # Session events endpoint
    @app.get("/api/v1/dev/session/{session_id}/events")
    async def session_events_endpoint(
        session_id: str,
        after: Optional[float] = Query(
            None, description="Timestamp to filter events after"
        ),
    ):
        return await get_session_events(session_id, after, tomo_service)

    # Conversations endpoint
    @app.get("/api/v1/session/{session_id}/conversations")
    async def conversations_endpoint(session_id: str):
        return await get_conversations(session_id, tomo_service)

    # Slots endpoint
    @app.get("/api/v1/session/{session_id}/slots")
    async def slots_endpoint(session_id: str):
        return await get_slots(session_id, tomo_service)

    return app


def run_app():
    """Run the FastAPI application"""
    import uvicorn  # pylint: disable=C0415

    app = create_app("config.yaml")  # Update path as needed
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run_app()
