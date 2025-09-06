"""
Tests for the data loader system
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from src.game.data_loader import DataLoader


class TestDataLoader:
    """Test cases for DataLoader class"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.data_loader = DataLoader(self.temp_dir)
        
        # Create test data structure
        self._create_test_data()
    
    def teardown_method(self):
        """Clean up after each test method"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_data(self):
        """Create test data files"""
        # Create directories
        os.makedirs(os.path.join(self.temp_dir, "regions"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "activities"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "items"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "enemies"), exist_ok=True)
        
        # Create test region
        region_data = {
            "id": "test_region",
            "name": "Test Region",
            "description": "A test region",
            "level": 1,
            "loot_multiplier": 1.0,
            "enemy_level_bonus": 0,
            "available_activities": ["combat", "foraging"],
            "neighboring_regions": [],
            "unlock_requirements": {"level": 1, "items": [], "quests": []},
            "travel_cost": {"gold": 0, "items": []},
            "environmental_effects": []
        }
        
        with open(os.path.join(self.temp_dir, "regions", "test_region.json"), 'w') as f:
            json.dump(region_data, f)
        
        # Create test activity
        activity_data = {
            "id": "test_activity",
            "name": "Test Activity",
            "description": "A test activity",
            "base_duration": 30,
            "energy_cost": 10,
            "required_tools": [],
            "possible_rewards": [],
            "experience_reward": 5,
            "skill_requirements": {}
        }
        
        with open(os.path.join(self.temp_dir, "activities", "test_activity.json"), 'w') as f:
            json.dump(activity_data, f)
        
        # Create test item
        item_data = {
            "id": "test_item",
            "name": "Test Item",
            "description": "A test item",
            "type": "consumable",
            "rarity": "common",
            "quality": "normal",
            "value": 10,
            "stackable": True,
            "max_stack": 99
        }
        
        with open(os.path.join(self.temp_dir, "items", "test_item.json"), 'w') as f:
            json.dump(item_data, f)
        
        # Create test enemy
        enemy_data = {
            "id": "test_enemy",
            "name": "Test Enemy",
            "description": "A test enemy",
            "type": "normal",
            "behavior": "aggressive",
            "base_level": 1,
            "base_stats": {
                "health": 50,
                "mana": 20,
                "attack": 10,
                "defense": 5,
                "speed": 10
            },
            "experience_reward": 20,
            "gold_reward": 10,
            "loot_table": [],
            "ai_abilities": [],
            "spawn_regions": ["test_region"]
        }
        
        with open(os.path.join(self.temp_dir, "enemies", "test_enemy.json"), 'w') as f:
            json.dump(enemy_data, f)
    
    def test_load_region_success(self):
        """Test successful region loading"""
        region = self.data_loader.load_region("test_region")
        
        assert region is not None
        assert region["id"] == "test_region"
        assert region["name"] == "Test Region"
        assert region["level"] == 1
        assert "combat" in region["available_activities"]
    
    def test_load_region_not_found(self):
        """Test loading non-existent region"""
        region = self.data_loader.load_region("nonexistent")
        assert region is None
    
    def test_load_activity_success(self):
        """Test successful activity loading"""
        activity = self.data_loader.load_activity("test_activity")
        
        assert activity is not None
        assert activity["id"] == "test_activity"
        assert activity["name"] == "Test Activity"
        assert activity["energy_cost"] == 10
    
    def test_load_item_success(self):
        """Test successful item loading"""
        item = self.data_loader.load_item("test_item")
        
        assert item is not None
        assert item["id"] == "test_item"
        assert item["name"] == "Test Item"
        assert item["value"] == 10
        assert item["stackable"] is True
    
    def test_load_enemy_success(self):
        """Test successful enemy loading"""
        enemy = self.data_loader.load_enemy("test_enemy")
        
        assert enemy is not None
        assert enemy["id"] == "test_enemy"
        assert enemy["name"] == "Test Enemy"
        assert enemy["base_level"] == 1
        assert enemy["experience_reward"] == 20
    
    def test_caching(self):
        """Test that data is cached properly"""
        # Load data twice
        region1 = self.data_loader.load_region("test_region")
        region2 = self.data_loader.load_region("test_region")
        
        # Should be the same object (cached)
        assert region1 is region2
    
    def test_list_regions(self):
        """Test listing available regions"""
        regions = self.data_loader.list_regions()
        assert "test_region" in regions
    
    def test_list_activities(self):
        """Test listing available activities"""
        activities = self.data_loader.list_activities()
        assert "test_activity" in activities
    
    def test_list_items(self):
        """Test listing available items"""
        items = self.data_loader.list_items()
        assert "test_item" in items
    
    def test_list_enemies(self):
        """Test listing available enemies"""
        enemies = self.data_loader.list_enemies()
        assert "test_enemy" in enemies
    
    def test_get_enemies_for_region(self):
        """Test getting enemies for a specific region"""
        enemies = self.data_loader.get_enemies_for_region("test_region")
        assert "test_enemy" in enemies
    
    def test_get_enemies_for_nonexistent_region(self):
        """Test getting enemies for non-existent region"""
        enemies = self.data_loader.get_enemies_for_region("nonexistent")
        assert enemies == []
    
    def test_clear_cache(self):
        """Test cache clearing"""
        # Load data to populate cache
        self.data_loader.load_region("test_region")
        assert "regions" in self.data_loader._cache
        
        # Clear cache
        self.data_loader.clear_cache()
        assert self.data_loader._cache == {}
    
    def test_invalid_json_file(self):
        """Test handling of invalid JSON files"""
        # Create invalid JSON file
        invalid_file = os.path.join(self.temp_dir, "regions", "invalid.json")
        with open(invalid_file, 'w') as f:
            f.write("invalid json content")
        
        # Should return None without crashing
        result = self.data_loader.load_region("invalid")
        assert result is None
    
    def test_missing_file(self):
        """Test handling of missing files"""
        result = self.data_loader.load_region("missing")
        assert result is None
