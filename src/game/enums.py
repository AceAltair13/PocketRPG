"""
Consolidated enums for PocketRPG
Contains all game-related enums in one place to reduce duplication
"""

from enum import Enum


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


class PlayerClass(Enum):
    """Available player classes"""
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    CLERIC = "cleric"


class EnemyType(Enum):
    """Types of enemies"""
    NORMAL = "normal"
    ELITE = "elite"
    BOSS = "boss"
    MINIBOSS = "miniboss"


class EnemyBehavior(Enum):
    """AI behavior patterns for enemies"""
    AGGRESSIVE = "aggressive"  # Always attacks
    DEFENSIVE = "defensive"    # Prefers to defend
    BALANCED = "balanced"      # Mix of attack and defend
    HEALER = "healer"         # Focuses on healing
    SPELLCASTER = "spellcaster"  # Prefers magic attacks


class ItemType(Enum):
    """Types of items"""
    CONSUMABLE = "consumable"    # Potions, food, etc.
    WEAPON = "weapon"           # Swords, staffs, etc.
    ARMOR = "armor"             # Helmets, chest pieces, etc.
    ACCESSORY = "accessory"     # Rings, amulets, etc.
    QUEST = "quest"             # Quest-specific items
    MATERIAL = "material"       # Crafting materials
    MISC = "misc"               # Miscellaneous items


class ItemRarity(Enum):
    """Item rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class ItemQuality(Enum):
    """Item quality levels"""
    POOR = "poor"
    NORMAL = "normal"
    GOOD = "good"
    EXCELLENT = "excellent"
    PERFECT = "perfect"


class EquipmentSlot(Enum):
    """Available equipment slots"""
    WEAPON = "weapon"
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    HANDS = "hands"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    NECKLACE = "necklace"
    ACCESSORY = "accessory"


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


class CombatAction(Enum):
    """Available combat actions"""
    ATTACK = "attack"
    DEFEND = "defend"
    USE_ITEM = "use_item"
    FLEE = "flee"
    SPECIAL_ABILITY = "special_ability"


class CombatResult(Enum):
    """Possible combat results"""
    VICTORY = "victory"
    DEFEAT = "defeat"
    FLEE = "flee"
    ONGOING = "ongoing"
