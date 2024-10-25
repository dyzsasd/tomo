import abc
import logging
import typing

from tomo.shared.action_executor import ActionExector
from tomo.shared.event import Event
from tomo.shared.output_channel import OutputChannel
from tomo.shared.session import Session
from tomo.utils.json import JSONSerializableBase

logger = logging.getLogger(__name__)


class Action(abc.ABC, JSONSerializableBase):
    @classmethod
    def action_for_name_or_text(cls, name: str, executor: ActionExector):
        """ "Create an action instance which can run"""
        logger.debug(f"getting actions: {name}")
        logger.debug(f"getting actions: {executor}")
        return DummyAction()

    @property
    def name(self):
        pass

    @abc.abstractmethod
    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        pass


class DummyAction(Action):
    name = "dummy"

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        logger.info("Executing dummy action")
        return []
