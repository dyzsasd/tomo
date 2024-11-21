from typing import Optional
import logging

from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .core import TomoService
from .managers.websocket import WebSocketManager
from .endpoints.websocket import handle_websocket
from .endpoints.events import get_session_events
from .endpoints.conversations import get_conversations
from .endpoints.slots import get_slots
from .models import (
    ConversationResponse,
    SlotResponse,
    EventResponse,
)


logger = logging.getLogger(__name__)


def custom_openapi(app: FastAPI):
    """Generate custom OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Tomo BFF API",
        version="1.0.0",
        description="Backend for Frontend service for Tomo chatbot",
        routes=app.routes,
    )

    # Customize the schema here if needed
    openapi_schema["info"]["x-logo"] = {"url": "https://path-to-your-logo.png"}

    # Add authentication information if needed
    # openapi_schema["components"]["securitySchemes"] = {...}

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def create_app(config_path: str) -> FastAPI:
    """Create and configure the FastAPI application"""

    app = FastAPI(
        title="Tomo Demo BFF Service",
        description="Backend for Frontend service for Tomo Demo chatbot",
        version="1.0.0",
        docs_url="/api/v1/docs",
        openapi_url="/api/v1/openapi.json",
        redoc_url="/api/v1/redoc",
    )

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

    # Custom OpenAPI schema
    app.openapi = lambda: custom_openapi(app)

    # WebSocket endpoint with versioning
    @app.websocket("/api/v1/ws/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str):
        """
        WebSocket endpoint for real-time chat communication

        Parameters:
        - session_id: Unique identifier for the chat session
        """
        await handle_websocket(websocket, session_id, websocket_manager, tomo_service)

    # Development endpoints
    @app.get("/api/v1/dev/session/{session_id}/events", response_model=EventResponse)
    async def session_events_endpoint(
        session_id: str,
        after: Optional[float] = Query(
            None, description="Timestamp to filter events after"
        ),
    ):
        """
        Get events for a specific session

        Parameters:
        - session_id: Session identifier
        - after: Optional timestamp to filter events
        """
        return await get_session_events(session_id, after, tomo_service)

    # Public endpoints
    @app.get(
        "/api/v1/session/{session_id}/conversations",
        response_model=ConversationResponse,
    )
    async def conversations_endpoint(session_id: str):
        """
        Get conversation history for a session

        Parameters:
        - session_id: Session identifier
        """
        return await get_conversations(session_id, tomo_service)

    @app.get("/api/v1/session/{session_id}/slots", response_model=SlotResponse)
    async def slots_endpoint(session_id: str):
        """
        Get all slots for a session

        Parameters:
        - session_id: Session identifier
        """
        return await get_slots(session_id, tomo_service)

    # Endpoint to expose OpenAPI schema
    @app.get("/api/v1/openapi.json")
    async def get_openapi_schema():
        return app.openapi()

    return app


def run_app():
    """Run the FastAPI application"""
    import uvicorn  # pylint: disable=C0415
    from dotenv import load_dotenv  # pylint: disable=C0415

    load_dotenv()

    app = create_app("assistants/flight_agent.yaml")  # Update path as needed
    uvicorn.run(app, host="0.0.0.0", port=8000)