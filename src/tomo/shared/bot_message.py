import typing

from pydantic import BaseModel, Field


class BotMessage(BaseModel):
    recipient_id: typing.Optional[str]
    text: typing.Optional[str] = None
    quick_replies: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None
    buttons: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None
    custom: typing.Optional[typing.Dict[str, typing.Any]] = None
    image: typing.Optional[str] = None
    attachment: typing.Optional[str] = None
    elements: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None
    additional_properties: typing.Dict[str, typing.Any] = Field(default_factory=dict)
