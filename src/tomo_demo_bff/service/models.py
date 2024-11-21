from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel


class WebSocketMessage(BaseModel):
    """Model for WebSocket messages"""

    text: str
    timestamp: datetime = datetime.now()


class BotMessage(BaseModel):
    """Model for bot responses"""

    text: Optional[str] = None
    timestamp: datetime
    type: str = "bot"
    metadata: Optional[Dict[str, Any]] = None


class UserMessage(BaseModel):
    """Model for user messages"""

    text: str
    timestamp: datetime
    type: str = "user"
    metadata: Optional[Dict[str, Any]] = None


class ConversationMessage(BaseModel):
    """Model for conversation messages"""

    text: str
    timestamp: datetime
    type: str
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Response model for conversations endpoint"""

    session_id: str
    messages: List[ConversationMessage]


class SlotInfo(BaseModel):
    """Model for slot information"""

    name: str
    value: Optional[Any] = None
    description: Optional[str] = None
    extractable: bool


class SlotResponse(BaseModel):
    """Response model for slots endpoint"""

    session_id: str
    slots: List[SlotInfo]


class Event(BaseModel):
    """Model for session events"""

    type: str
    timestamp: datetime
    data: Dict[str, Any]


class EventResponse(BaseModel):
    """Response model for events endpoint"""

    session_id: str
    events: List[Event]
