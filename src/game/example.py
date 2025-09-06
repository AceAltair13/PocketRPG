"""
Example usage of the RPG game classes
Demonstrates how to create and use players, enemies, items, and combat
"""

from .player import Player, PlayerClass
from .enemy import Enemy, EnemyType, EnemyBehavior
from .item import CommonItems
from .combat import Combat
from .effect import CommonEffects
from .entity import StatType


def create_example_player() -> Player:
    """Create an example player"""
    player = Player("Hero", PlayerClass.WARRIOR, level=5)
    player.set_user_id(12345)  # Discord user ID
    
    # Add some items to inventory
    player.inventory.add_item(CommonItems.health_potion(), 3)
    player.inventory.add_item(CommonItems.mana_potion(), 2)
    player.inventory.add_item(CommonItems.iron_sword())
    player.inventory.add_item(CommonItems.leather_armor())
    
    # Equip items
    sword = CommonItems.iron_sword()
    armor = CommonItems.leather_armor()
    player.equipment.equip_item(sword)
    player.equipment.equip_item(armor)
    
    return player


def create_example_enemy() -> Enemy:
    """Create an example enemy"""
    enemy = Enemy("Goblin Warrior", EnemyType.NORMAL, level=3, behavior=EnemyBehavior.AGGRESSIVE)
    
    # Add some loot
    enemy.add_loot_item("Health Potion", 0.3, 1)  # 30% chance to drop 1 health potion
    enemy.add_loot_item("Gold", 0.8, 10)  # 80% chance to drop 10 gold
    
    return enemy


def run_example_combat():
    """Run an example combat scenario"""
    print("=== PocketRPG Combat Example ===\n")
    
    # Create participants
    player = create_example_player()
    enemy = create_example_enemy()
    
    print(f"Player: {player}")
    print(f"Enemy: {enemy}")
    print()
    
    # Create combat
    combat = Combat([player, enemy])
    
    print("Starting combat...")
    print(combat.get_combat_status())
    print()
    
    # Run combat
    result = combat.start_combat()
    
    print(f"Combat Result: {result.value}")
    print()
    
    # Show final status
    print("Final Status:")
    print(f"Player: {player}")
    print(f"Enemy: {enemy}")
    print()
    
    # Show combat log
    print("Combat Log:")
    for log_entry in combat.get_combat_log():
        print(f"  {log_entry}")
    
    # Show loot if player won
    if result.value == "victory":
        print("\nLoot Dropped:")
        loot = enemy.generate_loot()
        for item in loot:
            print(f"  - {item['quantity']}x {item['item_name']}")
        
        # Add experience and gold
        player.add_experience(enemy.experience_reward)
        player.add_gold(enemy.gold_reward)
        print(f"\nGained {enemy.experience_reward} experience and {enemy.gold_reward} gold!")
    
    return result


def demonstrate_effects():
    """Demonstrate status effects"""
    print("\n=== Status Effects Example ===\n")
    
    player = create_example_player()
    print(f"Player before effects: {player}")
    
    # Apply some effects
    strength_buff = CommonEffects.strength_buff(duration=3, power=10)
    poison = CommonEffects.poison(duration=5, damage=5)
    
    player.add_status_effect(strength_buff)
    player.add_status_effect(poison)
    
    print(f"Player after applying effects: {player}")
    print(f"Attack stat: {player.get_stat(StatType.ATTACK)}")
    
    # Process effects for a few turns
    for turn in range(3):
        print(f"\nTurn {turn + 1}:")
        player.process_status_effects()
        print(f"Player: {player}")
        print(f"Active effects: {[effect.name for effect in player.status_effects]}")


def demonstrate_inventory():
    """Demonstrate inventory system"""
    print("\n=== Inventory Example ===\n")
    
    player = create_example_player()
    
    print("Player Inventory:")
    print(player.inventory)
    print()
    
    print("Player Equipment:")
    print(player.equipment)
    print()
    
    print("Player Stats (including equipment bonuses):")
    effective_stats = player.get_effective_stats()
    for stat, value in effective_stats.items():
        print(f"  {stat.value}: {value}")


if __name__ == "__main__":
    # Run examples
    run_example_combat()
    demonstrate_effects()
    demonstrate_inventory()
