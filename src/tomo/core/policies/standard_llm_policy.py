# pylint: disable=C0301
# Line too long
import json
import logging
import textwrap
from typing import Optional, Dict, Any, List

from tomo.shared.session import Session
from tomo.utils.instruction_builder import (
    json_conversation_history_instruction,
    slot_instruction,
)

from .base_llm_policy import BaseLLMPolicy


logger = logging.getLogger(__name__)


class StandardLLMPolicy(BaseLLMPolicy):
    """Standard policy for intent-based workflows"""

    def __init__(
        self,
        name: str,
        mission: str,
        instructions: str,
        actions: List[str],
        intents: Optional[List[str]] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(name, actions, intents, llm_config, **kwargs)

        system_prompt = (
            json.dumps(
                {
                    "persona": [
                        "You are an intelligent agent within multi-agent based customer service system, your responsability is guiding the system to determine and execute actions in order to complete the specific missions",
                        "The assistant should only handle intents within this intent scope and must not respond to intents outside of it",
                        "The assistant is responsible for determining the appropriate actions from the actions list, based on the current session state and conversation history.",
                        "1.  Session State: The session state is represented by a set of slots that store specific information about the customer and their booking.",
                        "2.  Conversation History: All messages between the customer and the assistant are logged as conversation history. Each customer message contains the customer's intent, providing context for the assistant to decide the next action.",
                        "In order to select the action to execute, the assistant should",
                        "1. Check the session state, the customer bot conversation history and the instructions.",
                        "2. Select the right actions the system should execute from the available actions list.",
                    ],
                    "mession": mission,
                    "intent scope": self.intent_instruction,
                    "instructions": instructions,
                    "actions": self.action_instruction,
                    "output_format": self.output_parser.get_format_instructions(),
                },
                indent=2,
            )
            .replace("{", "{{")
            .replace("}", "}}")
        )

        human_prompt = textwrap.dedent(
            """
        {{
            "slots": "{slots}",
            "conversations": "{conversations}"
        }}
        """
        )
        self.llm_chain = self._setup_chain(
            system_prompt, human_prompt, self.output_parser
        )

    def _get_inputs(self, session: Session) -> Dict[str, Any]:
        return {
            "slots": slot_instruction(session),
            "conversations": json_conversation_history_instruction(session),
        }
