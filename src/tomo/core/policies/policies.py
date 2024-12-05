import abc
import asyncio
import logging
from typing import Optional

from tomo.core.actions import ActionBotUtterQuickReply
from tomo.core.session import Session

from .models import PolicyPrediction


logger = logging.getLogger(__name__)


class Policy(abc.ABC):
    subclasses = {}

    @classmethod
    def create(cls, policy_name, **kwargs):
        """Factory method to create an instance of a subclass by name."""
        if policy_name not in cls.subclasses:
            raise ValueError(f"Unknown policy: {policy_name}")
        return cls.subclasses[policy_name](**kwargs)

    def __init_subclass__(cls, **kwargs):
        """Automatically record each subclass."""
        super().__init_subclass__(**kwargs)
        if cls.__name__ in Policy.subclasses:
            logger.fatal(f"policy {cls.__name__} exists already.")
        Policy.subclasses[cls.__name__] = cls  # Store subclass by name

    @property
    def name(self):
        return __class__.__name__

    @abc.abstractmethod
    async def run(self, session: Session) -> Optional[PolicyPrediction]:
        pass


class QuickResponsePolicy(Policy):
    """A policy which can send a reply to user quickly.

    Other policy may take long time in execution, so this policy
    will return a immediate reply to the user, in order to ensure
    the user that the requirement has been received.

    Args:
        waiting_time: how long the bot should wait before sending the quick reply,
                      default is 500 ms
    """

    def __init__(self, message, waiting_time=500):
        self.message = message
        self.waiting_time = waiting_time

    async def run(self, session: Session) -> Optional[PolicyPrediction]:
        if session.has_bot_replied():
            return None

        await asyncio.sleep(self.waiting_time / 1000)
        action = ActionBotUtterQuickReply(message=self.message)
        return PolicyPrediction(policy_name=self.name, actions=[action])
