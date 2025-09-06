"""
Tests for the region system
"""

import pytest
import tempfile
import os
import json
from src.game.region import Region, RegionManager
from src.game.entities.player import Player
from src.game.enums import PlayerClass
from src.game.data_loader import DataLoader


class TestRegion:
    """Test cases for Region class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self._create_test_region_data()
        
        # Create region instance with test data loader
        test_data_loader = DataLoader(self.temp_dir)
        self.region = Region("test_region", test_data_loader)
    
    def teardown_method(self):
        """Clean up after each test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_region_data(self):
        """Create test region data"""
        os.makedirs(os.path.join(self.temp_dir, "regions"), exist_ok=True)
        
        region_data = {
            "id": "test_region",
            "name": "Test Region",
            "description": "A test region for testing",
            "level": 2,
            "loot_multiplier": 1.5,
            "enemy_level_bonus": 1,
            "available_activities": ["combat", "mining", "foraging"],
            "neighboring_regions": ["test_region_2"],
            "unlock_requirements": {
                "level": 3,
                "items": [{"item": "test_key", "quantity": 1}],
                "quests": ["test_quest"]
            },
            "travel_cost": {
                "gold": 50,
                "items": [{"item": "travel_token", "quantity": 1}]
            },
            "environmental_effects": ["rain", "wind"]
        }
        
        with open(os.path.join(self.temp_dir, "regions", "test_region.json"), 'w') as f:
            json.dump(region_data, f)
        
        # Create second test region
        region_data_2 = {
            "id": "test_region_2",
            "name": "Test Region 2",
            "description": "Another test region",
            "level": 3,
            "loot_multiplier": 2.0,
            "enemy_level_bonus": 2,
            "available_activities": ["combat"],
            "neighboring_regions": ["test_region"],
            "unlock_requirements": {"level": 1, "items": [], "quests": []},
            "travel_cost": {"gold": 0, "items": []},
            "environmental_effects": []
        }
        
        with open(os.path.join(self.temp_dir, "regions", "test_region_2.json"), 'w') as f:
            json.dump(region_data_2, f)
    
    def test_region_properties(self):
        """Test region property access"""
        assert self.region.name == "Test Region"
        assert self.region.description == "A test region for testing"
        assert self.region.level == 2
        assert self.region.loot_multiplier == 1.5
        assert self.region.enemy_level_bonus == 1
    
    def test_available_activities(self):
        """Test available activities"""
        activities = self.region.available_activities
        assert "combat" in activities
        assert "mining" in activities
        assert "foraging" in activities
        assert len(activities) == 3
    
    def test_neighboring_regions(self):
        """Test neighboring regions"""
        neighbors = self.region.neighboring_regions
        assert "test_region_2" in neighbors
        assert len(neighbors) == 1
    
    def test_unlock_requirements(self):
        """Test unlock requirements"""
        requirements = self.region.get_unlock_requirements()
        assert requirements["level"] == 3
        assert len(requirements["items"]) == 1
        assert requirements["items"][0]["item"] == "test_key"
        assert requirements["items"][0]["quantity"] == 1
        assert "test_quest" in requirements["quests"]
    
    def test_travel_cost(self):
        """Test travel cost"""
        cost = self.region.get_travel_cost()
        assert cost["gold"] == 50
        assert len(cost["items"]) == 1
        assert cost["items"][0]["item"] == "travel_token"
        assert cost["items"][0]["quantity"] == 1
    
    def test_environmental_effects(self):
        """Test environmental effects"""
        effects = self.region.get_environmental_effects()
        assert "rain" in effects
        assert "wind" in effects
        assert len(effects) == 2
    
    def test_can_player_access_success(self):
        """Test successful player access check"""
        player = Player("TestPlayer", PlayerClass.WARRIOR, level=5)
        player.inventory.add_item(type('Item', (), {
            'name': 'test_key',
            'quantity': 1,
            'stackable': False
        })())
        
        can_access, reason = self.region.can_player_access(player)
        assert can_access
        assert reason == ""
    
    def test_can_player_access_level_too_low(self):
        """Test player access with level too low"""
        player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
        
        can_access, reason = self.region.can_player_access(player)
        assert not can_access
        assert "level" in reason.lower()
    
    def test_can_player_access_missing_item(self):
        """Test player access with missing required item"""
        player = Player("TestPlayer", PlayerClass.WARRIOR, level=5)
        
        can_access, reason = self.region.can_player_access(player)
        assert not can_access
        assert "test_key" in reason
    
    def test_to_dict(self):
        """Test converting region to dictionary"""
        region_dict = self.region.to_dict()
        assert isinstance(region_dict, dict)
        assert region_dict["id"] == "test_region"
        assert region_dict["name"] == "Test Region"
        assert region_dict["level"] == 2


