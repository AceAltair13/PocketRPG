"""
Systems module for PocketRPG
Contains game systems like combat, effects, and other mechanics
"""

from .effect import (
    Effect, EffectType, EffectTarget,
    StatModifierEffect, DamageOverTimeEffect, HealOverTimeEffect,
    StatusEffect, CustomEffect, CommonEffects
)
from .combat import Combat, CombatAction, CombatResult, CombatTurn

__all__ = [
    'Effect', 'EffectType', 'EffectTarget',
    'StatModifierEffect', 'DamageOverTimeEffect', 'HealOverTimeEffect',
    'StatusEffect', 'CustomEffect', 'CommonEffects',
    'Combat', 'CombatAction', 'CombatResult', 'CombatTurn'
]
