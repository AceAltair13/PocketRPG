"""
Item class hierarchy for all items in the RPG
Includes consumables, equipment, and quest items
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from ..enums import ItemType, ItemRarity, ItemQuality
from ..utils.serialization import SerializableMixin
from ..utils.string_representation import StringRepresentationMixin
from ..utils.stat_utils import StatUtils


class Item(ABC, SerializableMixin, StringRepresentationMixin):
    """
    Base class for all items in the game.
    Provides common functionality for all item types.
    """
    
    def __init__(self, name: str, item_type: ItemType, description: str = "",
                 rarity: ItemRarity = ItemRarity.COMMON, quality: ItemQuality = ItemQuality.NORMAL,
                 value: int = 0, stackable: bool = False, max_stack: int = 1):
        self.name: str = name
        self.item_type: ItemType = item_type
        self.description: str = description
        self.rarity: ItemRarity = rarity
        self.quality: ItemQuality = quality
        self.value: int = value
        self.stackable: bool = stackable
        self.max_stack: int = max_stack
        self.quantity: int = 1
        
        # Item properties
        self.level_requirement: int = 1
        self.class_requirement: Optional[str] = None  # Player class requirement
        self.unique: bool = False  # Unique items cannot be duplicated
    
    @abstractmethod
    def use(self, user) -> bool:
        """
        Use the item. Returns True if successful.
        Must be implemented by subclasses.
        """
        pass
    
    def can_use(self, user) -> bool:
        """Check if the user can use this item"""
        # Check level requirement
        if hasattr(user, 'level') and user.level < self.level_requirement:
            return False
        
        # Check class requirement
        if self.class_requirement and hasattr(user, 'player_class'):
            if user.player_class.value != self.class_requirement:
                return False
        
        return True
    
    def get_display_name(self) -> str:
        """Get the display name with quality and rarity indicators"""
        quality_prefix = {
            ItemQuality.POOR: "[Poor] ",
            ItemQuality.NORMAL: "",
            ItemQuality.GOOD: "[Good] ",
            ItemQuality.EXCELLENT: "[Excellent] ",
            ItemQuality.PERFECT: "[Perfect] "
        }
        
        rarity_color = {
            ItemRarity.COMMON: "",
            ItemRarity.UNCOMMON: "**",
            ItemRarity.RARE: "***",
            ItemRarity.EPIC: "****",
            ItemRarity.LEGENDARY: "*****"
        }
        
        prefix = quality_prefix.get(self.quality, "")
        suffix = rarity_color.get(self.rarity, "")
        
        return f"{prefix}{self.name}{suffix}"
    
    def get_full_description(self) -> str:
        """Get the full description including all item details"""
        desc = f"{self.get_display_name()}\n"
        desc += f"Type: {self.item_type.value.title()}\n"
        desc += f"Rarity: {self.rarity.value.title()}\n"
        desc += f"Quality: {self.quality.value.title()}\n"
        desc += f"Value: {self.value} gold\n"
        
        if self.level_requirement > 1:
            desc += f"Level Required: {self.level_requirement}\n"
        
        if self.class_requirement:
            desc += f"Class Required: {self.class_requirement.title()}\n"
        
        if self.description:
            desc += f"\n{self.description}\n"
        
        return desc
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for serialization"""
        return {
            'name': self.name,
            'item_type': self.item_type.value,
            'description': self.description,
            'rarity': self.rarity.value,
            'quality': self.quality.value,
            'value': self.value,
            'stackable': self.stackable,
            'max_stack': self.max_stack,
            'quantity': self.quantity,
            'level_requirement': self.level_requirement,
            'class_requirement': self.class_requirement,
            'unique': self.unique
        }
    
    def __str__(self) -> str:
        """String representation of the item"""
        if self.quantity > 1:
            return f"{self.get_display_name()} x{self.quantity}"
        return self.get_display_name()
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"Item(name='{self.name}', type={self.item_type.value}, rarity={self.rarity.value})"


