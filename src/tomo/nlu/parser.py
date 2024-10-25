import logging
from typing import Any, Dict, Optional

from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.llms import LlamaCpp, HuggingFaceHub

from tomo.core.user_message import UserMessage
from tomo.nlu.models import NLUExtraction, Intent, Entity
from tomo.shared.session import Session

logger = logging.getLogger(__name__)


class NLUParser:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Load config
        self.config = config or {}
        llm_type = self.config.get("llm_type", "openai")
        llm_params = self.config.get("llm_params", {})

        # Initialize LLM based on type
        if llm_type == "openai":
            self.llm = ChatOpenAI(**llm_params)
        elif llm_type == "azure_openai":
            self.llm = AzureChatOpenAI(**llm_params)
        elif llm_type == "llamacpp":
            self.llm = LlamaCpp(**llm_params)
        elif llm_type == "huggingfacehub":
            self.llm = HuggingFaceHub(**llm_params)
        else:
            raise ValueError(f"LLM type '{llm_type}' is not supported.")

        self.intents = self.config.get("intents")
        if not self.intents:
            raise ValueError("An 'intents' list is required in the config.")

        self.entities = self.config.get("entities")
        if not self.entities:
            raise ValueError("An 'entities' list is required in the config.")

        # Define output parser for structured responses
        self.output_parser = SimpleJsonOutputParser(pydantic_object=NLUExtraction)

        # Define the system message prompt
        self.system_prompt = """
            You are a natural language understanding assistant of chat assistant service called Tomo responsible for analyzing user input, extracting intents, and entities.

            Available intents list: {intents}
            Available entities list: {entities}

            Conversation history:
            {conversation_history}

            Please return results in the following format:
            {format_instructions}
        """

        logger.debug(f"System prompt is:\n{self.system_prompt}")

        # Configure prompt and chain
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(self.system_prompt),
                HumanMessagePromptTemplate.from_template("{user_input}"),
            ]
        )

        # Combine prompt, LLM, and output parser in a processing chain
        self.llm_chain = self.prompt | self.llm | self.output_parser

    def generate_history_from_session(self, session: Session):
        # TODO: generate conversation history
        history = str(session.events)
        return history

    async def parse(self, message: UserMessage, session: Session) -> Dict:
        """Parse a user message to extract intents and entities."""
        logger.debug(f"Processing message: {message.text}")

        conversation_history = self.generate_history_from_session(session)
        conversation_history = ""

        # Prepare the inputs for the LLM
        inputs = {
            "user_input": message.text,
            "intents": ", ".join(self.intents),
            "entities": ", ".join(self.entities),
            "conversation_history": conversation_history,
            "format_instructions": self.output_parser.get_format_instructions(),
        }

        final_prompt = self.prompt.format_messages(**inputs)
        logger.debug(f"Prompt sent to LLM: {final_prompt}")

        try:
            # Invoke the LLM chain with the provided inputs
            result = self.llm_chain.invoke(inputs)
            logger.debug(f"Get result from LLM: {result}")

            # Process result (an instance of IntentExtraction)
            intent = result.get("intent")
            entities = result.get("entities")

            # Log and return extracted intent and entities
            logger.debug(f"Extracted intent: {intent} with entities: {entities}")
            return {
                "intent": intent or Intent(**intent),
                "entities": [Entity(**entity) for entity in entities or []],
            }

        except Exception as e:
            logger.error(f"Error processing message with LLM: {e}", exc_info=True)
            # Return a fallback intent and empty entities if parsing fails
            return {"intent": {"name": "unknown", "confidence": 0.0}, "entities": []}
