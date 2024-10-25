# pylint: disable=C0301

from typing import List, Optional

from langchain_core.pydantic_v1 import BaseModel, Field

from tomo.utils.json import json_serializable


@json_serializable
class Entity(BaseModel):
    name: str = Field(
        description="The entity name, which should be one of the value in Entity list."
    )
    value: str = Field(description="The value of the entity.")


@json_serializable
class Intent(BaseModel):
    name: str = Field(
        description="The intent name, which should be one of the value in the intent list."
    )
    description: str = Field(description="Description of the user's intent")


@json_serializable
class NLUExtraction(BaseModel):
    intent: Optional[Intent] = Field(
        description="Intent detected from user's message with the conversation history, which could be omnit."
    )
    entities: List[Entity] = Field(
        description="Entities detected from the user's message with the conversation history, it could be an empty list."
    )
