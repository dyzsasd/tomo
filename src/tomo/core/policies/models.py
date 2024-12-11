import typing
from dataclasses import dataclass
from pydantic import BaseModel, Field

from tomo.shared.action import Action


@dataclass
class PolicyPrediction:
    policy_name: typing.Optional[str]
    actions: typing.List[Action]

    @property
    def action_names(self):
        return [action.name for action in self.actions]


class ExtractedAction(BaseModel):
    name: str = Field(description="The action name from the action list")
    arguments: typing.Optional[typing.Dict[str, typing.Any]] = Field(
        description=(
            "The arguments to execute the action, "
            "if no argument needed, then it should be empty."
        )
    )


class ActionList(BaseModel):
    reason: str = Field(description="Reasoning for generating these actions")
    actions: typing.List[ExtractedAction] = Field(description="Actions returned by LLM")
