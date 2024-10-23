import abc
import typing

from tomo.shared.sessions import Session

from .policy import PolicyPrediction

# TODO: implement policy manager
class PolicyManager(abc.ABC):
    @abc.abstractmethod
    async def run(self, session: Session) -> typing.AsyncGenerator[PolicyPrediction, None]:
        pass