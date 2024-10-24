from dataclasses import dataclass
from typing import get_type_hints, Type, Dict, Any, Optional, Optional


JSON_SERIALIZABLE_KEY = "__JSON_SERIALIZABLE_KEY__"
CLASS_REGISTRY: Dict[str, Type] = {}


class JsonFormat:
    @staticmethod
    def to_json(instance: Optional[Any]) -> Dict[str, Any]:
        if instance is None:
            return None
        if not hasattr(instance, '__dict__'):
            raise TypeError(f"Object of type {type(instance).__name__} is not serializable")
        data = {}
        for attr_name, attr_value in instance.__dict__.items():
            if hasattr(attr_value, JSON_SERIALIZABLE_KEY):
                attr_value = JsonFormat.to_json(attr_value)
            elif isinstance(attr_value, list):
                JsonFormat = [
                    Json.to_json(item) if hasattr(item, JSON_SERIALIZABLE_KEY) else item
                    for item in attr_value
                ]
            data[attr_name] = attr_value
        data['_class'] = instance.__class__.__name__
        return data

    @staticmethod
    def from_json(data: Optional[Dict[str, Any]]):
        if data is None:
            return None
        class_name = data.pop('_class', None)
        if not class_name:
            raise ValueError("Missing '_class' key in JSON data for deserialization")
        cls = CLASS_REGISTRY.get(class_name)
        if not cls:
            raise ValueError(f"Unknown class: {class_name}")
        type_hints = get_type_hints(cls)

        def deserialize_value(value, field_type):
            origin = getattr(field_type, '__origin__', None)
            if origin is list:
                item_type = field_type.__args__[0]
                return [deserialize_value(item, item_type) for item in value]
            elif hasattr(field_type, JSON_SERIALIZABLE_KEY):
                return JsonFormat.from_json(value)
            else:
                return value

        deserialized_data = {}
        for field_name, field_type in type_hints.items():
            if field_name in data:
                deserialized_data[field_name] = deserialize_value(data[field_name], field_type)
        return cls(**deserialized_data)


def json_serializable(cls):
    """Decorator to make a class JSON serializable."""
    # Register concrete classes
    if getattr(cls, '__abstractmethods__', None) is None:
        CLASS_REGISTRY[cls.__name__] = cls
    setattr(cls, JSON_SERIALIZABLE_KEY, True)
    return cls


class JSONSerializableBase:
    """Base class that ensures subclasses are registered for JSON serialization."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        json_serializable(cls)
        dataclass(cls)

