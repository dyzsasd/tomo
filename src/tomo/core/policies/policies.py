import abc
import asyncio
from typing import Optional

from tomo.core.actions import ActionBotUtterQuickReply
from tomo.core.policies.models import PolicyPrediction
from tomo.shared.session import Session


class Policy(abc.ABC):
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
