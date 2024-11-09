# pylint: disable=C0301
# Line too long

from functools import cached_property
import logging
import textwrap
from typing import Optional, Dict, Any, List, Type

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.llms import LlamaCpp, HuggingFaceHub

from tomo.core.actions import Action
from tomo.shared.session import Session
from tomo.utils.instruction_builder import (
    generate_action_instruction,
    slot_instruction,
    conversation_history_instruction,
)
from tomo.utils.json import json_serializable

from .models import PolicyPrediction
from .policies import Policy


logger = logging.getLogger(__name__)


@json_serializable
class ExtractedAction(BaseModel):
    name: str = Field(description="The action name from the action list")
    arguments: Optional[Dict[str, Any]] = Field(
        description="The arguments to execute the action, if no argument needed, then it should be empty."
    )


@json_serializable
class ActionList(BaseModel):
    actions: List[ExtractedAction] = Field(description="Actions returned by LLM")


class LLMPolicy(Policy):
    """A policy based on LLM and user's prompt"""

    def __init__(
        self,
        name: str,
        scope: str,
        actions: List[str],
        intents: Optional[List[str]] = None,
        llm_config: Optional[Dict[str, Any]] = None,
    ):
        # Load config
        self._name = name
        self.intents = intents or []
        self.scope = scope
        self.actions: Type[Action] = [
            Action.get_action_cls(action) for action in actions
        ]
        self.llm_config = llm_config or {}

        llm_type = self.llm_config.get("llm_type", "openai")
        llm_params = self.llm_config.get("llm_params", {})

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

        self.system_prompt = textwrap.dedent(
            """
            Objective: Guide the system to determine and execute actions based on the user's inquiry.

            Scope: {scope}

            The assistant should only handle intents within this policy's scope and must not respond to intents outside of it.

            {intent_instruction}

            Instructions:
            1. Analyze the Conversation History:
            1.1 Focus on the last user message, which includes the detected user's intent and the messages exchanged between the user and the bot.
            1.2 Decide if any action should be taken based on the user's intent.

            2. Intent Handling:
            2.1 If the user's latest intent is not within the intents that this policy can handle, no actions should be taken, and the assistant must return an empty action list.
            2.2 Do not use any actions, including bot_utter, to respond to intents outside the policy's scope.

            3. Analyze Session Information:
            3.1 If the intent is within the policy's scope (i.e., weather), review session slot data to determine the necessary actions to fulfill the user's requirements, such as:
            3.2 Asking questions to the user to get additional information.
            3.3 Making API calls to other services to get information for filling the session slots.
            3.4 Providing information to the user.

            4. Slot Overview:
            4.1 Each session slot is a key-value pair containing specific information, which allows the system to execute an action or generate a message to the user.

            5. Post-Requirement Handling:
            5.1 Once the user's requirements are satisfied, the bot needs to wait for the user's further input by listening to the user.
            5.2 However, do not use the listen action when the user's intent is outside the policy's scope.

            6. Action Restrictions:
            6.1 Actions should only be used in response to intents within the policy's scope.
            6.2 Do not generate any actions including listen or bot_utter, for intents outside the policy's scope.

            The output should be a list of action which will be executed by order or empty list as {{"actions":[]}}.

            {format_instructions}
        """
        )

        self.session_message_promp = textwrap.dedent(
            """
            Available Actions:
            Action is the operation which the bot can take, it may have required slots, which means this action can be taken only if all these slot is filled.
                {actions}

            Conversation histories:
                {conversations}

            Session Slots: The session currently has the following slots and values:
                {slots}
        """
        )

        # Configure prompt and chain
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(self.system_prompt),
                HumanMessagePromptTemplate.from_template(self.session_message_promp),
            ]
        )

        self.output_parser = SimpleJsonOutputParser(pydantic_object=ActionList)

        # Combine prompt, LLM, and output parser in a processing chain
        self.llm_chain = self.prompt | self.llm | self.output_parser

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
        if len(self.intents) == 0:
            return "This policy can handle all intent"
        return "This policy can handle the following intents: " + ", ".join(
            self.intents
        )

    async def run(self, session: Session) -> Optional[PolicyPrediction]:
        inputs = {
            "scope": self.scope,
            "actions": self.action_instruction,
            "format_instructions": self.output_parser.get_format_instructions(),
            "intent_instruction": self.intent_instruction,
            "slots": slot_instruction(session),
            "conversations": conversation_history_instruction(session),
        }

        final_prompt = self.prompt.format_messages(**inputs)
        logger.debug(f"System message: {final_prompt[0].content}")
        logger.debug(f"User message: {final_prompt[1].content}")

        try:
            # Invoke the LLM chain with the provided inputs
            result = self.llm_chain.invoke(inputs)
            logger.debug(f"Get result from LLM: {result}")
            actions = result.get("actions")

            actions = [
                Action.create(action["name"], **action["arguments"])
                for action in actions
            ]

            return PolicyPrediction(policy_name=self.name, actions=actions)

        except Exception as e:
            logger.error(
                f"Error running policy {self.name} with LLM: {e}", exc_info=True
            )
            # Return a fallback intent and empty entities if parsing fails
            return None
