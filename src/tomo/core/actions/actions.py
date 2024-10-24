import abc
import logging
import typing

from tomo.core.policies.policy import PolicyPrediction
from tomo.core.output_channels import OutputChannel
from tomo.core.nlg.generator import NaturalLanguageGenerator
from tomo.shared.events import Event
from tomo.shared.sessions import Session

from tomo.shared.utils.json import JSONSerializableBase

from .executor import ActionExector


logger = logging.getLogger(__name__)


# TODO: implement Action
class Action(abc.ABC, JSONSerializableBase):
    @classmethod
    def action_for_name_or_text(cls, name: typing.Text, executor: ActionExector):
        """"Create an action instance which can run"""
        return DummyAction()

    @property
    def name(self):
        pass

    @abc.abstractmethod
    async def run(self, output_channel: OutputChannel, nlg: NaturalLanguageGenerator, session: Session) -> typing.Optional[typing.List[Event]]:
        pass


class DummyAction(Action):
    name = "dummy"
    
    async def run(self, output_channel: OutputChannel, nlg: NaturalLanguageGenerator, session: Session) -> typing.Optional[typing.List[Event]]:
        logger.info("Executing dummy action")
        return []


class ActionListen(Action):
    name = "listen"
    async def run(self, output_channel: OutputChannel, nlg: NaturalLanguageGenerator, session: Session) -> typing.Optional[typing.List[Event]]:
        pass

    def event_for_successful_execution(self, policy: PolicyPrediction) -> typing.List[Event]:
        pass

class ActionExtractSlots(Action):
    name = "extract_slots"
    async def run(self, output_channel: OutputChannel, nlg: NaturalLanguageGenerator, session: Session) -> typing.Optional[typing.List[Event]]:
        pass

    def event_for_successful_execution(self, policy: PolicyPrediction) -> typing.List[Event]:
        pass

class ActionSessionStart(Action):
    name = "session_start"
    async def run(self, output_channel: OutputChannel, nlg: NaturalLanguageGenerator, session: Session) -> typing.Optional[typing.List[Event]]:
        pass

    def event_for_successful_execution(self, policy: PolicyPrediction) -> typing.List[Event]:
        pass

class ActionDisableSession(Action):
    "Turn off action"
