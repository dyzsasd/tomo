from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of messages that can be sent through WebSocket"""

    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    ACTION = "action"
    CUSTOM = "custom"


class MessageContent(BaseModel):
    """Base content model for all message types"""

    content_type: MessageType = Field(description="Type of the message content")


class TextContent(MessageContent):
    """Content model for text messages"""

    content_type: MessageType = MessageType.TEXT
    value: str = Field(description="The text content of the message")


class ImageContent(MessageContent):
    """Content model for image messages"""

    content_type: MessageType = MessageType.IMAGE
    value: str = Field(description="Base64 encoded image data")
    format: str = Field(description="Image format (e.g., 'jpeg', 'png')")
    caption: Optional[str] = Field(None, description="Optional caption for the image")


class VoiceContent(MessageContent):
    """Content model for voice messages"""

    content_type: MessageType = MessageType.VOICE
    value: str = Field(description="Base64 encoded voice data")
    format: str = Field(description="Audio format (e.g., 'mp3', 'wav')")
    duration: Optional[float] = Field(
        None, description="Duration of the voice recording in seconds"
    )


class ActionContent(MessageContent):
    """Content model for action messages"""

    content_type: MessageType = MessageType.ACTION
    value: str = Field(description="Name of the action to perform")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Parameters for the action"
    )


class CustomContent(MessageContent):
    """Content model for custom messages"""

    content_type: MessageType = MessageType.CUSTOM
    value: Dict[str, Any] = Field(description="Custom message data")


class WebSocketMessage(BaseModel):
    """Main message model for WebSocket communication"""

    timestamp: datetime = Field(description="Timestamp of when the message was sent")
    session_id: str = Field(description="Session identifier")
    contents: List[
        Union[TextContent, ImageContent, VoiceContent, ActionContent, CustomContent]
    ] = Field(description="List of content items in the message")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the message"
    )
