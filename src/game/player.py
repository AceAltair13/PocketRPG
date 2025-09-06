"""
Player class for user-controlled characters in the RPG
Inherits from Entity and adds player-specific functionality
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from .entity import Entity, EntityType, StatType
from .inventory import Inventory
from .equipment import Equipment


class PlayerClass(Enum):
    """Available player classes"""
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    CLERIC = "cleric"


class Player(Entity):
    """
    Player class representing user-controlled characters.
    Extends Entity with player-specific features like inventory, equipment, and class bonuses.
    """
    
    def __init__(self, name: str, player_class: PlayerClass, level: int = 1):
        # Initialize as player entity type
        super().__init__(name, EntityType.PLAYER, level)
        
        self.player_class: PlayerClass = player_class
        self.user_id: Optional[int] = None  # Discord user ID
        self.gold: int = 0
        
        # Player-specific systems
        self.inventory: Inventory = Inventory()
        self.equipment: Equipment = Equipment()
        
        # Player progression
        self.skill_points: int = 0
        self.available_skills: List[str] = []
        self.learned_skills: List[str] = []
        
        # Initialize class-specific stats
        self._initialize_class_stats()
    
    def _initialize_stats(self) -> None:
        """Initialize base player stats"""
        # Base stats for all players
        self.stats.update({
            StatType.HEALTH: 120,
            StatType.MAX_HEALTH: 120,
            StatType.MANA: 60,
            StatType.MAX_MANA: 60,
            StatType.ATTACK: 12,
            StatType.DEFENSE: 8,
            StatType.SPEED: 10,
            StatType.EXPERIENCE: 0
        })
    
    def _initialize_class_stats(self) -> None:
        """Initialize class-specific stat bonuses"""
        class_bonuses = {
            PlayerClass.WARRIOR: {
                StatType.HEALTH: 30,
                StatType.MAX_HEALTH: 30,
                StatType.ATTACK: 5,
                StatType.DEFENSE: 3
            },
            PlayerClass.MAGE: {
                StatType.MANA: 40,
                StatType.MAX_MANA: 40,
                StatType.ATTACK: 3,
                StatType.SPEED: 2
            },
            PlayerClass.ROGUE: {
                StatType.SPEED: 5,
                StatType.ATTACK: 4,
                StatType.DEFENSE: 1
            },
            PlayerClass.CLERIC: {
                StatType.HEALTH: 20,
                StatType.MAX_HEALTH: 20,
                StatType.MANA: 30,
                StatType.MAX_MANA: 30,
                StatType.DEFENSE: 2
            }
        }
        
        # Apply class bonuses
        bonuses = class_bonuses.get(self.player_class, {})
        for stat, bonus in bonuses.items():
            current_value = self.get_stat(stat)
            self.set_stat(stat, current_value + bonus)
    
    def _apply_level_up_bonuses(self) -> None:
        """Apply level up bonuses based on player class"""
        # Base level up bonuses
        self.modify_stat(StatType.MAX_HEALTH, 10)
        self.modify_stat(StatType.MAX_MANA, 5)
        self.modify_stat(StatType.ATTACK, 2)
        self.modify_stat(StatType.DEFENSE, 1)
        self.modify_stat(StatType.SPEED, 1)
        
        # Class-specific bonuses
        class_bonuses = {
            PlayerClass.WARRIOR: {
                StatType.MAX_HEALTH: 15,
                StatType.ATTACK: 3,
                StatType.DEFENSE: 2
            },
            PlayerClass.MAGE: {
                StatType.MAX_MANA: 10,
                StatType.ATTACK: 3,
                StatType.SPEED: 1
            },
            PlayerClass.ROGUE: {
                StatType.ATTACK: 4,
                StatType.SPEED: 2,
                StatType.DEFENSE: 1
            },
            PlayerClass.CLERIC: {
                StatType.MAX_HEALTH: 12,
                StatType.MAX_MANA: 8,
                StatType.DEFENSE: 2
            }
        }
        
        bonuses = class_bonuses.get(self.player_class, {})
        for stat, bonus in bonuses.items():
            self.modify_stat(stat, bonus)
        
        # Gain skill points
        self.skill_points += 1
    
    def set_user_id(self, user_id: int) -> None:
        """Set the Discord user ID for this player"""
        self.user_id = user_id
    
    def add_gold(self, amount: int) -> None:
        """Add gold to player's inventory"""
        self.gold = max(0, self.gold + amount)
    
    def spend_gold(self, amount: int) -> bool:
        """Spend gold, return True if successful"""
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    
    def get_effective_stats(self) -> Dict[StatType, int]:
        """Get stats including equipment bonuses"""
        base_stats = {stat: self.get_stat(stat) for stat in StatType}
        
        # Add equipment bonuses
        equipment_bonuses = self.equipment.get_total_bonuses()
        for stat, bonus in equipment_bonuses.items():
            if stat in base_stats:
                base_stats[stat] += bonus
        
        return base_stats
    
    def can_use_item(self, item) -> bool:
        """Check if player can use a specific item"""
        # Check level requirement
        if hasattr(item, 'level_requirement') and self.level < item.level_requirement:
            return False
        
        # Check class requirement
        if hasattr(item, 'class_requirement') and item.class_requirement != self.player_class:
            return False
        
        return True
    
    def learn_skill(self, skill_name: str) -> bool:
        """Learn a new skill if requirements are met"""
        if skill_name in self.learned_skills:
            return False  # Already learned
        
        if skill_name not in self.available_skills:
            return False  # Not available
        
        # Check if player has enough skill points
        skill_cost = self._get_skill_cost(skill_name)
        if self.skill_points < skill_cost:
            return False
        
        self.skill_points -= skill_cost
        self.learned_skills.append(skill_name)
        return True
    
    def _get_skill_cost(self, skill_name: str) -> int:
        """Get the cost to learn a skill"""
        # Simple cost calculation for MVP
        return 1
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions for the player"""
        actions = ["attack", "defend", "use_item", "flee"]
        
        # Add class-specific actions
        if self.player_class == PlayerClass.MAGE:
            actions.extend(["cast_spell", "meditate"])
        elif self.player_class == PlayerClass.CLERIC:
            actions.extend(["heal", "bless"])
        elif self.player_class == PlayerClass.ROGUE:
            actions.extend(["sneak_attack", "dodge"])
        elif self.player_class == PlayerClass.WARRIOR:
            actions.extend(["berserker_rage", "shield_bash"])
        
        return actions
    
    def get_class_description(self) -> str:
        """Get description of the player's class"""
        descriptions = {
            PlayerClass.WARRIOR: "A strong melee fighter with high health and attack power.",
            PlayerClass.MAGE: "A spellcaster with powerful magic but lower physical stats.",
            PlayerClass.ROGUE: "A nimble fighter with high speed and critical hit potential.",
            PlayerClass.CLERIC: "A support class with healing abilities and balanced stats."
        }
        return descriptions.get(self.player_class, "Unknown class")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for serialization"""
        base_dict = super().to_dict()
        base_dict.update({
            'player_class': self.player_class.value,
            'user_id': self.user_id,
            'gold': self.gold,
            'skill_points': self.skill_points,
            'learned_skills': self.learned_skills,
            'inventory': self.inventory.to_dict(),
            'equipment': self.equipment.to_dict()
        })
        return base_dict
    
    def __str__(self) -> str:
        """String representation of the player"""
        class_name = self.player_class.value.title()
        return f"{self.name} the {class_name} (Lv.{self.level}) - HP: {self.get_stat(StatType.HEALTH)}/{self.get_stat(StatType.MAX_HEALTH)}"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"Player(name='{self.name}', class={self.player_class.value}, level={self.level}, user_id={self.user_id})"
