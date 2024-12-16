from inspect import isclass
from typing import Union, Type

from pydantic import BaseModel


def get_event_union(base_class: Type[BaseModel]) -> Type:
    """
    Dynamically generate a Union type of all subclasses of the given base class.
    """
    subclasses = base_class.__subclasses__()
    # Filter only classes that are still subclasses of BaseModel
    valid_subclasses = [
        cls for cls in subclasses if isclass(cls) and issubclass(cls, BaseModel)
    ]
    return Union[tuple(valid_subclasses)]
