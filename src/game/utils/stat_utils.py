"""
Stat utility functions to reduce code duplication
Provides common stat-related calculations and operations
"""

from typing import Dict, Any, Union
from enum import Enum


class StatUtils:
    """
    Utility class for common stat-related operations.
    Reduces code duplication across entity classes.
    """
    
    @staticmethod
    def calculate_percentage(current: int, maximum: int) -> float:
        """
        Calculate percentage with safe division.
        
        Args:
            current: Current value
            maximum: Maximum value
            
        Returns:
            Percentage as float (0-100)
        """
        if maximum <= 0:
            return 0.0
        return (current / maximum) * 100
    
    @staticmethod
    def apply_stat_bonuses(base_stats: Dict[Any, int], bonuses: Dict[Any, int]) -> Dict[Any, int]:
        """
        Apply stat bonuses to base stats.
        
        Args:
            base_stats: Base stat values
            bonuses: Bonus values to apply
            
        Returns:
            New dictionary with bonuses applied
        """
        result = base_stats.copy()
        for stat, bonus in bonuses.items():
            if stat in result:
                result[stat] = max(0, result[stat] + bonus)
            else:
                result[stat] = max(0, bonus)
        return result
    
    @staticmethod
    def calculate_quality_multiplier(quality: Enum) -> float:
        """
        Calculate quality multiplier for items.
        
        Args:
            quality: Item quality enum
            
        Returns:
            Multiplier value
        """
        quality_multipliers = {
            'poor': 0.8,
            'normal': 1.0,
            'good': 1.2,
            'excellent': 1.4,
            'perfect': 1.6
        }
        
        quality_name = quality.value.lower() if hasattr(quality, 'value') else str(quality).lower()
        return quality_multipliers.get(quality_name, 1.0)
    
    @staticmethod
    def calculate_level_up_bonuses(level: int, base_bonuses: Dict[Any, int]) -> Dict[Any, int]:
        """
        Calculate level up bonuses based on level.
        
        Args:
            level: Current level
            base_bonuses: Base bonus values per level
            
        Returns:
            Calculated bonuses for this level
        """
        bonuses = {}
        for stat, bonus in base_bonuses.items():
            bonuses[stat] = bonus * level
        return bonuses
    
    @staticmethod
    def clamp_stat_value(value: int, min_value: int = 0, max_value: int = None) -> int:
        """
        Clamp a stat value between min and max.
        
        Args:
            value: Value to clamp
            min_value: Minimum allowed value
            max_value: Maximum allowed value (None for no max)
            
        Returns:
            Clamped value
        """
        if max_value is not None:
            return max(min_value, min(value, max_value))
        return max(min_value, value)
    
    @staticmethod
    def calculate_damage(base_damage: int, defense: int, multiplier: float = 1.0) -> int:
        """
        Calculate damage after defense and multiplier.
        
        Args:
            base_damage: Base damage value
            defense: Defense value
            multiplier: Damage multiplier
            
        Returns:
            Final damage value
        """
        damage = int(base_damage * multiplier)
        return max(1, damage - defense)
    
    @staticmethod
    def calculate_healing(base_healing: int, current_health: int, max_health: int) -> int:
        """
        Calculate actual healing amount.
        
        Args:
            base_healing: Base healing value
            current_health: Current health
            max_health: Maximum health
            
        Returns:
            Actual healing amount (limited by max health)
        """
        return min(base_healing, max_health - current_health)
