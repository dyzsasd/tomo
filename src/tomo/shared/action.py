import abc
import logging
import typing

from tomo.shared.event import Event
from tomo.shared.output_channel import OutputChannel
from tomo.shared.session import Session
from tomo.utils.json import JSONSerializableBase

logger = logging.getLogger(__name__)


class Action(abc.ABC, JSONSerializableBase):
    subclasses = {}

    @classmethod
    def get_action_cls(cls, action_name):
        if action_name not in cls.subclasses:
            raise ValueError(f"Unknown action: {action_name}")
        return cls.subclasses[action_name]

    @classmethod
    def create(cls, action_name, **kwargs):
        return cls.get_action_cls(action_name)(**kwargs)

    def __init_subclass__(cls, **kwargs):
        """Automatically record each subclass."""
        super().__init_subclass__(**kwargs)
        action_name = cls.name
        if action_name in Action.subclasses:
            logger.fatal(f"action {action_name} exists already.")
        Action.subclasses[action_name] = cls  # Store subclass by name

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    @abc.abstractmethod
    def description(self):
        pass

    @classmethod
    def required_slots(cls):
        return []

    @abc.abstractmethod
    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        pass


class DummyAction(Action):
    name = "dummy"
    description = "dummy action for test purpose"

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        logger.info("Executing dummy action")
        return []
