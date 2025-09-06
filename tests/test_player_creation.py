"""
Tests for the player creation system
"""

import pytest
from src.game.player_creation import PlayerCreation
from src.game.enums import PlayerClass, StatType, EquipmentSlot
from src.game.entities.player import Player


class TestPlayerCreation:
    """Test cases for PlayerCreation class"""
    
    def test_create_player_warrior(self):
        """Test creating a warrior player"""
        player = PlayerCreation.create_player("TestWarrior", PlayerClass.WARRIOR)
        
        assert isinstance(player, Player)
        assert player.name == "TestWarrior"
        assert player.player_class == PlayerClass.WARRIOR
        assert player.level == 1
        assert player.current_region == "grasslands"
        assert player.gold == 10
    
    def test_create_player_mage(self):
        """Test creating a mage player"""
        player = PlayerCreation.create_player("TestMage", PlayerClass.MAGE)
        
        assert isinstance(player, Player)
        assert player.name == "TestMage"
        assert player.player_class == PlayerClass.MAGE
        assert player.level == 1
        assert player.current_region == "grasslands"
        assert player.gold == 10
    
    def test_create_player_rogue(self):
        """Test creating a rogue player"""
        player = PlayerCreation.create_player("TestRogue", PlayerClass.ROGUE)
        
        assert isinstance(player, Player)
        assert player.name == "TestRogue"
        assert player.player_class == PlayerClass.ROGUE
        assert player.level == 1
        assert player.current_region == "grasslands"
        assert player.gold == 10
    
    def test_create_player_cleric(self):
        """Test creating a cleric player"""
        player = PlayerCreation.create_player("TestCleric", PlayerClass.CLERIC)
        
        assert isinstance(player, Player)
        assert player.name == "TestCleric"
        assert player.player_class == PlayerClass.CLERIC
        assert player.level == 1
        assert player.current_region == "grasslands"
        assert player.gold == 10
    
    def test_create_player_default_class(self):
        """Test creating a player with default class (warrior)"""
        player = PlayerCreation.create_player("TestDefault")
        
        assert player.player_class == PlayerClass.WARRIOR
    
    def test_player_has_starting_equipment(self):
        """Test that player has starting equipment (fists)"""
        player = PlayerCreation.create_player("TestEquipped")
        
        # Check if fists are equipped
        equipped_weapon = player.equipment.get_equipped_item(EquipmentSlot.MAIN_HAND)
        assert equipped_weapon is not None
        assert equipped_weapon.name == "Bare Fists"
        assert equipped_weapon.damage == 3
    
    def test_player_has_full_health_and_mana(self):
        """Test that player starts with full health and mana"""
        player = PlayerCreation.create_player("TestHealth")
        
        assert player.get_stat(StatType.HEALTH) == player.get_stat(StatType.MAX_HEALTH)
        assert player.get_stat(StatType.MANA) == player.get_stat(StatType.MAX_MANA)
    
    def test_warrior_stats(self):
        """Test warrior-specific stat bonuses"""
        player = PlayerCreation.create_player("TestWarrior", PlayerClass.WARRIOR)
        
        # Warriors should have higher health and attack
        assert player.get_stat(StatType.MAX_HEALTH) >= 120  # Base + class bonus
        assert player.get_stat(StatType.ATTACK) >= 12  # Base + class bonus
    
    def test_mage_stats(self):
        """Test mage-specific stat bonuses"""
        player = PlayerCreation.create_player("TestMage", PlayerClass.MAGE)
        
        # Mages should have higher mana
        assert player.get_stat(StatType.MAX_MANA) >= 60  # Base + class bonus
    
    def test_rogue_stats(self):
        """Test rogue-specific stat bonuses"""
        player = PlayerCreation.create_player("TestRogue", PlayerClass.ROGUE)
        
        # Rogues should have higher speed
        assert player.get_stat(StatType.SPEED) >= 10  # Base + class bonus
    
    def test_cleric_stats(self):
        """Test cleric-specific stat bonuses"""
        player = PlayerCreation.create_player("TestCleric", PlayerClass.CLERIC)
        
        # Clerics should have balanced stats
        assert player.get_stat(StatType.MAX_HEALTH) >= 120  # Base + class bonus
        assert player.get_stat(StatType.MAX_MANA) >= 60  # Base + class bonus
    
    def test_get_available_classes(self):
        """Test getting available player classes"""
        classes = PlayerCreation.get_available_classes()
        
        assert PlayerClass.WARRIOR in classes
        assert PlayerClass.MAGE in classes
        assert PlayerClass.ROGUE in classes
        assert PlayerClass.CLERIC in classes
        assert len(classes) == 4
    
    def test_get_class_description(self):
        """Test getting class descriptions"""
        warrior_desc = PlayerCreation.get_class_description(PlayerClass.WARRIOR)
        mage_desc = PlayerCreation.get_class_description(PlayerClass.MAGE)
        rogue_desc = PlayerCreation.get_class_description(PlayerClass.ROGUE)
        cleric_desc = PlayerCreation.get_class_description(PlayerClass.CLERIC)
        
        assert isinstance(warrior_desc, str)
        assert isinstance(mage_desc, str)
        assert isinstance(rogue_desc, str)
        assert isinstance(cleric_desc, str)
        
        assert len(warrior_desc) > 0
        assert len(mage_desc) > 0
        assert len(rogue_desc) > 0
        assert len(cleric_desc) > 0
    
    def test_validate_player_name_valid(self):
        """Test validating valid player names"""
        valid_names = ["Test", "Player123", "Hero", "Adventurer", "AB"]
        
        for name in valid_names:
            is_valid, error = PlayerCreation.validate_player_name(name)
            assert is_valid, f"Name '{name}' should be valid: {error}"
            assert error == ""
    
    def test_validate_player_name_invalid(self):
        """Test validating invalid player names"""
        # Empty name
        is_valid, error = PlayerCreation.validate_player_name("")
        assert not is_valid
        assert "empty" in error.lower()
        
        # Whitespace only
        is_valid, error = PlayerCreation.validate_player_name("   ")
        assert not is_valid
        assert "empty" in error.lower()
        
        # Too short
        is_valid, error = PlayerCreation.validate_player_name("A")
        assert not is_valid
        assert "2 characters" in error
        
        # Too long
        long_name = "A" * 21
        is_valid, error = PlayerCreation.validate_player_name(long_name)
        assert not is_valid
        assert "20 characters" in error
        
        # Invalid characters
        invalid_names = ["Test<", "Player>", "Hero:", "Adventurer\"", "Name|", "Test?"]
        for name in invalid_names:
            is_valid, error = PlayerCreation.validate_player_name(name)
            assert not is_valid, f"Name '{name}' should be invalid"
            assert "cannot contain" in error
    
    def test_validate_player_name_edge_cases(self):
        """Test edge cases for name validation"""
        # Exactly 2 characters (should be valid)
        is_valid, error = PlayerCreation.validate_player_name("AB")
        assert is_valid
        
        # Exactly 20 characters (should be valid)
        name_20 = "A" * 20
        is_valid, error = PlayerCreation.validate_player_name(name_20)
        assert is_valid
        
        # Name with spaces (should be valid after strip)
        is_valid, error = PlayerCreation.validate_player_name("  Test Player  ")
        assert is_valid