class TestRegionManager:
    """Test cases for RegionManager class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self._create_test_region_data()
        
        # Create region manager with test data loader
        test_data_loader = DataLoader(self.temp_dir)
        self.region_manager = RegionManager(test_data_loader)
    
    def teardown_method(self):
        """Clean up after each test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_region_data(self):
        """Create test region data"""
        os.makedirs(os.path.join(self.temp_dir, "regions"), exist_ok=True)
        
        # Create simple test region
        region_data = {
            "id": "simple_region",
            "name": "Simple Region",
            "description": "A simple test region",
            "level": 1,
            "loot_multiplier": 1.0,
            "enemy_level_bonus": 0,
            "available_activities": ["combat"],
            "neighboring_regions": [],
            "unlock_requirements": {"level": 1, "items": [], "quests": []},
            "travel_cost": {"gold": 0, "items": []},
            "environmental_effects": []
        }
        
        with open(os.path.join(self.temp_dir, "regions", "simple_region.json"), 'w') as f:
            json.dump(region_data, f)
    
    def test_set_current_region_success(self):
        """Test setting current region successfully"""
        success = self.region_manager.set_current_region("simple_region")
        assert success
        assert self.region_manager.get_current_region() is not None
        assert self.region_manager.get_current_region().name == "Simple Region"
    
    def test_set_current_region_failure(self):
        """Test setting current region with invalid ID"""
        success = self.region_manager.set_current_region("nonexistent")
        assert not success
        assert self.region_manager.get_current_region() is None
    
    def test_get_current_region(self):
        """Test getting current region"""
        # Initially no region set
        assert self.region_manager.get_current_region() is None
        
        # Set region and check
        self.region_manager.set_current_region("simple_region")
        current = self.region_manager.get_current_region()
        assert current is not None
        assert current.name == "Simple Region"
    
    def test_get_available_regions(self):
        """Test getting available regions"""
        regions = self.region_manager.get_available_regions()
        assert "simple_region" in regions
    
    def test_can_travel_to_success(self):
        """Test successful travel check"""
        player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
        
        can_travel, reason = self.region_manager.can_travel_to(player, "simple_region")
        assert can_travel
        assert reason == ""
    
    def test_can_travel_to_nonexistent_region(self):
        """Test travel check with nonexistent region"""
        player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
        
        can_travel, reason = self.region_manager.can_travel_to(player, "nonexistent")
        assert not can_travel
        assert "not found" in reason.lower()
    
    def test_travel_to_region_success(self):
        """Test successful travel"""
        player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
        
        success, message = self.region_manager.travel_to_region(player, "simple_region")
        assert success
        assert "Successfully traveled" in message
        assert player.current_region == "simple_region"
        assert self.region_manager.get_current_region().name == "Simple Region"
    
    def test_travel_to_region_failure(self):
        """Test failed travel"""
        player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
        
        success, message = self.region_manager.travel_to_region(player, "nonexistent")
        assert not success
        assert "not found" in message.lower()
        assert player.current_region != "nonexistent"
