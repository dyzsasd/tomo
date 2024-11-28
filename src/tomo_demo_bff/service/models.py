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
    """
    Model for session events

    Parameters:
    - type: event type, which could be action, bot utter etc.
    - timestamp: timestamps of event
    - name: the name of the event
    - detail: html block to display the event informations
    - data: detailed full information about event
    - metadata: metadata of event
    """

    type: str
    timestamp: float
    name: str
    detail: str
    data: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]


class EventResponse(BaseModel):
    """Response model for events endpoint"""

    session_id: str
    events: List[Event]


class SessionSummary(BaseModel):
    """Model for session summary information"""

    session_id: str
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    message_count: int
    active: bool
    current_step: Optional[str] = None


class SessionListResponse(BaseModel):
    """Response model for sessions list endpoint"""

    total_sessions: int
    sessions: List[SessionSummary]
