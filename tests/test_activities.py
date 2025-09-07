"""
Tests for activity system and energy management
"""

import pytest
import tempfile
import os
import json
from src.game.entities.player import Player, PlayerClass
from src.game.enums import StatType
from src.game.data_loader import DataLoader


class TestActivitySystem:
    """Test cases for activity system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self._create_test_activity_data()
        
        # Create data loader
        self.data_loader = DataLoader(self.temp_dir)
        
        # Create test player
        self.player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
    
    def teardown_method(self):
        """Clean up after each test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_activity_data(self):
        """Create test activity data"""
        os.makedirs(os.path.join(self.temp_dir, "activities"), exist_ok=True)
        
        # Create scout activity
        scout_data = {
            "id": "scout",
            "name": "Scout",
            "description": "Explore the area carefully to scout for enemies",
            "energy_cost": 8,
            "requirements": {
                "level": 1,
                "items": [],
                "tools": []
            },
            "rewards": {
                "experience": 5,
                "gold": 0,
                "items": []
            },
            "success_rate": 0.7,
            "duration": 0,
            "category": "exploration",
            "region_specific": True,
            "enemy_encounter": True,
            "encounter_rates": {
                "normal": 0.6,
                "mini_boss": 0.3,
                "boss": 0.1
            }
        }
        
        with open(os.path.join(self.temp_dir, "activities", "scout.json"), 'w') as f:
            json.dump(scout_data, f)
        
        # Create foraging activity
        foraging_data = {
            "id": "foraging",
            "name": "Foraging",
            "description": "Search for useful plants and materials",
            "energy_cost": 5,
            "requirements": {
                "level": 1,
                "items": [],
                "tools": []
            },
            "rewards": {
                "experience": 3,
                "gold": 2,
                "items": ["herbs", "berries"]
            },
            "success_rate": 0.8,
            "duration": 0,
            "category": "gathering",
            "region_specific": True,
            "enemy_encounter": False
        }
        
        with open(os.path.join(self.temp_dir, "activities", "foraging.json"), 'w') as f:
            json.dump(foraging_data, f)
    
    def test_load_activity_data(self):
        """Test loading activity data"""
        scout_activity = self.data_loader.load_activity("scout")
        
        assert scout_activity is not None
        assert scout_activity["id"] == "scout"
        assert scout_activity["name"] == "Scout"
        assert scout_activity["energy_cost"] == 8
        assert scout_activity["enemy_encounter"] is True
    
    def test_activity_energy_cost(self):
        """Test activity energy cost validation"""
        scout_activity = self.data_loader.load_activity("scout")
        foraging_activity = self.data_loader.load_activity("foraging")
        
        # Scout costs more energy than foraging
        assert scout_activity["energy_cost"] > foraging_activity["energy_cost"]
        
        # Both activities have positive energy costs
        assert scout_activity["energy_cost"] > 0
        assert foraging_activity["energy_cost"] > 0
    
    def test_player_energy_consumption(self):
        """Test player energy consumption during activities"""
        initial_mana = self.player.get_stat(StatType.MANA)
        scout_activity = self.data_loader.load_activity("scout")
        energy_cost = scout_activity["energy_cost"]
        
        # Player should have enough energy initially
        assert initial_mana >= energy_cost
        
        # Consume energy (simulate activity)
        self.player.modify_stat(StatType.MANA, -energy_cost)
        
        # Check energy was consumed
        new_mana = self.player.get_stat(StatType.MANA)
        assert new_mana == initial_mana - energy_cost
    
    def test_insufficient_energy(self):
        """Test behavior when player has insufficient energy"""
        # Set player mana to low value
        self.player.set_stat(StatType.MANA, 3)
        scout_activity = self.data_loader.load_activity("scout")
        energy_cost = scout_activity["energy_cost"]  # 8
        
        # Player should not have enough energy
        current_mana = self.player.get_stat(StatType.MANA)
        assert current_mana < energy_cost
    
    def test_activity_rewards(self):
        """Test activity reward structure"""
        foraging_activity = self.data_loader.load_activity("foraging")
        rewards = foraging_activity["rewards"]
        
        assert "experience" in rewards
        assert "gold" in rewards
        assert "items" in rewards
        assert rewards["experience"] > 0
        assert rewards["gold"] >= 0
        assert isinstance(rewards["items"], list)
    
    def test_activity_requirements(self):
        """Test activity requirement structure"""
        scout_activity = self.data_loader.load_activity("scout")
        requirements = scout_activity["requirements"]
        
        assert "level" in requirements
        assert "items" in requirements
        assert "tools" in requirements
        assert requirements["level"] >= 1
        assert isinstance(requirements["items"], list)
        assert isinstance(requirements["tools"], list)
    
    def test_activity_categories(self):
        """Test activity categorization"""
        scout_activity = self.data_loader.load_activity("scout")
        foraging_activity = self.data_loader.load_activity("foraging")
        
        assert scout_activity["category"] == "exploration"
        assert foraging_activity["category"] == "gathering"
    
    def test_enemy_encounter_activities(self):
        """Test activities that can encounter enemies"""
        scout_activity = self.data_loader.load_activity("scout")
        foraging_activity = self.data_loader.load_activity("foraging")
        
        # Scout should have enemy encounters
        assert scout_activity["enemy_encounter"] is True
        assert "encounter_rates" in scout_activity
        
        # Foraging should not have enemy encounters
        assert foraging_activity["enemy_encounter"] is False
        assert "encounter_rates" not in foraging_activity
    
    def test_encounter_rates(self):
        """Test enemy encounter rate structure"""
        scout_activity = self.data_loader.load_activity("scout")
        encounter_rates = scout_activity["encounter_rates"]
        
        assert "normal" in encounter_rates
        assert "mini_boss" in encounter_rates
        assert "boss" in encounter_rates
        
        # Rates should be between 0 and 1
        for rate in encounter_rates.values():
            assert 0 <= rate <= 1
        
        # Total rates should not exceed 1.0
        total_rate = sum(encounter_rates.values())
        assert total_rate <= 1.0


