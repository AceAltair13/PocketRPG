"""
Player creation system
Handles the initial player setup with default stats and starting equipment
"""

from typing import Optional
from .entities.player import Player, PlayerClass
from .enums import StatType, EquipmentSlot
from .data_loader import data_loader


class PlayerCreation:
    """
    Handles player creation and initialization.
    Sets up default stats, starting equipment, and initial location.
    """
    
    @staticmethod
    def create_player(name: str, player_class: PlayerClass = PlayerClass.WARRIOR) -> Player:
        """
        Create a new player with default stats and starting equipment.
        
        Args:
            name: Player's name
            player_class: Player's class (defaults to Warrior)
            
        Returns:
            Newly created Player instance
        """
        # Create player with default level 1
        player = Player(name, player_class, level=1)
        
        # Set default stats (these are already set in Player.__init__)
        # But we can customize them here if needed
        player.set_stat(StatType.HEALTH, player.get_stat(StatType.MAX_HEALTH))
        player.set_stat(StatType.MANA, player.get_stat(StatType.MAX_MANA))
        
        # Give starting equipment (bare fists)
        PlayerCreation._give_starting_equipment(player)
        
        # Set starting location
        player.current_region = "grasslands"
        
        # Give starting gold
        player.add_gold(10)
        
        return player
    
    @staticmethod
    def _give_starting_equipment(player: Player) -> None:
        """Give the player their starting equipment"""
        # Load fists data
        fists_data = data_loader.load_item("fists")
        if fists_data:
            # Create fists item from data
            from .items.item import WeaponItem
            from .enums import ItemRarity, ItemQuality
            
            fists = WeaponItem(
                name=fists_data["name"],
                description=fists_data["description"],
                rarity=ItemRarity(fists_data["rarity"]),
                quality=ItemQuality(fists_data["quality"]),
                value=fists_data["value"],
                level_requirement=fists_data["level_requirement"],
                emoji=fists_data.get("emoji", "👊")
            )
            
            # Set weapon stats
            weapon_stats = fists_data.get("weapon_stats", {})
            fists.damage = weapon_stats.get("damage", 3)
            fists.damage_type = weapon_stats.get("damage_type", "physical")
            fists.weapon_type = weapon_stats.get("weapon_type", "unarmed")
            fists.critical_chance = weapon_stats.get("critical_chance", 0.02)
            fists.critical_multiplier = weapon_stats.get("critical_multiplier", 1.5)
            
        # Equip the fists
        player.equipment.equip_item(fists, EquipmentSlot.MAIN_HAND)
    
    @staticmethod
    def get_available_classes() -> list[PlayerClass]:
        """Get list of available player classes"""
        return list(PlayerClass)
    
    @staticmethod
    def get_class_description(player_class: PlayerClass) -> str:
        """Get description of a player class"""
        descriptions = {
            PlayerClass.WARRIOR: "A strong melee fighter with high health and attack power. Good for beginners.",
            PlayerClass.MAGE: "A spellcaster with powerful magic but lower physical stats. Requires strategy.",
            PlayerClass.ROGUE: "A nimble fighter with high speed and critical hit potential. High risk, high reward.",
            PlayerClass.CLERIC: "A support class with healing abilities and balanced stats. Great for team play."
        }
        return descriptions.get(player_class, "Unknown class")
    
    @staticmethod
    def validate_player_name(name: str) -> tuple[bool, str]:
        """
        Validate a player name.
        
        Args:
            name: Name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Name cannot be empty"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, "Name must be at least 2 characters long"
        
        if len(name) > 20:
            return False, "Name must be no more than 20 characters long"
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in invalid_chars:
            if char in name:
                return False, f"Name cannot contain '{char}'"
        
        return True, ""
