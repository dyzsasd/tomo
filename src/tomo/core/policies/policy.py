import typing

if typing.TYPE_CHECKING:
    from tomo.core.actions.actions import Action  # Forward declaration for Action


# TODO: implement PolicyPrediction
class PolicyPrediction():
    action_names: typing.List[typing.Text]

    @property
    def actions(self) -> typing.List["Action"]:
        pass