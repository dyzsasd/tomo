import typing

from tomo.shared.action import Action


# TODO: implement PolicyPrediction
class PolicyPrediction():
    action_names: typing.List[typing.Text]

    @property
    def actions(self) -> typing.List[Action]:
        pass
