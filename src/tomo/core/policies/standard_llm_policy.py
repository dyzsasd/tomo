# pylint: disable=C0301
# Line too long

import logging
import textwrap
from typing import Optional, Dict, Any, List

from tomo.shared.session import Session
from tomo.utils.instruction_builder import (
    conversation_history_instruction,
    slot_instruction,
)

from .base_llm_policy import BaseLLMPolicy


logger = logging.getLogger(__name__)


class StandardLLMPolicy(BaseLLMPolicy):
    """Standard policy for intent-based workflows"""

    def __init__(
        self,
        name: str,
        scope: str,
        actions: List[str],
        intents: Optional[List[str]] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(name, actions, intents, llm_config, **kwargs)
        self.scope = scope

        system_prompt = textwrap.dedent(
            """
            Objective: Guide the system to determine and execute actions based on the user's inquiry.

            Scope: {scope}

            The assistant should only handle intents within this policy's scope and must not respond to intents outside of it.

            Intent Scope: {intent_instruction}

            Instructions:

            Instructions:
            1. Analyze the Conversation History and decide if any action should be taken based on the user's intent.

            2. Intent Handling:
            2.1 If the user's latest intent is not within the intents that this policy can handle, no actions should be taken, and the assistant must return an empty action list.

            3. Analyze Session Information:
            3.1 If the intent is within the policy's scope (i.e., {intent_instruction}), review session slot data to determine the necessary actions to fulfill the user's requirements, such as:
                - 3.2 Asking questions to the user to get additional information by using the `bot_utter` action to ask for specific missing slots.
                - 3.3 Making API calls to other services to get information for filling the session slots.
                - 3.4 Providing information to the user.

            4. Slot Overview:
            4.1 Each session slot is a key-value pair containing specific information, which allows the system to execute an action or generate a message to the user.

            5. Post-Requirement Handling:
            5.1 Once the user's requirements are satisfied, the bot needs to wait for the user's further input by listening to the user.
            5.2 However, do not use the listen action when the user's intent is outside the policy's scope.

            6. Action Restrictions:
            6.1 Actions should only be used in response to intents within the policy's scope.
            6.2 Do not generate any actions including listen or bot_utter, for intents outside the policy's scope.

            The output should be a list of actions which will be executed by order.

            {format_instructions}
        """
        )

        session_prompt = textwrap.dedent(
            """
            Available Actions:
            Action is the operation which the bot can take, it may have required slots, which means this action can be taken only if all these slot is filled.
            {actions}

            Conversation histories:
            The messages between user and bot ordered from oldest to latest.
            The user's message has the intent as the prefix before the text content
            {conversations}

            Session Slots: The session currently has the following slots and values:
            {slots}
        """
        )

        self.llm_chain = self._setup_chain(
            system_prompt, session_prompt, self.output_parser
        )

    def _get_inputs(self, session: Session) -> Dict[str, Any]:
        return {
            "scope": self.scope,
            "actions": self.action_instruction,
            "format_instructions": self.output_parser.get_format_instructions(),
            "intent_instruction": self.intent_instruction,
            "slots": slot_instruction(session),
            "conversations": conversation_history_instruction(session),
        }
