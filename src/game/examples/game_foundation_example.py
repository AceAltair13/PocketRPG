"""
Example demonstrating the game foundation systems
Shows player creation, region system, and data loading
"""

from ..player_creation import PlayerCreation
from ..region import Region, RegionManager
from ..enums import PlayerClass
from ..data_loader import data_loader


def demonstrate_player_creation():
    """Demonstrate player creation system"""
    print("=== Player Creation Demo ===\n")
    
    # Create a new player
    player = PlayerCreation.create_player("TestHero", PlayerClass.WARRIOR)
    
    print(f"Created player: {player}")
    print(f"Player class: {player.player_class.value}")
    print(f"Starting region: {player.current_region}")
    print(f"Starting gold: {player.gold}")
    print(f"Equipped weapon: {player.equipment.get_equipped_item(player.equipment.equipped_items.keys().__iter__().__next__())}")
    print()
    
    return player


def demonstrate_region_system():
    """Demonstrate region system"""
    print("=== Region System Demo ===\n")
    
    # Create region manager
    region_manager = RegionManager()
    
    # Set starting region
    region_manager.set_current_region("grasslands")
    current_region = region_manager.get_current_region()
    
    print(f"Current region: {current_region.name}")
    print(f"Description: {current_region.description}")
    print(f"Region level: {current_region.level}")
    print(f"Available activities: {', '.join(current_region.available_activities)}")
    print(f"Loot multiplier: {current_region.loot_multiplier}")
    print(f"Enemy level bonus: {current_region.enemy_level_bonus}")
    print()
    
    return region_manager


def demonstrate_data_loading():
    """Demonstrate data loading system"""
    print("=== Data Loading Demo ===\n")
    
    # List available content
    print(f"Available regions: {data_loader.list_regions()}")
    print(f"Available activities: {data_loader.list_activities()}")
    print(f"Available items: {data_loader.list_items()}")
    print(f"Available enemies: {data_loader.list_enemies()}")
    print()
    
    # Load specific data
    foraging_data = data_loader.load_activity("foraging")
    if foraging_data:
        print(f"Foraging activity: {foraging_data['name']}")
        print(f"Description: {foraging_data['description']}")
        print(f"Energy cost: {foraging_data['energy_cost']}")
        print(f"Possible rewards: {len(foraging_data['possible_rewards'])}")
        print()
    
    # Load enemy data
    wolf_data = data_loader.load_enemy("grassland_wolf")
    if wolf_data:
        print(f"Enemy: {wolf_data['name']}")
        print(f"Type: {wolf_data['type']}")
        print(f"Base level: {wolf_data['base_level']}")
        print(f"Experience reward: {wolf_data['experience_reward']}")
        print()


def demonstrate_integration():
    """Demonstrate how all systems work together"""
    print("=== System Integration Demo ===\n")
    
    # Create player
    player = PlayerCreation.create_player("Adventurer", PlayerClass.ROGUE)
    
    # Create region manager
    region_manager = RegionManager()
    region_manager.set_current_region("grasslands")
    
    # Check what the player can do in the current region
    current_region = region_manager.get_current_region()
    print(f"{player.name} is in {current_region.name}")
    print(f"Available activities: {', '.join(current_region.available_activities)}")
    
    # Check available enemies
    available_enemies = current_region.get_available_enemies()
    print(f"Enemies in this region: {available_enemies}")
    
    # Show player's starting equipment
    equipped_weapon = None
    for slot, item in player.equipment.equipped_items.items():
        if item is not None:
            equipped_weapon = item
            break
    
    if equipped_weapon:
        print(f"Starting weapon: {equipped_weapon.name} (Damage: {equipped_weapon.damage})")
    
    print()


if __name__ == "__main__":
    # Run all demonstrations
    player = demonstrate_player_creation()
    region_manager = demonstrate_region_system()
    demonstrate_data_loading()
    demonstrate_integration()
    
    print("=== Foundation Systems Ready! ===")
    print("The game foundation is set up and ready for incremental development.")
    print("You can now add more regions, activities, items, and enemies by adding JSON files to the data/ folder.")
