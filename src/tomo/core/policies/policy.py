import typing

from tomo.shared.utils.json_meta import JSONSerializableMeta

if typing.TYPE_CHECKING:
    from tomo.core.actions.actions import Action  # Forward declaration for Action


# TODO: implement PolicyPrediction
class PolicyPrediction(metaclass=JSONSerializableMeta):
    action_names: typing.List[typing.Text]

    @property
    def actions(self) -> typing.List[Action]:
        pass