# pylint: disable=R0911
from abc import ABC, abstractmethod
from dataclasses import dataclass, is_dataclass, fields
from datetime import datetime
from typing import Any, Dict, Type, TypeVar, Union, get_type_hints, get_origin, get_args


T = TypeVar("T")  # Generic type for the target class

basic_types = (str, int, float, bool)


class JsonFormatter(ABC):
    """Abstract base class for custom JSON formatters"""

    @abstractmethod
    def to_json(self, instance: Any) -> Dict[str, Any]:
        """Convert instance to JSON-compatible dictionary"""

    @abstractmethod
    def from_json(self, data: Dict[str, Any], target_cls: Type[T]) -> T:
        """Convert JSON-compatible dictionary back to instance"""


class PolymorphicDataclassFormatter(JsonFormatter):
    """JSON formatter that handles polymorphic dataclasses"""

    def to_json(self, instance: Any) -> Dict[str, Any]:
        if not is_dataclass(instance):
            raise TypeError(f"Expected dataclass instance, got {type(instance)}")

        result = {
            "_type": f"{instance.__class__.__module__}.{instance.__class__.__qualname__}"
        }

        type_hints = get_type_hints(instance.__class__)

        # Handle fields defined in dataclass
        for field in fields(instance):
            value = getattr(instance, field.name)
            if value is not None:
                result[field.name] = self._serialize_value(
                    value, type_hints[field.name]
                )

        return result

    def from_json(self, data: Dict[str, Any], target_cls: Type[T]) -> T:
        """Convert JSON-compatible dictionary back to instance"""
        if not is_dataclass(target_cls):
            raise TypeError(f"Expected dataclass type, got {target_cls}")

        # Get the actual class if type information is present
        if "_type" in data:
            actual_cls = self._get_class_from_type_string(data["_type"])
            if not issubclass(actual_cls, target_cls):
                raise TypeError(f"{actual_cls} is not a subclass of {target_cls}")
            target_cls = actual_cls

        field_values = {}
        type_hints = get_type_hints(target_cls)

        # Process only the fields defined in the dataclass
        for field in fields(target_cls):
            if field.name in data:
                field_values[field.name] = self._deserialize_value(
                    data[field.name], type_hints.get(field.name, Any)
                )

        # Create instance with dataclass fields
        instance = target_cls(**field_values)

        # Set additional attributes that were not part of the dataclass definition
        dataclass_fields = {f.name for f in fields(target_cls)}
        for key, value in data.items():
            if key not in dataclass_fields and not key.startswith("_"):
                setattr(instance, key, value)

        return instance

    def _serialize_value(self, value: Any, field_type: Type) -> Any:
        if value is None:
            return None

        # Handle primitive types
        if isinstance(value, basic_types):
            return value

        # Handle dataclass fields
        if is_dataclass(value):
            return JsonEngine.to_json(value)

        # Handle lists
        origin = get_origin(field_type)
        if origin is list:
            item_type = get_args(field_type)[0]
            return [self._serialize_value(item, item_type) for item in value]
        if origin is dict:
            item_type = get_args(field_type)[0]
            return {k: self._serialize_value(v, item_type) for k, v in value.items()}
        if origin is Union:
            item_type = get_args(field_type)[0]
            return self._serialize_value(value, item_type)

        # For other types, try to find a custom formatter
        return JsonEngine.to_json(value)

    def _deserialize_value(self, value: Any, field_type: Type) -> Any:
        """Deserialize a value based on its intended type"""
        if value is None:
            return None

        if field_type == Any or field_type in basic_types:
            return value

        # If the value is a dict and has '_type' field, it's a nested object
        if isinstance(value, dict) and "_type" in value:
            # Get the actual class from the type information
            actual_cls = self._get_class_from_type_string(value["_type"])
            return self.from_json(value, actual_cls)

        # Handle dataclass fields
        if is_dataclass(field_type):
            return JsonEngine.from_json(value, field_type)

        # Handle lists
        origin = get_origin(field_type)
        if origin is list:
            item_type = get_args(field_type)[0]
            return [self._deserialize_value(item, item_type) for item in value]
        if origin is dict:
            item_type = get_args(field_type)[0]
            return {k: self._deserialize_value(v, item_type) for k, v in value.items()}
        if origin is Union:
            item_type = get_args(field_type)[0]
            return self._deserialize_value(value, item_type)

        return JsonEngine.from_json(value, field_type)

    def _get_class_from_type_string(self, type_string: str) -> Type:
        """Convert a type string to actual class"""
        try:
            module_path, class_name = type_string.rsplit(".", 1)

            # Handle nested classes
            class_parts = class_name.split(".")

            # Import the module
            module = __import__(module_path, fromlist=[class_parts[0]])

            # Get the class
            cls = getattr(module, class_parts[0])

            # Handle nested classes
            for part in class_parts[1:]:
                cls = getattr(cls, part)

            return cls
        except Exception as e:
            raise ValueError(f"Could not resolve class {type_string}") from e


class JsonEngine:
    """Central engine for JSON serialization/deserialization"""

    _formatters: Dict[Type, JsonFormatter] = {}
    _default_formatter = PolymorphicDataclassFormatter()

    @classmethod
    def register_formatter(cls, target_type: Type, formatter: JsonFormatter):
        """Register a custom formatter for a specific type"""
        cls._formatters[target_type] = formatter

    @classmethod
    def to_json(cls, instance: Any) -> Dict[str, Any]:
        """Convert an instance to a JSON-compatible dictionary"""
        if instance is None:
            return None

        formatter = cls._get_formatter(instance.__class__)
        if formatter is None:
            raise ValueError(f"formatter is mission for {instance}")
        return formatter.to_json(instance)

    @classmethod
    def from_json(cls, data: Dict[str, Any], target_cls: Type[T]) -> T:
        """Convert a JSON-compatible dictionary to an instance"""
        if data is None:
            return None

        formatter = cls._get_formatter(target_cls)
        if formatter is None:
            raise ValueError(f"formatter is mission for {target_cls}")
        return formatter.from_json(data, target_cls)

    @classmethod
    def _get_formatter(cls, target_type: Type) -> JsonFormatter:
        """Get the appropriate formatter for a type"""
        return cls._formatters.get(target_type, cls._default_formatter)


class DatetimeFormatter(JsonFormatter):
    def to_json(self, instance: datetime) -> Dict[str, Any]:
        return instance.isoformat()

    def from_json(self, data: Dict[str, Any], target_cls: Type[T]) -> T:
        return datetime.fromisoformat(data)


# Register custom formatter for datetime
JsonEngine.register_formatter(datetime, DatetimeFormatter())


class DataclassABC(ABC):
    """Abstract base class that automatically converts children to dataclasses"""

    def __init_subclass__(cls, **kwargs):
        """Called when a class inherits from this class"""
        super().__init_subclass__(**kwargs)

        # Skip if class is abstract
        abstract_methods = getattr(cls, "__abstractmethods__", set())
        if not abstract_methods:
            # Only apply dataclass if it's not already a dataclass
            dataclass(cls)
