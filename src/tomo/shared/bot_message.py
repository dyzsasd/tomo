from dataclasses import dataclass
import typing
import dataclasses

from tomo.utils.json import json_serializable


@dataclass
@json_serializable
class BotMessage():
    recipient_id: typing.Optional[typing.Text]
    text: typing.Optional[str] = None
    quick_replies: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None
    buttons: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None
    custom: typing.Optional[typing.Dict[str, typing.Any]] = None
    image: typing.Optional[str] = None
    attachment: typing.Optional[str] = None
    elements: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None
    additional_properties: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict)
