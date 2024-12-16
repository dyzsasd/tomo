import json
from typing import List, Type

from pydantic import BaseModel
from tomo.core.actions import Action
from tomo.core.events import BotUttered, UserUttered
from tomo.shared.exceptions import TomoFatalException
from tomo.core.session import Session


def generate_action_instruction(action: Type[Action]):
    instructions: List = [
        f"Action Name: {action.name}",
        f"Description: {action.description}",
    ]
    required_slots = action.required_slots()
    if required_slots is not None and len(required_slots) > 0:
        instructions.append("Required Slots:")
        for slot in required_slots:
            instructions.append(f"- {slot}")

    # Pydantic model fields
    if issubclass(action, BaseModel):
        user_fields = action.model_fields.values()
        if user_fields:
            instructions.append("Arguments to execute the action:")
            for field in user_fields:
                description = field.description or "No description provided"
                instructions.append(
                    f"Field Name: {field.name}, Field Type:"
                    f" {field.type_}, Description: {description}"
                )
        else:
            instructions.append("No Arguments are needed to execute the action")

    return "\n".join(instructions)


def slot_instruction(session: Session, only_extractable=False) -> str:
    instructions = []
    for _, slot in session.slots.items():
        if only_extractable and not slot.extractable:
            continue
        items = [
            f"Slot Name: {slot.name}",
            f"Description: {slot.description}",
        ]
        curr_value = slot.get_value()
        if curr_value is not None:
            items.append(f"Current Value: {curr_value}")
        else:
            items.append("Current Value: not filled")
        instructions.append("\n".join(items))
    if len(instructions) == 0:
        raise TomoFatalException("No slot found in session.")
    return "\n\n".join(instructions)


def conversation_history_instruction(session: Session) -> str:
    instructions = []
    for event in session.events:
        if isinstance(event, BotUttered):
            instructions.append(f"Bot: {event.text}")
        if isinstance(event, UserUttered):
            instructions.append(f"User: (intent: {event.intent_name}) - {event.text}")
    return "\n".join(instructions)


def json_conversation_history_instruction(session: Session) -> str:
    instructions = []
    for event in session.events:
        if isinstance(event, BotUttered):
            instructions.append({"from": "Bot", "message": event.text})
        if isinstance(event, UserUttered):
            instructions.append(
                {"from": "Customer", "intent": event.intent_name, "message": event.text}
            )
    return json.dumps(instructions, indent=2)


def json_slot_instruction(session: Session, only_extractable=False) -> str:
    instructions = []
    for _, slot in session.slots.items():
        if only_extractable and not slot.extractable:
            continue
        item = {
            "name": slot.name,
            "description": slot.description,
        }
        curr_value = slot.get_value()
        if curr_value is not None:
            item["current value"] = curr_value
        else:
            item["current value"] = "not filled"
        instructions.append(item)
    if len(instructions) == 0:
        raise TomoFatalException("No slot found in session.")
    return json.dumps(instructions, indent=2)


def json_generate_action_instruction(action: Type[Action]):
    instructions = {
        "action name": action.name,
        "description": action.description,
    }
    required_slots = action.required_slots()
    if required_slots is not None and len(required_slots) > 0:
        instructions["required slots"] = required_slots

    # Pydantic model fields
    if issubclass(action, BaseModel):
        user_fields = action.model_fields
        if user_fields:
            instructions["required arguments"] = [
                {
                    "Field Name": name,
                    "Field Type": str(field.discriminator),
                    "Description": field.description or "No description provided",
                }
                for name, field in user_fields.items()
            ]
        else:
            instructions[
                "required arguments"
            ] = "No Arguments are needed to execute the action"

    return json.dumps(instructions, indent=2)
