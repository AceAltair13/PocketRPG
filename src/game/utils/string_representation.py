"""
String representation utilities to reduce code duplication
Provides common string formatting patterns for game objects
"""

from typing import Any, Dict, Optional


class StringRepresentationMixin:
    """
    Mixin class that provides common string representation functionality.
    Reduces code duplication across game objects.
    """
    
    def _get_display_name(self) -> str:
        """
        Get the display name for the object.
        Can be overridden by subclasses for custom formatting.
        """
        return getattr(self, 'name', self.__class__.__name__)
    
    def _get_basic_info(self) -> Dict[str, Any]:
        """
        Get basic information about the object for string representation.
        Should be overridden by subclasses to provide relevant info.
        """
        return {
            'name': self._get_display_name(),
            'class': self.__class__.__name__
        }
    
    def _format_basic_string(self, info: Optional[Dict[str, Any]] = None) -> str:
        """Format a basic string representation"""
        if info is None:
            info = self._get_basic_info()
        
        name = info.get('name', 'Unknown')
        class_name = info.get('class', self.__class__.__name__)
        
        return f"{name} ({class_name})"
    
    def _format_detailed_string(self, info: Optional[Dict[str, Any]] = None) -> str:
        """Format a detailed string representation"""
        if info is None:
            info = self._get_basic_info()
        
        name = info.get('name', 'Unknown')
        class_name = info.get('class', self.__class__.__name__)
        
        # Add additional info if available
        parts = [f"{class_name}(name='{name}'"]
        
        # Add other relevant attributes
        for key, value in info.items():
            if key not in ['name', 'class']:
                parts.append(f"{key}={value}")
        
        parts.append(")")
        return ", ".join(parts)
    
    def __str__(self) -> str:
        """String representation of the object"""
        return self._format_basic_string()
    
    def __repr__(self) -> str:
        """Detailed string representation of the object"""
        return self._format_detailed_string()
