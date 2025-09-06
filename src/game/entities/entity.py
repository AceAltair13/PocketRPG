"""
Entity base class for all game characters (Player, Enemy, NPCs)
This is the foundation for all living entities in the RPG
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class EntityType(Enum):
    """Types of entities in the game"""
    PLAYER = "player"
    ENEMY = "enemy"
    NPC = "npc"
    BOSS = "boss"


class StatType(Enum):
    """Core stat types for entities"""
    HEALTH = "health"
    MAX_HEALTH = "max_health"
    MANA = "mana"
    MAX_MANA = "max_mana"
    ATTACK = "attack"
    DEFENSE = "defense"
    SPEED = "speed"
    LEVEL = "level"
    EXPERIENCE = "experience"


class Entity(ABC):
    """
    Base class for all entities in the game.
    Provides core functionality for health, stats, and basic combat mechanics.
    """
    
    def __init__(self, name: str, entity_type: EntityType, level: int = 1):
        self.id: str = str(uuid.uuid4())
        self.name: str = name
        self.entity_type: EntityType = entity_type
        self.level: int = level
        
        # Core stats - using a dictionary for flexibility
        self.stats: Dict[StatType, int] = {
            StatType.HEALTH: 100,
            StatType.MAX_HEALTH: 100,
            StatType.MANA: 50,
            StatType.MAX_MANA: 50,
            StatType.ATTACK: 10,
            StatType.DEFENSE: 5,
            StatType.SPEED: 10,
            StatType.EXPERIENCE: 0
        }
        
        # Status effects and modifiers
        self.status_effects: List['Effect'] = []
        self.temporary_modifiers: Dict[StatType, int] = {}
        
        # Combat state
        self.is_alive: bool = True
        self.is_stunned: bool = False
        self.is_defending: bool = False
        
        # Initialize entity-specific stats
        self._initialize_stats()
    
    @abstractmethod
    def _initialize_stats(self) -> None:
        """Initialize entity-specific base stats. Must be implemented by subclasses."""
        pass
    
    def get_stat(self, stat_type: StatType) -> int:
        """Get a stat value including temporary modifiers"""
        base_value = self.stats.get(stat_type, 0)
        modifier = self.temporary_modifiers.get(stat_type, 0)
        return max(0, base_value + modifier)
    
    def set_stat(self, stat_type: StatType, value: int) -> None:
        """Set a stat value"""
        self.stats[stat_type] = max(0, value)
    
    def modify_stat(self, stat_type: StatType, amount: int) -> None:
        """Modify a stat by a certain amount"""
        current_value = self.get_stat(stat_type)
        self.set_stat(stat_type, current_value + amount)
    
    def add_temporary_modifier(self, stat_type: StatType, amount: int) -> None:
        """Add a temporary modifier to a stat"""
        current_modifier = self.temporary_modifiers.get(stat_type, 0)
        self.temporary_modifiers[stat_type] = current_modifier + amount
    
    def remove_temporary_modifier(self, stat_type: StatType, amount: int) -> None:
        """Remove a temporary modifier from a stat"""
        current_modifier = self.temporary_modifiers.get(stat_type, 0)
        self.temporary_modifiers[stat_type] = max(0, current_modifier - amount)
    
    def take_damage(self, damage: int) -> int:
        """Take damage and return actual damage taken"""
        if not self.is_alive:
            return 0
        
        # Calculate actual damage after defense
        defense = self.get_stat(StatType.DEFENSE)
        actual_damage = max(1, damage - defense)
        
        # Apply damage
        current_health = self.get_stat(StatType.HEALTH)
        new_health = max(0, current_health - actual_damage)
        self.set_stat(StatType.HEALTH, new_health)
        
        # Check if entity died
        if new_health == 0:
            self.is_alive = False
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal the entity and return actual healing done"""
        if not self.is_alive:
            return 0
        
        current_health = self.get_stat(StatType.HEALTH)
        max_health = self.get_stat(StatType.MAX_HEALTH)
        actual_healing = min(amount, max_health - current_health)
        
        self.set_stat(StatType.HEALTH, current_health + actual_healing)
        return actual_healing
    
    def restore_mana(self, amount: int) -> int:
        """Restore mana and return actual mana restored"""
        current_mana = self.get_stat(StatType.MANA)
        max_mana = self.get_stat(StatType.MAX_MANA)
        actual_restoration = min(amount, max_mana - current_mana)
        
        self.set_stat(StatType.MANA, current_mana + actual_restoration)
        return actual_restoration
    
    def add_experience(self, amount: int) -> bool:
        """Add experience and return True if leveled up"""
        current_exp = self.get_stat(StatType.EXPERIENCE)
        self.set_stat(StatType.EXPERIENCE, current_exp + amount)
        
        # Check for level up (simple formula for MVP)
        exp_needed = self.level * 100
        if current_exp + amount >= exp_needed:
            self.level_up()
            return True
        return False
    
    def level_up(self) -> None:
        """Level up the entity"""
        self.level += 1
        # Restore health and mana on level up
        self.set_stat(StatType.HEALTH, self.get_stat(StatType.MAX_HEALTH))
        self.set_stat(StatType.MANA, self.get_stat(StatType.MAX_MANA))
        
        # Apply level up bonuses (to be implemented by subclasses)
        self._apply_level_up_bonuses()
    
    @abstractmethod
    def _apply_level_up_bonuses(self) -> None:
        """Apply level up bonuses. Must be implemented by subclasses."""
        pass
    
    def add_status_effect(self, effect: 'Effect') -> None:
        """Add a status effect to the entity"""
        self.status_effects.append(effect)
    
    def remove_status_effect(self, effect: 'Effect') -> None:
        """Remove a status effect from the entity"""
        if effect in self.status_effects:
            self.status_effects.remove(effect)
    
    def process_status_effects(self) -> None:
        """Process all active status effects"""
        effects_to_remove = []
        
        for effect in self.status_effects:
            effect.apply(self)
            effect.duration -= 1
            
            if effect.duration <= 0:
                effects_to_remove.append(effect)
        
        # Remove expired effects
        for effect in effects_to_remove:
            self.remove_status_effect(effect)
    
    def reset_combat_state(self) -> None:
        """Reset combat-specific state"""
        self.is_stunned = False
        self.is_defending = False
        self.temporary_modifiers.clear()
    
    def get_health_percentage(self) -> float:
        """Get current health as a percentage"""
        current_health = self.get_stat(StatType.HEALTH)
        max_health = self.get_stat(StatType.MAX_HEALTH)
        return (current_health / max_health) * 100 if max_health > 0 else 0
    
    def get_mana_percentage(self) -> float:
        """Get current mana as a percentage"""
        current_mana = self.get_stat(StatType.MANA)
        max_mana = self.get_stat(StatType.MAX_MANA)
        return (current_mana / max_mana) * 100 if max_mana > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'entity_type': self.entity_type.value,
            'level': self.level,
            'stats': {stat.value: value for stat, value in self.stats.items()},
            'is_alive': self.is_alive,
            'status_effects': [effect.to_dict() for effect in self.status_effects]
        }
    
    def __str__(self) -> str:
        """String representation of the entity"""
        health_pct = self.get_health_percentage()
        return f"{self.name} (Lv.{self.level}) - HP: {self.get_stat(StatType.HEALTH)}/{self.get_stat(StatType.MAX_HEALTH)} ({health_pct:.1f}%)"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"Entity(name='{self.name}', type={self.entity_type.value}, level={self.level}, alive={self.is_alive})"
