"""
Region system for the game
Handles regions, travel, and region-specific content
"""

from typing import Dict, List, Optional, Any
from .enums import StatType
from .data_loader import data_loader


class Region:
    """
    Represents a game region with its properties and content.
    """
    
    def __init__(self, region_id: str, data_loader_instance=None):
        self.region_id: str = region_id
        self.data: Optional[Dict[str, Any]] = None
        self.data_loader = data_loader_instance or data_loader
        self._load_data()
    
    def _load_data(self) -> None:
        """Load region data from JSON file"""
        self.data = self.data_loader.load_region(self.region_id)
        if not self.data:
            raise ValueError(f"Region {self.region_id} not found")
    
    @property
    def name(self) -> str:
        """Get region name"""
        return self.data.get("name", "Unknown Region")
    
    @property
    def description(self) -> str:
        """Get region description"""
        return self.data.get("description", "No description available")
    
    @property
    def level(self) -> int:
        """Get region level"""
        return self.data.get("level", 0)
    
    @property
    def loot_multiplier(self) -> float:
        """Get loot rarity multiplier"""
        return self.data.get("loot_multiplier", 1.0)
    
    @property
    def enemy_level_bonus(self) -> int:
        """Get enemy level bonus for this region"""
        return self.data.get("enemy_level_bonus", 0)
    
    @property
    def available_activities(self) -> List[str]:
        """Get list of available activities in this region"""
        return self.data.get("available_activities", [])
    
    def get_unlocked_activities(self, player) -> List[str]:
        """Get list of activities available to the player in this region"""
        region_activities = self.data.get("available_activities", [])
        return [activity for activity in region_activities if player.has_activity_unlocked(activity)]
    
    @property
    def neighboring_regions(self) -> List[str]:
        """Get list of neighboring regions"""
        return self.data.get("neighboring_regions", [])
    
    def get_unlock_requirements(self) -> Dict[str, Any]:
        """Get requirements to unlock this region"""
        return self.data.get("unlock_requirements", {})
    
    def get_travel_cost(self) -> Dict[str, Any]:
        """Get cost to travel to this region"""
        return self.data.get("travel_cost", {})
    
    def can_player_access(self, player) -> tuple[bool, str]:
        """
        Check if a player can access this region.
        
        Args:
            player: Player instance to check
            
        Returns:
            Tuple of (can_access, reason)
        """
        requirements = self.get_unlock_requirements()
        
        # Check level requirement
        required_level = requirements.get("level", 1)
        if player.level < required_level:
            return False, f"Requires level {required_level}"
        
        # Check item requirements
        required_items = requirements.get("items", [])
        for item_requirement in required_items:
            item_id = item_requirement.get("item")
            quantity = item_requirement.get("quantity", 1)
            if not player.inventory.has_item(item_id, quantity):
                return False, f"Requires {quantity}x {item_id}"
        
        # Check quest requirements
        required_quests = requirements.get("quests", [])
        for quest_id in required_quests:
            # This would need quest system implementation
            pass
        
        return True, ""
    
    def get_available_enemies(self) -> List[str]:
        """Get list of enemies that can spawn in this region"""
        return data_loader.get_enemies_for_region(self.region_id)
    
    def get_enemies_with_discovery(self, player) -> List[Dict[str, Any]]:
        """Get enemies with discovery status for a player"""
        enemies = []
        region_data = data_loader.load_region(self.region_id)
        if not region_data:
            return enemies
        
        enemy_ids = region_data.get("enemies", [])
        for enemy_id in enemy_ids:
            enemy_data = data_loader.load_enemy(enemy_id)
            if enemy_data:
                discovered = player.has_discovered_enemy(enemy_id)
                enemies.append({
                    "id": enemy_id,
                    "name": enemy_data["name"] if discovered else "Unknown Enemy",
                    "type": enemy_data["type"],
                    "level": enemy_data["base_level"],
                    "rarity": enemy_data.get("rarity", "common"),
                    "discovered": discovered,
                    "data": enemy_data if discovered else None
                })
        
        return enemies
    
    def get_scout_encounter(self, player) -> Optional[Dict[str, Any]]:
        """Get a random enemy encounter based on scout activity"""
        import random
        
        region_data = data_loader.load_region(self.region_id)
        if not region_data:
            return None
        
        # Get scout activity data
        scout_data = data_loader.load_activity("scout")
        if not scout_data:
            return None
        
        # Check if scout succeeds
        success_rate = scout_data.get("success_rate", 0.7)
        if random.random() > success_rate:
            return None  # Scout failed, no encounter
        
        # Get enemies in this region
        enemy_ids = region_data.get("enemies", [])
        if not enemy_ids:
            return None
        
        # Group enemies by type for weighted selection
        enemies_by_type = {"normal": [], "mini_boss": [], "boss": []}
        for enemy_id in enemy_ids:
            enemy_data = data_loader.load_enemy(enemy_id)
            if enemy_data:
                enemy_type = enemy_data.get("type", "normal")
                enemies_by_type[enemy_type].append(enemy_data)
        
        # Use encounter rates to select enemy type
        encounter_rates = scout_data.get("encounter_rates", {
            "normal": 0.6,
            "mini_boss": 0.3,
            "boss": 0.1
        })
        
        # Weighted random selection
        rand = random.random()
        selected_type = "normal"
        cumulative = 0
        
        for enemy_type, rate in encounter_rates.items():
            cumulative += rate
            if rand <= cumulative:
                selected_type = enemy_type
                break
        
        # Select random enemy of the chosen type
        available_enemies = enemies_by_type.get(selected_type, [])
        if not available_enemies:
            # Fallback to any available enemy
            all_enemies = []
            for enemy_list in enemies_by_type.values():
                all_enemies.extend(enemy_list)
            if not all_enemies:
                return None
            selected_enemy = random.choice(all_enemies)
        else:
            selected_enemy = random.choice(available_enemies)
        
        return {
            "enemy_id": selected_enemy["id"],
            "enemy_data": selected_enemy,
            "encounter_type": selected_type
        }
    
    def get_environmental_effects(self) -> List[str]:
        """Get environmental effects in this region"""
        return self.data.get("environmental_effects", [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert region to dictionary"""
        return self.data.copy() if self.data else {}


class RegionManager:
    """
    Manages regions and player travel between them.
    """
    
    def __init__(self, data_loader_instance=None):
        self.current_region: Optional[Region] = None
        self.data_loader = data_loader_instance or data_loader
    
    def set_current_region(self, region_id: str) -> bool:
        """
        Set the current region.
        
        Args:
            region_id: ID of the region to set as current
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.current_region = Region(region_id, self.data_loader)
            return True
        except ValueError:
            return False
    
    def get_current_region(self) -> Optional[Region]:
        """Get the current region"""
        return self.current_region
    
    def get_available_regions(self) -> List[str]:
        """Get list of all available regions"""
        return self.data_loader.list_regions()
    
    def get_accessible_regions(self, player) -> List[Dict[str, Any]]:
        """Get regions accessible to a player with their status"""
        regions = []
        all_regions = self.data_loader.list_regions()
        
        for region_id in all_regions:
            region = Region(region_id, self.data_loader)
            can_access, reason = region.can_player_access(player)
            
            regions.append({
                "id": region_id,
                "name": region.name,
                "level": region.level,
                "accessible": can_access,
                "reason": reason if not can_access else "",
                "current": region_id == player.current_region
            })
        
        return regions
    
    def can_travel_to(self, player, target_region_id: str) -> tuple[bool, str]:
        """
        Check if player can travel to a specific region.
        
        Args:
            player: Player instance
            target_region_id: ID of target region
            
        Returns:
            Tuple of (can_travel, reason)
        """
        try:
            target_region = Region(target_region_id, self.data_loader)
        except ValueError:
            return False, "Region not found"
        
        # Check if player can access the region
        can_access, reason = target_region.can_player_access(player)
        if not can_access:
            return False, reason
        
        # Check travel cost
        travel_cost = target_region.get_travel_cost()
        required_gold = travel_cost.get("gold", 0)
        if player.gold < required_gold:
            return False, f"Not enough gold. Requires {required_gold} gold"
        
        required_items = travel_cost.get("items", [])
        for item_requirement in required_items:
            item_id = item_requirement.get("item")
            quantity = item_requirement.get("quantity", 1)
            if not player.inventory.has_item(item_id, quantity):
                return False, f"Requires {quantity}x {item_id} to travel"
        
        return True, ""
    
    def travel_to_region(self, player, target_region_id: str) -> tuple[bool, str]:
        """
        Travel to a specific region.
        
        Args:
            player: Player instance
            target_region_id: ID of target region
            
        Returns:
            Tuple of (success, message)
        """
        can_travel, reason = self.can_travel_to(player, target_region_id)
        if not can_travel:
            return False, reason
        
        try:
            target_region = Region(target_region_id, self.data_loader)
        except ValueError:
            return False, "Region not found"
        
        # Pay travel cost
        travel_cost = target_region.get_travel_cost()
        required_gold = travel_cost.get("gold", 0)
        if required_gold > 0:
            player.spend_gold(required_gold)
        
        # Consume required items
        required_items = travel_cost.get("items", [])
        for item_requirement in required_items:
            item_id = item_requirement.get("item")
            quantity = item_requirement.get("quantity", 1)
            player.inventory.remove_item(item_id, quantity)
        
        # Set new region
        self.current_region = target_region
        player.current_region = target_region_id
        
        return True, f"Successfully traveled to {target_region.name}"
