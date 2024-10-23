import abc
import typing

from tomo.core.policies.policy import PolicyPrediction
from tomo.core.output_channels import OutputChannel
from tomo.core.nlg.generator import NaturalLanguageGenerator
from tomo.shared.events import Event
from tomo.shared.sessions import Session

from .executor import ActionExector


# TODO: implement Action
class Action(abc.ABC):
    @classmethod
    def action_for_name_or_text(cls, name: typing.Text, executor: ActionExector):
        """"Create an action instance which can run"""
        pass

    @property
    def name(self):
        pass

    @abc.abstractmethod
    def run(self, output_channel: OutputChannel, nlg: NaturalLanguageGenerator, session: Session) -> typing.Optional[typing.List[Event]]:
        pass

    @abc.abstractmethod
    def run(self, output_channel: OutputChannel, nlg: NaturalLanguageGenerator, session: Session) -> typing.list[Event]:
        pass

class ActionListen(Action):
    name = "listen"
    def run(self, output_channel: OutputChannel, nlg: NaturalLanguageGenerator, session: Session) -> typing.Optional[typing.List[Event]]:
        pass

    def event_for_successful_execution(self, policy: PolicyPrediction) -> typing.list[Event]:
        pass

class ActionExtractSlots(Action):
    name = "extract_slots"
    def run(self, output_channel: OutputChannel, nlg: NaturalLanguageGenerator, session: Session) -> typing.Optional[typing.List[Event]]:
        pass

    def event_for_successful_execution(self, policy: PolicyPrediction) -> typing.list[Event]:
        pass

class ActionSessionStart(Action):
    name = "session_start"
    def run(self, output_channel: OutputChannel, nlg: NaturalLanguageGenerator, session: Session) -> typing.Optional[typing.List[Event]]:
        pass

    def event_for_successful_execution(self, policy: PolicyPrediction) -> typing.list[Event]:
        pass

class ActionDisableSession(Action):
    "Turn off action"