class TestEnergyManagement:
    """Test cases for energy (mana) management"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
    
    def test_initial_energy(self):
        """Test player starts with full energy"""
        current_mana = self.player.get_stat(StatType.MANA)
        max_mana = self.player.get_stat(StatType.MAX_MANA)
        
        assert current_mana == max_mana
        assert current_mana > 0
    
    def test_energy_consumption(self):
        """Test energy consumption mechanics"""
        initial_mana = self.player.get_stat(StatType.MANA)
        energy_cost = 10
        
        # Consume energy
        self.player.modify_stat(StatType.MANA, -energy_cost)
        
        new_mana = self.player.get_stat(StatType.MANA)
        assert new_mana == initial_mana - energy_cost
    
    def test_energy_restoration(self):
        """Test energy restoration mechanics"""
        # Consume some energy first
        self.player.modify_stat(StatType.MANA, -20)
        current_mana = self.player.get_stat(StatType.MANA)
        
        # Restore energy
        restored = self.player.restore_mana(15)
        new_mana = self.player.get_stat(StatType.MANA)
        
        assert restored == 15
        assert new_mana == current_mana + 15
    
    def test_energy_cannot_exceed_maximum(self):
        """Test that energy cannot exceed maximum"""
        max_mana = self.player.get_stat(StatType.MAX_MANA)
        
        # Try to restore more than maximum
        restored = self.player.restore_mana(1000)
        current_mana = self.player.get_stat(StatType.MANA)
        
        # Should only restore up to maximum
        assert current_mana == max_mana
        assert restored <= max_mana
    
    def test_energy_cannot_go_below_zero(self):
        """Test that energy cannot go below zero"""
        # Try to consume more than available
        self.player.modify_stat(StatType.MANA, -1000)
        current_mana = self.player.get_stat(StatType.MANA)
        
        # Should not go below zero
        assert current_mana >= 0
    
    def test_level_up_restores_energy(self):
        """Test that leveling up restores energy"""
        # Consume some energy first
        self.player.modify_stat(StatType.MANA, -20)
        current_mana = self.player.get_stat(StatType.MANA)
        old_max_mana = self.player.get_stat(StatType.MAX_MANA)
        
        # Level up (this should restore energy)
        self.player.level_up()
        new_mana = self.player.get_stat(StatType.MANA)
        new_max_mana = self.player.get_stat(StatType.MAX_MANA)
        
        # Energy should be restored to the old maximum (before bonuses applied)
        # The new maximum will be higher due to level up bonuses
        assert new_mana == old_max_mana
        assert new_max_mana > old_max_mana
        assert new_mana > current_mana
    
    def test_different_classes_have_different_energy(self):
        """Test that different classes have different energy amounts"""
        warrior = Player("Warrior", PlayerClass.WARRIOR, level=1)
        mage = Player("Mage", PlayerClass.MAGE, level=1)
        rogue = Player("Rogue", PlayerClass.ROGUE, level=1)
        cleric = Player("Cleric", PlayerClass.CLERIC, level=1)
        
        warrior_mana = warrior.get_stat(StatType.MAX_MANA)
        mage_mana = mage.get_stat(StatType.MAX_MANA)
        rogue_mana = rogue.get_stat(StatType.MAX_MANA)
        cleric_mana = cleric.get_stat(StatType.MAX_MANA)
        
        # Mage should have the most mana
        assert mage_mana > warrior_mana
        assert mage_mana > rogue_mana
        
        # Cleric should have more mana than warrior and rogue
        assert cleric_mana > warrior_mana
        assert cleric_mana > rogue_mana
        
        # All classes should have positive mana
        assert warrior_mana > 0
        assert mage_mana > 0
        assert rogue_mana > 0
        assert cleric_mana > 0
