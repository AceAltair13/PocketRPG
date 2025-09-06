"""
Game logic and mechanics for PocketRPG
"""

# Import main classes for easy access
from .entities import Entity, Player, Enemy, EntityType, StatType, PlayerClass, EnemyType, EnemyBehavior
from .items import Item, Inventory, Equipment, ItemType, ItemRarity, ItemQuality, CommonItems
from .systems import Effect, Combat, EffectType, CombatAction, CombatResult, CommonEffects
from .examples import create_example_player, create_example_enemy, run_example_combat

__all__ = [
    # Entities
    'Entity', 'Player', 'Enemy', 'EntityType', 'StatType', 'PlayerClass', 'EnemyType', 'EnemyBehavior',
    # Items
    'Item', 'Inventory', 'Equipment', 'ItemType', 'ItemRarity', 'ItemQuality', 'CommonItems',
    # Systems
    'Effect', 'Combat', 'EffectType', 'CombatAction', 'CombatResult', 'CommonEffects',
    # Examples
    'create_example_player', 'create_example_enemy', 'run_example_combat'
]
