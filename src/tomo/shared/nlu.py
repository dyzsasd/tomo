from pydantic import BaseModel, Field
from typing import List, Optional

from .utils.json_meta import JSONSerializableMeta


class Entity(BaseModel, metadata=JSONSerializableMeta):
    name: str
    value: str

class Intent(BaseModel):
    name: str
    description: str
