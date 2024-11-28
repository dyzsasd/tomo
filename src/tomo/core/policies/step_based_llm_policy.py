# pylint: disable=C0301
# Line too long

import logging
import textwrap
from typing import Optional, Dict, Any, List

from tomo.shared.action import Action
from tomo.shared.session import Session
from tomo.shared.exceptions import TomoFatalException
from tomo.utils.instruction_builder import (
    conversation_history_instruction,
    slot_instruction,
)

from .base_llm_policy import BaseLLMPolicy
from .models import PolicyPrediction


logger = logging.getLogger(__name__)


def step_descriptions(steps: List[Dict[str, Any]]) -> str:
    instructions = []
    for step in steps:
        instructions.append(
            textwrap.dedent(
                f"""
        - step name: {step["id"]}
          description: {step["description"]}
        """
            )
        )
    return "\n".join(instructions)


def current_step_instruction(step: Dict[str, Any]) -> str:
    return textwrap.dedent(
        f"""
        step name: {step["id"]}
        step description: {step["description"]}
        step instruction: {step["prompt"]}
    """
    )


class StepBasedLLMPolicy(BaseLLMPolicy):
    """Policy for step-based workflows"""

    def __init__(
        self,
        steps: List[Dict[str, Any]],
        actions: List[str],
        llm_config: Optional[Dict[str, Any]] = None,
        intents: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__("step_based_policy", actions, intents, llm_config, **kwargs)
        self.steps = steps
        self.step_dict = {step["id"]: step for step in self.steps}

        system_prompt = textwrap.dedent(
            """
            You are an intelligent agent within multi-agent based customer service system, your responsability is guiding the system to determine and execute actions in order to finish the flight ticket exchange process.

            The assistant is responsible for determining the appropriate actions from the available actions list, based on the current session state and conversation history.

            1.  Session State: The session state is represented by a set of slots that store specific information about the customer and their booking.
            2.  Conversation History: All messages between the customer and the assistant are logged as conversation history. Each customer message begins with a JSON prefix that indicates the customer's intent, providing context for the assistant to decide the next action.

            The exchange process is broken down into a series of steps , each associated with specific objectif and actions that the assistant should take.
            Here is the steps of following:

            {step_descriptions}

            In order to select the action to execute, the assistant should:
            1. Check in which step currently the system is.
            2. Check the session state, the customer bot conversation history and the step instructions.
            3. Decide select the right actions the system should execute from the available actions list.

            The output should be a list of actions which will be executed by order, here is the available actions

            Action is the operation which the bot can take, it may have required slots, which means this action can be taken only if all these slot is filled.
            {actions}

            {format_instructions}
        """
        )

        session_prompt = textwrap.dedent(
            """
            The current step the process is:
            {current_step}

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

    async def run(self, session: Session) -> Optional[PolicyPrediction]:
        current_step_slot = session.slots.get("step")
        current_step_name = current_step_slot is not None and current_step_slot.value
        if current_step_name is None:
            return PolicyPrediction(
                policy_name=self.name,
                actions=[Action.create("update_step", step_name=self.steps[0]["id"])],
            )

        return await super().run(session)

    def _get_inputs(self, session: Session) -> Dict[str, Any]:
        current_step_name = session.slots.get("step").value
        if current_step_name is None:
            raise TomoFatalException("Session step slot is None")

        current_step = self.step_dict.get(current_step_name)
        if current_step is None:
            raise TomoFatalException(f"{current_step_name} isn't in step dictionary")

        return {
            "step_descriptions": step_descriptions(self.steps),
            "actions": self.action_instruction,
            "format_instructions": self.output_parser.get_format_instructions(),
            "current_step": current_step_instruction(current_step),
            "conversations": conversation_history_instruction(session),
            "slots": slot_instruction(session),
        }
