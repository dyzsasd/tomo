import typing

from langchain_core.pydantic_v1 import BaseModel, Field

from tomo.shared.action import Action
from tomo.utils.json import JSONSerializableBase, json_serializable


class PolicyPrediction(JSONSerializableBase):
    policy_name: typing.Optional[str]
    actions: typing.List[Action]

    @property
    def action_names(self):
        return [action.name for action in self.actions]


@json_serializable
class ExtractedAction(BaseModel):
    name: str = Field(description="The action name from the action list")
    arguments: typing.Optional[typing.Dict[str, typing.Any]] = Field(
        description=(
            "The arguments to execute the action, "
            "if no argument needed, then it should be empty."
        )
    )


@json_serializable
class ActionList(BaseModel):
    actions: typing.List[ExtractedAction] = Field(description="Actions returned by LLM")
