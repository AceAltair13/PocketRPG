"""
Effect class for status effects, buffs, and debuffs in the RPG
Handles temporary modifications to entity stats and behaviors
"""

from typing import Dict, Any, Optional, Callable
from enum import Enum
from abc import ABC, abstractmethod


class EffectType(Enum):
    """Types of effects"""
    BUFF = "buff"           # Positive effect
    DEBUFF = "debuff"       # Negative effect
    DOT = "dot"            # Damage over time
    HOT = "hot"            # Heal over time
    STATUS = "status"      # Status condition (stun, poison, etc.)


class EffectTarget(Enum):
    """What the effect targets"""
    SELF = "self"          # Affects the entity that has the effect
    ENEMY = "enemy"        # Affects enemies
    ALLY = "ally"          # Affects allies
    ALL = "all"           # Affects everyone


class Effect(ABC):
    """
    Base class for all status effects, buffs, and debuffs.
    Effects can modify stats, deal damage, heal, or change behavior.
    """
    
    def __init__(self, name: str, effect_type: EffectType, duration: int, 
                 description: str = "", target: EffectTarget = EffectTarget.SELF):
        self.name: str = name
        self.effect_type: EffectType = effect_type
        self.duration: int = duration
        self.max_duration: int = duration
        self.description: str = description
        self.target: EffectTarget = target
        
        # Effect properties
        self.is_stackable: bool = False
        self.can_be_dispelled: bool = True
        self.is_hidden: bool = False  # Hidden effects don't show in UI
        
        # Effect data
        self.data: Dict[str, Any] = {}
    
    @abstractmethod
    def apply(self, entity) -> None:
        """Apply the effect to an entity. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def remove(self, entity) -> None:
        """Remove the effect from an entity. Must be implemented by subclasses."""
        pass
    
    def tick(self, entity) -> None:
        """Called each turn while the effect is active"""
        pass
    
    def can_stack_with(self, other_effect: 'Effect') -> bool:
        """Check if this effect can stack with another effect"""
        if not self.is_stackable or not other_effect.is_stackable:
            return False
        return self.name == other_effect.name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert effect to dictionary for serialization"""
        return {
            'name': self.name,
            'effect_type': self.effect_type.value,
            'duration': self.duration,
            'max_duration': self.max_duration,
            'description': self.description,
            'target': self.target.value,
            'is_stackable': self.is_stackable,
            'can_be_dispelled': self.can_be_dispelled,
            'data': self.data
        }


class StatModifierEffect(Effect):
    """
    Effect that modifies entity stats (buffs/debuffs)
    """
    
    def __init__(self, name: str, effect_type: EffectType, duration: int,
                 stat_modifiers: Dict[str, int], description: str = ""):
        super().__init__(name, effect_type, duration, description)
        self.stat_modifiers: Dict[str, int] = stat_modifiers
    
    def apply(self, entity) -> None:
        """Apply stat modifications to the entity"""
        from ..entities.entity import StatType
        
        for stat_name, modifier in self.stat_modifiers.items():
            try:
                stat_type = StatType(stat_name)
                entity.add_temporary_modifier(stat_type, modifier)
            except ValueError:
                # Handle custom stats if needed
                pass
    
    def remove(self, entity) -> None:
        """Remove stat modifications from the entity"""
        from ..entities.entity import StatType
        
        for stat_name, modifier in self.stat_modifiers.items():
            try:
                stat_type = StatType(stat_name)
                entity.remove_temporary_modifier(stat_type, modifier)
            except ValueError:
                # Handle custom stats if needed
                pass


class DamageOverTimeEffect(Effect):
    """
    Effect that deals damage over time
    """
    
    def __init__(self, name: str, duration: int, damage_per_tick: int, 
                 damage_type: str = "physical", description: str = ""):
        super().__init__(name, EffectType.DOT, duration, description)
        self.damage_per_tick: int = damage_per_tick
        self.damage_type: str = damage_type
    
    def apply(self, entity) -> None:
        """Apply DOT effect"""
        pass  # DOT effects are handled in tick()
    
    def remove(self, entity) -> None:
        """Remove DOT effect"""
        pass  # No cleanup needed for DOT
    
    def tick(self, entity) -> None:
        """Deal damage each turn"""
        if entity.is_alive:
            damage = self.damage_per_tick
            # Could add damage type resistance here
            actual_damage = entity.take_damage(damage)
            self.data['total_damage_dealt'] = self.data.get('total_damage_dealt', 0) + actual_damage