class ConsumableItem(Item):
    """
    Items that can be consumed for immediate effects
    """
    
    def __init__(self, name: str, description: str = "", rarity: ItemRarity = ItemRarity.COMMON,
                 quality: ItemQuality = ItemQuality.NORMAL, value: int = 0, max_stack: int = 99):
        super().__init__(name, ItemType.CONSUMABLE, description, rarity, quality, value, True, max_stack)
        
        # Consumable-specific properties
        self.effects: List[Dict[str, Any]] = []  # List of effects to apply
        self.cooldown: int = 0  # Cooldown in turns before can be used again
    
    def use(self, user) -> bool:
        """Use the consumable item"""
        if not self.can_use(user):
            return False
        
        if self.quantity <= 0:
            return False
        
        # Apply all effects
        for effect_data in self.effects:
            self._apply_effect(user, effect_data)
        
        # Consume the item
        self.quantity -= 1
        
        return True
    
    def _apply_effect(self, user, effect_data: Dict[str, Any]) -> None:
        """Apply a specific effect to the user"""
        effect_type = effect_data.get('type', 'heal')
        
        if effect_type == 'heal':
            amount = effect_data.get('amount', 0)
            user.heal(amount)
        elif effect_type == 'mana_restore':
            amount = effect_data.get('amount', 0)
            user.restore_mana(amount)
        elif effect_type == 'stat_boost':
            stat = effect_data.get('stat', 'attack')
            amount = effect_data.get('amount', 0)
            duration = effect_data.get('duration', 3)
            # Create and apply stat boost effect
            from .effect import StatModifierEffect, EffectType
            effect = StatModifierEffect(
                name=f"{self.name} Boost",
                effect_type=EffectType.BUFF,
                duration=duration,
                stat_modifiers={stat: amount}
            )
            user.add_status_effect(effect)
    
    def add_effect(self, effect_type: str, amount: int, duration: int = 0, stat: str = "") -> None:
        """Add an effect to this consumable"""
        effect_data = {
            'type': effect_type,
            'amount': amount,
            'duration': duration,
            'stat': stat
        }
        self.effects.append(effect_data)


class EquipmentItem(Item):
    """
    Items that can be equipped to provide stat bonuses
    """
    
    def __init__(self, name: str, item_type: ItemType, description: str = "",
                 rarity: ItemRarity = ItemRarity.COMMON, quality: ItemQuality = ItemQuality.NORMAL,
                 value: int = 0, level_requirement: int = 1):
        super().__init__(name, item_type, description, rarity, quality, value, False, 1)
        self.level_requirement = level_requirement
        
        # Equipment-specific properties
        self.stat_bonuses: Dict[str, int] = {}  # Stat bonuses provided
        self.durability: int = 100
        self.max_durability: int = 100
        self.slot: Optional[str] = None  # Equipment slot (head, chest, weapon, etc.)
    
    def use(self, user) -> bool:
        """Equip the item"""
        if not self.can_use(user):
            return False
        
        # Equipment items are equipped, not consumed
        # This would typically be handled by the equipment system
        return True
    
    def get_stat_bonuses(self) -> Dict[str, int]:
        """Get the stat bonuses provided by this equipment"""
        return self.stat_bonuses.copy()
    
    def add_stat_bonus(self, stat: str, bonus: int) -> None:
        """Add a stat bonus to this equipment"""
        self.stat_bonuses[stat] = self.stat_bonuses.get(stat, 0) + bonus
    
    def repair(self, amount: int = None) -> None:
        """Repair the equipment"""
        if amount is None:
            self.durability = self.max_durability
        else:
            self.durability = min(self.max_durability, self.durability + amount)
    
    def damage(self, amount: int = 1) -> None:
        """Damage the equipment"""
        self.durability = max(0, self.durability - amount)
    
    def is_broken(self) -> bool:
        """Check if the equipment is broken"""
        return self.durability <= 0


