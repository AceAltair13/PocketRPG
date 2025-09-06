"""
Data loader for game content
Handles loading of regions, activities, items, and enemies from JSON files
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class DataLoader:
    """
    Loads game data from JSON files in the data directory.
    Provides a clean interface for accessing game content.
    """
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self._cache = {}
    
    def load_region(self, region_id: str) -> Optional[Dict[str, Any]]:
        """Load a region by ID"""
        if region_id in self._cache.get('regions', {}):
            return self._cache['regions'][region_id]
        
        file_path = self.data_path / "regions" / f"{region_id}.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cache the data
            if 'regions' not in self._cache:
                self._cache['regions'] = {}
            self._cache['regions'][region_id] = data
            
            return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading region {region_id}: {e}")
            return None
    
    def load_activity(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """Load an activity by ID"""
        if activity_id in self._cache.get('activities', {}):
            return self._cache['activities'][activity_id]
        
        file_path = self.data_path / "activities" / f"{activity_id}.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cache the data
            if 'activities' not in self._cache:
                self._cache['activities'] = {}
            self._cache['activities'][activity_id] = data
            
            return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading activity {activity_id}: {e}")
            return None
    
    def load_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Load an item by ID"""
        if item_id in self._cache.get('items', {}):
            return self._cache['items'][item_id]
        
        file_path = self.data_path / "items" / f"{item_id}.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cache the data
            if 'items' not in self._cache:
                self._cache['items'] = {}
            self._cache['items'][item_id] = data
            
            return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading item {item_id}: {e}")
            return None
    
    def load_enemy(self, enemy_id: str) -> Optional[Dict[str, Any]]:
        """Load an enemy by ID"""
        if enemy_id in self._cache.get('enemies', {}):
            return self._cache['enemies'][enemy_id]
        
        file_path = self.data_path / "enemies" / f"{enemy_id}.json"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cache the data
            if 'enemies' not in self._cache:
                self._cache['enemies'] = {}
            self._cache['enemies'][enemy_id] = data
            
            return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading enemy {enemy_id}: {e}")
            return None
    
    def list_regions(self) -> List[str]:
        """List all available region IDs"""
        regions_dir = self.data_path / "regions"
        if not regions_dir.exists():
            return []
        
        return [f.stem for f in regions_dir.glob("*.json")]
    
    def list_activities(self) -> List[str]:
        """List all available activity IDs"""
        activities_dir = self.data_path / "activities"
        if not activities_dir.exists():
            return []
        
        return [f.stem for f in activities_dir.glob("*.json")]
    
    def list_items(self) -> List[str]:
        """List all available item IDs"""
        items_dir = self.data_path / "items"
        if not items_dir.exists():
            return []
        
        return [f.stem for f in items_dir.glob("*.json")]
    
    def list_enemies(self) -> List[str]:
        """List all available enemy IDs"""
        enemies_dir = self.data_path / "enemies"
        if not enemies_dir.exists():
            return []
        
        return [f.stem for f in enemies_dir.glob("*.json")]
    
    def get_enemies_for_region(self, region_id: str) -> List[str]:
        """Get all enemies that can spawn in a specific region"""
        enemies = []
        for enemy_id in self.list_enemies():
            enemy_data = self.load_enemy(enemy_id)
            if enemy_data and region_id in enemy_data.get('spawn_regions', []):
                enemies.append(enemy_id)
        return enemies
    
    def clear_cache(self):
        """Clear the data cache"""
        self._cache.clear()
    
    def reload_data(self):
        """Reload all data from files"""
        self.clear_cache()
        # Preload some common data
        for region_id in self.list_regions():
            self.load_region(region_id)
        for activity_id in self.list_activities():
            self.load_activity(activity_id)
        for item_id in self.list_items():
            self.load_item(item_id)
        for enemy_id in self.list_enemies():
            self.load_enemy(enemy_id)


# Global data loader instance
data_loader = DataLoader()
