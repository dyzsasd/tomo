import abc
import logging
import typing

from tomo.shared.session import Session

from .policies import PolicyPrediction
from .policies import Policy


logger = logging.getLogger(__name__)


class PolicyManager(abc.ABC):
    @abc.abstractmethod
    async def run(
        self, session: Session
    ) -> typing.AsyncGenerator[PolicyPrediction, None]:
        pass


class EmptyPolicyManager(PolicyManager):
    async def run(
        self, session: Session
    ) -> typing.AsyncGenerator[PolicyPrediction, None]:
        return
        yield  # This makes the function an async generator


class LocalPolicyManager(PolicyManager):
    def __init__(self, policies: typing.List[Policy]):
        self.policies = policies

    async def run(
        self, session: Session
    ) -> typing.AsyncGenerator[PolicyPrediction, None]:
        for policy in self.policies:
            policy_prediction = await policy.run(session)
            logger.debug(f"policy {policy.name} returns {policy_prediction}")
            if policy_prediction is not None:
                yield policy_prediction
