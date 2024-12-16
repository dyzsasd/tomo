import abc
import logging
import typing

from pydantic import BaseModel

from tomo.core.events.base import Event
from tomo.shared.output_channel import OutputChannel
from tomo.core.session import Session

logger = logging.getLogger(__name__)


class Action(BaseModel):
    subclasses: typing.ClassVar[dict[str, typing.Any]] = {}

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
    name: typing.ClassVar[str] = "dummy"
    description: typing.ClassVar[str] = "dummy action for test purpose"

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        logger.info("Executing dummy action")
        return []
