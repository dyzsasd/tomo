from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, Union, get_type_hints

JSON_SERIALIZABLE_KEY = "__JSON_SERIALIZABLE_KEY__"
CLASS_REGISTRY: Dict[str, Type] = {}


class JsonFormat:
    @staticmethod
    def to_json(instance: Optional[Any]) -> Dict[str, Any]:
        if instance is None:
            return None
        if not hasattr(instance, "__dict__"):
            raise TypeError(
                f"Object of type {type(instance).__name__} is not serializable"
            )
        data = {}
        for attr_name, attr_value in instance.__dict__.items():
            if hasattr(attr_value, JSON_SERIALIZABLE_KEY):
                attr_value = JsonFormat.to_json(attr_value)
            elif isinstance(attr_value, list):
                attr_value = [
                    JsonFormat.to_json(item)
                    if hasattr(item, JSON_SERIALIZABLE_KEY)
                    else item
                    for item in attr_value
                ]
            data[attr_name] = attr_value
        data["_class"] = instance.__class__.__name__
        return data

    @staticmethod
    def from_json(data: Optional[Dict[str, Any]]):
        if data is None:
            return None
        class_name = data.pop("_class", None)
        if not class_name:
            raise ValueError(
                f"Missing '_class' key in JSON data for deserialization: {data}"
            )
        cls = CLASS_REGISTRY.get(class_name)
        if not cls:
            raise ValueError(f"Unknown class: {class_name}")
        type_hints = get_type_hints(cls)

        def deserialize_value(value, field_type):
            if value is None:
                return None

            origin = getattr(field_type, "__origin__", None)
            if origin is Union:
                # Get the first non-NoneType argument (Optional is Union[T, None])
                embedded_type = next(
                    t for t in field_type.__args__ if t is not type(None)
                )
                return deserialize_value(value, embedded_type)
            if origin is list:
                item_type = field_type.__args__[0]
                return [deserialize_value(item, item_type) for item in value]
            if hasattr(field_type, JSON_SERIALIZABLE_KEY):
                return JsonFormat.from_json(value)
            return value

        deserialized_data = {}
        for field_name, field_type in type_hints.items():
            if field_name in data:
                deserialized_data[field_name] = deserialize_value(
                    data[field_name], field_type
                )
        return cls(**deserialized_data)


def json_serializable(cls):
    """Decorator to make a class JSON serializable."""
    # Register concrete classes
    abstract_methods = getattr(cls, "__abstractmethods__", None)
    if abstract_methods is None or len(abstract_methods) == 0:
        CLASS_REGISTRY[cls.__name__] = cls

    setattr(cls, JSON_SERIALIZABLE_KEY, True)
    return cls


class JSONSerializableBase:
    """Base class that ensures subclasses are registered for JSON serialization."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        dataclass(cls)
        json_serializable(cls)
