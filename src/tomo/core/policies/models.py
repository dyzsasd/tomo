import typing

from pydantic import BaseModel, Field

from tomo.shared.action import Action


class PolicyPrediction(BaseModel):
    policy_name: typing.Optional[str] = Field(None)
    actions: typing.List[Action] = Field(default_factory=list)

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