class HealOverTimeEffect(Effect):
    """
    Effect that heals over time
    """
    
    def __init__(self, name: str, duration: int, heal_per_tick: int, description: str = ""):
        super().__init__(name, EffectType.HOT, duration, description)
        self.heal_per_tick: int = heal_per_tick
    
    def apply(self, entity) -> None:
        """Apply HOT effect"""
        pass  # HOT effects are handled in tick()
    
    def remove(self, entity) -> None:
        """Remove HOT effect"""
        pass  # No cleanup needed for HOT
    
    def tick(self, entity) -> None:
        """Heal each turn"""
        if entity.is_alive:
            actual_healing = entity.heal(self.heal_per_tick)
            self.data['total_healing_done'] = self.data.get('total_healing_done', 0) + actual_healing


class StatusEffect(Effect):
    """
    Effect that changes entity behavior or status
    """
    
    def __init__(self, name: str, duration: int, status_changes: Dict[str, Any], 
                 description: str = ""):
        super().__init__(name, EffectType.STATUS, duration, description)
        self.status_changes: Dict[str, Any] = status_changes
        self.original_values: Dict[str, Any] = {}
    
    def apply(self, entity) -> None:
        """Apply status changes to the entity"""
        # Store original values
        for status, value in self.status_changes.items():
            if hasattr(entity, status):
                self.original_values[status] = getattr(entity, status)
                setattr(entity, status, value)
    
    def remove(self, entity) -> None:
        """Restore original status values"""
        for status, original_value in self.original_values.items():
            if hasattr(entity, status):
                setattr(entity, status, original_value)


class CustomEffect(Effect):
    """
    Effect with custom behavior defined by functions
    """
    
    def __init__(self, name: str, effect_type: EffectType, duration: int,
                 apply_func: Optional[Callable] = None, remove_func: Optional[Callable] = None,
                 tick_func: Optional[Callable] = None, description: str = ""):
        super().__init__(name, effect_type, duration, description)
        self.apply_func: Optional[Callable] = apply_func
        self.remove_func: Optional[Callable] = remove_func
        self.tick_func: Optional[Callable] = tick_func
    
    def apply(self, entity) -> None:
        """Apply custom effect"""
        if self.apply_func:
            self.apply_func(entity, self)
    
    def remove(self, entity) -> None:
        """Remove custom effect"""
        if self.remove_func:
            self.remove_func(entity, self)
    
    def tick(self, entity) -> None:
        """Custom tick behavior"""
        if self.tick_func:
            self.tick_func(entity, self)


# Predefined common effects
class CommonEffects:
    """Collection of commonly used effects"""
    
    @staticmethod
    def strength_buff(duration: int = 3, power: int = 5) -> StatModifierEffect:
        """Create a strength buff effect"""
        return StatModifierEffect(
            name="Strength Buff",
            effect_type=EffectType.BUFF,
            duration=duration,
            stat_modifiers={"attack": power},
            description=f"Increases attack power by {power} for {duration} turns"
        )
    
    @staticmethod
    def weakness_debuff(duration: int = 3, power: int = 3) -> StatModifierEffect:
        """Create a weakness debuff effect"""
        return StatModifierEffect(
            name="Weakness",
            effect_type=EffectType.DEBUFF,
            duration=duration,
            stat_modifiers={"attack": -power},
            description=f"Reduces attack power by {power} for {duration} turns"
        )
    
    @staticmethod
    def poison(duration: int = 5, damage: int = 3) -> DamageOverTimeEffect:
        """Create a poison DOT effect"""
        return DamageOverTimeEffect(
            name="Poison",
            duration=duration,
            damage_per_tick=damage,
            damage_type="poison",
            description=f"Deals {damage} poison damage per turn for {duration} turns"
        )
    
    @staticmethod
    def regeneration(duration: int = 5, healing: int = 5) -> HealOverTimeEffect:
        """Create a regeneration HOT effect"""
        return HealOverTimeEffect(
            name="Regeneration",
            duration=duration,
            heal_per_tick=healing,
            description=f"Heals {healing} HP per turn for {duration} turns"
        )
    
    @staticmethod
    def stun(duration: int = 1) -> StatusEffect:
        """Create a stun status effect"""
        return StatusEffect(
            name="Stunned",
            effect_type=EffectType.STATUS,
            duration=duration,
            status_changes={"is_stunned": True},
            description=f"Unable to act for {duration} turn(s)"
        )
    
    @staticmethod
    def shield(duration: int = 3, defense_bonus: int = 10) -> StatModifierEffect:
        """Create a shield buff effect"""
        return StatModifierEffect(
            name="Shield",
            effect_type=EffectType.BUFF,
            duration=duration,
            stat_modifiers={"defense": defense_bonus},
            description=f"Increases defense by {defense_bonus} for {duration} turns"
        )
