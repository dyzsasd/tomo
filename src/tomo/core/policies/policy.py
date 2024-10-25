import typing

from tomo.shared.action import Action


# TODO: implement PolicyPrediction
class PolicyPrediction:
    policy_name: typing.Optional[str]
    action_names: typing.List[str]

    @property
    def actions(self) -> typing.List[Action]:
        pass
