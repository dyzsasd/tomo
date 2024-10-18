import abc


class Slot(abc.ABC):
    """
    Represents a key-value pair to store context or information extracted from the user
    during the conversation.
    """

    def __init__(self, name: str, initial_value=None, auto_fill: bool = True):
        """
        Initialize a Slot.

        Args:
            name: The name of the slot (key).
            initial_value: The initial value of the slot (optional).
            auto_fill: If True, the slot will be filled automatically from extracted entities.
        """
        self.name = name
        self.value = initial_value
        self.auto_fill = auto_fill

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