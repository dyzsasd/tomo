# pylint: disable=C0301

from typing import List, Optional

from pydantic import BaseModel, Field


class Entity(BaseModel):
    name: str = Field(
        description="The entity name, which should be one of the value in Entity list."
    )
    value: str = Field(description="The value of the entity.")
    replace: bool = Field(
        description="If the slot contains already the value, this field will give the instruction to replace the value or not"
    )


class IntentExtraction(BaseModel):
    name: str = Field(
        description="The intent name, which should be one of the value in the intent list."
    )


class NLUExtraction(BaseModel):
    intent: Optional[IntentExtraction] = Field(
        description="Intent detected from user's message with the conversation history, which could be omnit."
    )
    entities: List[Entity] = Field(
        description="Entities detected from the user's message with the conversation history, it could be an empty list."
    )
