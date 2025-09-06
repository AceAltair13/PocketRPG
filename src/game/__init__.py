"""
Game logic and mechanics for PocketRPG
"""

# Import main classes for easy access
from .entities import Entity, Player, Enemy
from .items import Item, Inventory, Equipment, CommonItems
from .systems import Effect, Combat, CommonEffects
from .examples import create_example_player, create_example_enemy, run_example_combat
from .enums import (
    EntityType, StatType, PlayerClass, EnemyType, EnemyBehavior,
    ItemType, ItemRarity, ItemQuality, EquipmentSlot,
    EffectType, EffectTarget, CombatAction, CombatResult
)

__all__ = [
    # Entities
    'Entity', 'Player', 'Enemy',
    # Items
    'Item', 'Inventory', 'Equipment', 'CommonItems',
    # Systems
    'Effect', 'Combat', 'CommonEffects',
    # Examples
    'create_example_player', 'create_example_enemy', 'run_example_combat',
    # Enums
    'EntityType', 'StatType', 'PlayerClass', 'EnemyType', 'EnemyBehavior',
    'ItemType', 'ItemRarity', 'ItemQuality', 'EquipmentSlot',
    'EffectType', 'EffectTarget', 'CombatAction', 'CombatResult'
]
