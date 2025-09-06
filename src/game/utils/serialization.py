"""
Serialization utilities to reduce code duplication
Provides common serialization patterns for game objects
"""

from typing import Dict, Any, Type, TypeVar
from abc import ABC, abstractmethod

T = TypeVar('T', bound='SerializableMixin')


class SerializableMixin:
    """
    Mixin class that provides common serialization functionality.
    Reduces code duplication across game objects.
    """
    
    def _get_serialization_data(self) -> Dict[str, Any]:
        """
        Get the data to be serialized. Should be implemented by subclasses.
        Returns empty dict by default.
        """
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert object to dictionary for serialization.
        Uses _get_serialization_data() to get the actual data.
        """
        return self._get_serialization_data()
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create object from dictionary data.
        Must be implemented by subclasses for proper reconstruction.
        """
        raise NotImplementedError(f"{cls.__name__} must implement from_dict method")
    
    def _serialize_enum(self, enum_value) -> str:
        """Helper method to serialize enum values"""
        return enum_value.value if hasattr(enum_value, 'value') else str(enum_value)
    
    def _serialize_list(self, items: list, serializer_func=None) -> list:
        """Helper method to serialize lists of objects"""
        if serializer_func is None:
            serializer_func = lambda x: x.to_dict() if hasattr(x, 'to_dict') else x
        return [serializer_func(item) for item in items]
    
    def _serialize_dict(self, items: dict, key_serializer=None, value_serializer=None) -> dict:
        """Helper method to serialize dictionaries"""
        if key_serializer is None:
            key_serializer = lambda x: x.value if hasattr(x, 'value') else str(x)
        if value_serializer is None:
            value_serializer = lambda x: x.to_dict() if hasattr(x, 'to_dict') else x
        
        return {
            key_serializer(k): value_serializer(v) 
            for k, v in items.items()
        }
