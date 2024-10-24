from pydantic import BaseModel

from tomo.utils.json import json_serializable


@json_serializable
class Entity(BaseModel):
    name: str
    value: str


@json_serializable
class Intent(BaseModel):
    name: str
    description: str
