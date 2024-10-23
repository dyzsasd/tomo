import typing
import dataclasses

from tomo.shared.utils.json_meta import JSONSerializableMeta

class BotMessage(metaclass=JSONSerializableMeta):
    recipient_id: typing.Text
    text: typing.Optional[str] = None
    quick_replies: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None
    buttons: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None
    custom: typing.Optional[typing.Dict[str, typing.Any]] = None
    image: typing.Optional[str] = None
    attachment: typing.Optional[str] = None
    elements: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None
    additional_properties: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict)
