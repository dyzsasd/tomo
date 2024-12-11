# pylint: disable=C0301
# Line too long

from functools import cached_property
import logging
import textwrap
from typing import Any, Dict, List, Optional

from langchain.output_parsers.json import SimpleJsonOutputParser

from tomo.core.base_llm_component import BaseLLMComponent
from tomo.core.user_message import UserMessage
from tomo.nlu.models import NLUExtraction, Entity, IntentExtraction
from tomo.shared.intent import Intent
from tomo.core.session import Session
from tomo.utils.instruction_builder import (
    slot_instruction,
    conversation_history_instruction,
)


logger = logging.getLogger(__name__)


class NLUParser(BaseLLMComponent):
    """NLU parser using LLM"""

    def __init__(
        self,
        intents: List[Intent],
        config: Optional[Dict[str, Any]] = None,
        local_test=False,
    ):
        super().__init__(config)
        self.intents = intents
        self.output_parser = SimpleJsonOutputParser(pydantic_object=NLUExtraction)
        self.local_test = local_test

        system_prompt = textwrap.dedent(
            """
            You are a natural language understanding assistant responsible for analyzing user input, extracting intents, and entities for filling the slots in the conversation session.

            The extraction should consider the conversation history
            Conversation history:
            {conversation_history}

            The intent should be chosen from this available intents list:
            {intents}

            Then entities should be extract for filling these session slots, the slot may contains already a value, in this case you need to decide if it should be replaced:
            {slots}

            Please return results in the following format:
            {format_instructions}
        """
        )

        self.llm_chain = self._setup_chain(
            system_prompt, "{user_input}", self.output_parser
        )

    @cached_property
    def intent_instruction(self):
        return "\n\n".join(
            f"Intent Name: {intent.name}\nDescription: {intent.description}"
            for intent in self.intents
        )

    async def parse(self, message: UserMessage, session: Session) -> Dict:
        try:
            inputs = {
                "user_input": message.text,
                "intents": self.intent_instruction,
                "slots": slot_instruction(session, only_extractable=True),
                "conversation_history": conversation_history_instruction(session),
                "format_instructions": self.output_parser.get_format_instructions(),
            }

            if self.local_test:
                final_prompt = self.prompt.format_messages(**inputs)
                self._save_prompts(
                    session.session_id, [msg.content for msg in final_prompt], "nlu"
                )

            result = self.llm_chain.invoke(inputs)
            intent = result.get("intent")
            entities = result.get("entities", [])

            return {
                "intent": intent and IntentExtraction(**intent),
                "entities": [Entity(**entity) for entity in entities],
            }

        except Exception as e:
            logger.error(f"Error processing message with LLM: {e}", exc_info=True)
            return {"intent": {"name": "unknown", "confidence": 0.0}, "entities": []}
