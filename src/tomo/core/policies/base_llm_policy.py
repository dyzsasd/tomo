from functools import cached_property
import logging
from typing import Optional, Dict, Any, List

from langchain.output_parsers.json import SimpleJsonOutputParser

from tomo.core.base_llm_component import BaseLLMComponent
from tomo.shared.action import Action
from tomo.shared.session import Session
from tomo.utils.instruction_builder import generate_action_instruction

from .policies import Policy
from .models import ActionList, PolicyPrediction


logger = logging.getLogger(__name__)


class BaseLLMPolicy(BaseLLMComponent, Policy):
    """Base class for LLM-based policies"""

    def __init__(
        self,
        name: str,
        actions: List[str],
        intents: Optional[List[str]] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        local_test: bool = False,
    ):
        super().__init__(llm_config)
        self._name = name
        self.intents = intents or []
        self.actions = [Action.get_action_cls(action) for action in actions]

        self.output_parser = SimpleJsonOutputParser(pydantic_object=ActionList)
        self.llm_chain = None  # To be set by subclasses

        self.local_test = local_test

    @property
    def name(self):
        return self._name

    @cached_property
    def action_instruction(self):
        return "\n\n".join(
            [generate_action_instruction(action) for action in self.actions]
        )

    @cached_property
    def intent_instruction(self):
        if not self.intents:
            return "all intents"
        return ", ".join(self.intents)

    async def run(self, session: Session) -> Optional[PolicyPrediction]:
        try:
            inputs = self._get_inputs(session)

            if self.local_test:
                final_prompt = self.prompt.format_messages(**inputs)
                self._save_prompts(
                    session.session_id,
                    [msg.content for msg in final_prompt],
                    f"policy-{self.name}",
                )

            result = self.llm_chain.invoke(inputs)
            actions = [
                Action.create(action["name"], **action["arguments"])
                for action in result.get("actions", [])
            ]

            return PolicyPrediction(policy_name=self.name, actions=actions)

        except Exception as e:
            logger.error(
                f"Error running policy {self.name} with LLM: {e}", exc_info=True
            )
            return None

    def _get_inputs(self, session: Session) -> Dict[str, Any]:
        """Get inputs for the LLM chain - to be implemented by subclasses"""
        raise NotImplementedError
