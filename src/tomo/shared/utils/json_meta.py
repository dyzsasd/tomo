import copy
from dataclasses import dataclass, fields
from typing import get_type_hints

__JSON_SERIALIZABLE_KEY = "__JSON_SERIALIZABLE_KEY__"

class JSONSerializableMeta(type):
    """Metaclass to automatically add JSON serialization and deserialization methods."""
    
    _registry = {}

    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)
        new_class = dataclass(new_class)

        # Register only concrete classes (skip abstract classes)
        if getattr(new_class, '__abstractmethods__', None) is not None:
            return new_class

        cls._registry[name] = new_class
        
        # Define the to_json method
        def to_json(self):
            data = {}
            for f in fields(self):
                attr = getattr(self, f.name)
                if hasattr(attr, __JSON_SERIALIZABLE_KEY):
                    attr = attr.to_json()
                data[f.name] = attr
            data['_class'] = self.__class__.__name__  # Add class name for deserialization
            return data

        # Define the from_json method
        @classmethod
        def from_json(cls, data):
            class_name = data.pop('_class')  # Extract class information
            subclass = cls._registry.get(class_name)
            if not subclass:
                raise ValueError(f"Unknown class: {class_name}")

            # Get type hints for each field
            type_hints = get_type_hints(subclass)

            def deserialize_value(value, field_type):
                """Handle deserialization of complex types like dataclasses."""
                # If the field type is a dataclass, recursively call from_json
                if hasattr(field_type, __JSON_SERIALIZABLE_KEY):
                    return field_type.from_json(value)
                return value

            # Deserialize fields based on type hints
            deserialized_data = {}
            for field_name, field_type in type_hints.items():
                if field_name in data:
                    deserialized_data[field_name] = deserialize_value(data[field_name], field_type)

            return subclass(**deserialized_data)

        # Add methods to the class if not already defined
        dct['to_json'] = to_json
        dct['from_json'] = from_json

        setattr(new_class, __JSON_SERIALIZABLE_KEY, True)

        return new_class
