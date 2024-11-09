import typing

from tomo.shared.action import Action
from tomo.utils.json import JSONSerializableBase


class PolicyPrediction(JSONSerializableBase):
    policy_name: typing.Optional[str]
    actions: typing.List[Action]

    @property
    def action_names(self):
        return [action.name for action in self.actions]
