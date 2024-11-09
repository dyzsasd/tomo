from typing import Any, Optional

from tomo.utils.json import json_serializable


@json_serializable
class Slot:
    """
    Represents a key-value pair to store context or information extracted from the user
    during the conversation.
    """

    def __init__(
        self,
        name: str,
        extractable: bool,
        initial_value: Optional[Any] = None,
        description: Optional[str] = None,
    ):
        """
        Initialize a Slot.

        Args:
            name: The name of the slot (key).
            initial_value: The initial value of the slot (optional).
            description: the description
        """
        self.name = name
        self.extractable = extractable
        self.value = initial_value
        self.description = description

    def set_value(self, value):
        """
        Set the value of the slot.

        Args:
            value: The value to assign to the slot.
        """
        self.value = value

    def get_value(self):
        """
        Get the current value of the slot.

        Returns:
            The current value of the slot.
        """
        return self.value

    def reset(self):
        """
        Reset the slot to its initial value.
        """
        self.value = None

    def __repr__(self):
        return f"<Slot name={self.name} value={self.value}>"