class WeaponItem(EquipmentItem):
    """
    Weapons that can be equipped
    """
    
    def __init__(self, name: str, description: str = "", rarity: ItemRarity = ItemRarity.COMMON,
                 quality: ItemQuality = ItemQuality.NORMAL, value: int = 0, level_requirement: int = 1):
        super().__init__(name, ItemType.WEAPON, description, rarity, quality, value, level_requirement)
        self.slot = "weapon"
        
        # Weapon-specific properties
        self.damage: int = 0
        self.damage_type: str = "physical"
        self.weapon_type: str = "sword"  # sword, staff, bow, etc.
        self.critical_chance: float = 0.05  # 5% base crit chance
        self.critical_multiplier: float = 2.0
    
    def get_damage_range(self) -> tuple:
        """Get the damage range for this weapon"""
        base_damage = self.damage
        quality_multiplier = {
            ItemQuality.POOR: 0.8,
            ItemQuality.NORMAL: 1.0,
            ItemQuality.GOOD: 1.2,
            ItemQuality.EXCELLENT: 1.4,
            ItemQuality.PERFECT: 1.6
        }
        
        multiplier = quality_multiplier.get(self.quality, 1.0)
        min_damage = int(base_damage * multiplier * 0.9)
        max_damage = int(base_damage * multiplier * 1.1)
        
        return (min_damage, max_damage)


class ArmorItem(EquipmentItem):
    """
    Armor pieces that can be equipped
    """
    
    def __init__(self, name: str, armor_type: str, description: str = "",
                 rarity: ItemRarity = ItemRarity.COMMON, quality: ItemQuality = ItemQuality.NORMAL,
                 value: int = 0, level_requirement: int = 1):
        super().__init__(name, ItemType.ARMOR, description, rarity, quality, value, level_requirement)
        self.slot = armor_type
        
        # Armor-specific properties
        self.armor_type: str = armor_type  # head, chest, legs, feet, etc.
        self.defense: int = 0
        self.resistances: Dict[str, float] = {}  # Damage type resistances
    
    def get_defense_value(self) -> int:
        """Get the defense value including quality bonuses"""
        quality_multiplier = {
            ItemQuality.POOR: 0.8,
            ItemQuality.NORMAL: 1.0,
            ItemQuality.GOOD: 1.2,
            ItemQuality.EXCELLENT: 1.4,
            ItemQuality.PERFECT: 1.6
        }
        
        multiplier = quality_multiplier.get(self.quality, 1.0)
        return int(self.defense * multiplier)


class QuestItem(Item):
    """
    Items used for quests and story progression
    """
    
    def __init__(self, name: str, description: str = "", quest_id: str = ""):
        super().__init__(name, ItemType.QUEST, description, ItemRarity.COMMON, ItemQuality.NORMAL, 0, False, 1)
        self.quest_id: str = quest_id
        self.unique = True  # Quest items are typically unique
    
    def use(self, user) -> bool:
        """Quest items typically cannot be used directly"""
        return False


# Predefined common items
class CommonItems:
    """Collection of commonly used items"""
    
    @staticmethod
    def health_potion(quality: ItemQuality = ItemQuality.NORMAL) -> ConsumableItem:
        """Create a health potion"""
        potion = ConsumableItem(
            name="Health Potion",
            description="Restores health when consumed",
            rarity=ItemRarity.COMMON,
            quality=quality,
            value=10,
            max_stack=99
        )
        potion.add_effect('heal', 50)
        return potion
    
    @staticmethod
    def mana_potion(quality: ItemQuality = ItemQuality.NORMAL) -> ConsumableItem:
        """Create a mana potion"""
        potion = ConsumableItem(
            name="Mana Potion",
            description="Restores mana when consumed",
            rarity=ItemRarity.COMMON,
            quality=quality,
            value=10,
            max_stack=99
        )
        potion.add_effect('mana_restore', 30)
        return potion
    
    @staticmethod
    def iron_sword(quality: ItemQuality = ItemQuality.NORMAL) -> WeaponItem:
        """Create an iron sword"""
        sword = WeaponItem(
            name="Iron Sword",
            description="A sturdy iron sword",
            rarity=ItemRarity.COMMON,
            quality=quality,
            value=50,
            level_requirement=1
        )
        sword.damage = 15
        sword.add_stat_bonus('attack', 5)
        return sword
    
    @staticmethod
    def leather_armor(quality: ItemQuality = ItemQuality.NORMAL) -> ArmorItem:
        """Create leather armor"""
        armor = ArmorItem(
            name="Leather Armor",
            description="Basic leather armor",
            armor_type="chest",
            rarity=ItemRarity.COMMON,
            quality=quality,
            value=30,
            level_requirement=1
        )
        armor.defense = 8
        armor.add_stat_bonus('defense', 3)
        return armor
