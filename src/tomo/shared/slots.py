from dataclasses import dataclass
from typing import Any, Optional

from tomo.utils.json import json_serializable


@dataclass
@json_serializable
class Slot:
    """
    Represents a key-value pair to store context or information extracted from the user
    during the conversation.
    """

    name: str
    extractable: bool
    value: Optional[Any] = None
    initial_value: Optional[Any] = None
    description: Optional[str] = None

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
