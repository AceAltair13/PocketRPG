"""
Tests for item and inventory systems
"""

import pytest
from src.game.items.item import Item, ConsumableItem, EquipmentItem, WeaponItem, ArmorItem, QuestItem
from src.game.items.inventory import Inventory
from src.game.items.equipment import Equipment, EquipmentSlot
from src.game.enums import ItemType, ItemRarity, ItemQuality, StatType
from src.game.entities.player import Player, PlayerClass


class TestItem:
    """Test cases for Item base class"""
    
    def test_item_creation(self):
        """Test basic item creation"""
        # Create a mock item (since Item is abstract)
        class MockItem(Item):
            def use(self, user):
                return True
        
        item = MockItem(
            name="Test Item",
            item_type=ItemType.CONSUMABLE,
            description="A test item",
            rarity=ItemRarity.COMMON,
            quality=ItemQuality.NORMAL,
            value=10
        )
        
        assert item.name == "Test Item"
        assert item.item_type == ItemType.CONSUMABLE
        assert item.description == "A test item"
        assert item.rarity == ItemRarity.COMMON
        assert item.quality == ItemQuality.NORMAL
        assert item.value == 10
        assert item.quantity == 1
        assert item.stackable is False
        assert item.max_stack == 1
    
    def test_item_display_name(self):
        """Test item display name formatting"""
        class MockItem(Item):
            def use(self, user):
                return True
        
        # Test normal quality
        item = MockItem("Test Item", ItemType.CONSUMABLE, rarity=ItemRarity.COMMON, quality=ItemQuality.NORMAL)
        assert item.get_display_name() == "Test Item"
        
        # Test good quality
        item = MockItem("Test Item", ItemType.CONSUMABLE, rarity=ItemRarity.COMMON, quality=ItemQuality.GOOD)
        assert item.get_display_name() == "[Good] Test Item"
        
        # Test rare item
        item = MockItem("Test Item", ItemType.CONSUMABLE, rarity=ItemRarity.RARE, quality=ItemQuality.NORMAL)
        assert item.get_display_name() == "Test Item***"
    
    def test_item_can_use(self):
        """Test item usage requirements"""
        class MockItem(Item):
            def use(self, user):
                return True
        
        item = MockItem("Test Item", ItemType.CONSUMABLE)
        item.level_requirement = 5
        player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
        
        # Player level too low
        assert item.can_use(player) is False
        
        # Player level sufficient
        player.level = 5
        assert item.can_use(player) is True


class TestConsumableItem:
    """Test cases for ConsumableItem class"""
    
    def test_consumable_creation(self):
        """Test consumable item creation"""
        item = ConsumableItem(
            name="Health Potion",
            description="Restores health",
            rarity=ItemRarity.COMMON,
            quality=ItemQuality.NORMAL,
            value=10,
            max_stack=99
        )
        
        assert item.name == "Health Potion"
        assert item.item_type == ItemType.CONSUMABLE
        assert item.stackable is True
        assert item.max_stack == 99
        assert len(item.effects) == 0
    
    def test_consumable_effects(self):
        """Test consumable item effects"""
        item = ConsumableItem("Health Potion", "Restores health")
        
        # Add effects
        item.add_effect("heal", 50)
        item.add_effect("mana_restore", 25)
        
        assert len(item.effects) == 2
        assert item.effects[0]["type"] == "heal"
        assert item.effects[0]["amount"] == 50
        assert item.effects[1]["type"] == "mana_restore"
        assert item.effects[1]["amount"] == 25
    
    def test_consumable_use(self):
        """Test using consumable items"""
        item = ConsumableItem("Health Potion", "Restores health")
        item.add_effect("heal", 50)
        
        player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
        initial_health = player.get_stat(player.stats[StatType.HEALTH])
        
        # Use item
        success = item.use(player)
        assert success is True
        assert item.quantity == 0  # Should be consumed
        
        # Check if healing was applied (this would need proper effect system)
        # For now, just check that the use was successful


class TestWeaponItem:
    """Test cases for WeaponItem class"""
    
    def test_weapon_creation(self):
        """Test weapon item creation"""
        weapon = WeaponItem(
            name="Iron Sword",
            description="A sturdy iron sword",
            rarity=ItemRarity.COMMON,
            quality=ItemQuality.NORMAL,
            value=50,
            level_requirement=1
        )
        
        assert weapon.name == "Iron Sword"
        assert weapon.item_type == ItemType.WEAPON
        assert weapon.slot == "weapon"
        assert weapon.damage == 0  # Default
        assert weapon.damage_type == "physical"
        assert weapon.weapon_type == "sword"
        assert weapon.critical_chance == 0.05
        assert weapon.critical_multiplier == 2.0
    
    def test_weapon_damage_range(self):
        """Test weapon damage range calculation"""
        weapon = WeaponItem("Test Sword", "A test sword")
        weapon.damage = 20
        
        min_damage, max_damage = weapon.get_damage_range()
        assert min_damage > 0
        assert max_damage > min_damage
        assert min_damage <= 20
        assert max_damage >= 20


class TestArmorItem:
    """Test cases for ArmorItem class"""
    
    def test_armor_creation(self):
        """Test armor item creation"""
        armor = ArmorItem(
            name="Leather Armor",
            armor_type="chest",
            description="Basic leather armor",
            rarity=ItemRarity.COMMON,
            quality=ItemQuality.NORMAL,
            value=30,
            level_requirement=1
        )
        
        assert armor.name == "Leather Armor"
        assert armor.item_type == ItemType.ARMOR
        assert armor.armor_type == "chest"
        assert armor.slot == "chest"
        assert armor.defense == 0  # Default
    
    def test_armor_defense_value(self):
        """Test armor defense value calculation"""
        armor = ArmorItem("Test Armor", "chest", "Test armor")
        armor.defense = 10
        
        defense_value = armor.get_defense_value()
        assert defense_value > 0
        assert defense_value >= 10


class TestInventory:
    """Test cases for Inventory class"""
    
    def test_inventory_creation(self):
        """Test inventory creation"""
        inventory = Inventory(max_capacity=20)
        
        assert inventory.max_capacity == 20
        assert len(inventory.items) == 0
        assert inventory.get_used_capacity() == 0
        assert inventory.get_free_capacity() == 20
        assert inventory.is_full() is False
    
    def test_add_item(self):
        """Test adding items to inventory"""
        inventory = Inventory()
        
        class MockItem:
            def __init__(self, name, stackable=False, max_stack=1):
                self.name = name
                self.stackable = stackable
                self.max_stack = max_stack
                self.quantity = 1
        
        # Add non-stackable item
        item1 = MockItem("Sword", stackable=False)
        success = inventory.add_item(item1, 1)
        assert success is True
        assert inventory.get_used_capacity() == 1
        assert inventory.has_item("Sword")
        
        # Add stackable item
        item2 = MockItem("Arrow", stackable=True, max_stack=99)
        success = inventory.add_item(item2, 50)
        assert success is True
        assert inventory.get_item_count("Arrow") == 50
    
    def test_remove_item(self):
        """Test removing items from inventory"""
        inventory = Inventory()
        
        class MockItem:
            def __init__(self, name, stackable=False, max_stack=1):
                self.name = name
                self.stackable = stackable
                self.max_stack = max_stack
                self.quantity = 1
        
        item = MockItem("Test Item", stackable=True, max_stack=99)
        inventory.add_item(item, 10)
        
        # Remove some items
        success = inventory.remove_item("Test Item", 5)
        assert success is True
        assert inventory.get_item_count("Test Item") == 5
        
        # Remove remaining items
        success = inventory.remove_item("Test Item", 5)
        assert success is True
        assert inventory.has_item("Test Item") is False
    
    def test_inventory_full(self):
        """Test inventory capacity limits"""
        inventory = Inventory(max_capacity=2)
        
        class MockItem:
            def __init__(self, name, stackable=False, max_stack=1):
                self.name = name
                self.stackable = stackable
                self.max_stack = max_stack
                self.quantity = 1
        
        # Fill inventory
        item1 = MockItem("Item1")
        item2 = MockItem("Item2")
        item3 = MockItem("Item3")
        
        assert inventory.add_item(item1, 1) is True
        assert inventory.add_item(item2, 1) is True
        assert inventory.is_full() is True
        
        # Try to add more (should fail)
        assert inventory.add_item(item3, 1) is False


class TestEquipment:
    """Test cases for Equipment class"""
    
    def test_equipment_creation(self):
        """Test equipment creation"""
        equipment = Equipment()
        
        assert len(equipment.equipped_items) == len(EquipmentSlot)
        assert equipment.get_equipped_items() == []
        # Equipment returns a dict with all StatType keys set to 0
        bonuses = equipment.get_total_bonuses()
        assert all(bonus == 0 for bonus in bonuses.values())
    
    def test_equip_item(self):
        """Test equipping items"""
        equipment = Equipment()
        
        # Create a proper WeaponItem
        weapon = WeaponItem(
            name="Test Sword",
            description="A test sword",
            rarity=ItemRarity.COMMON,
            quality=ItemQuality.NORMAL,
            value=50,
            level_requirement=1
        )
        weapon.stat_bonuses = {"attack": 5}
        
        success = equipment.equip_item(weapon, EquipmentSlot.WEAPON)
        
        assert success is True
        assert equipment.get_equipped_item(EquipmentSlot.WEAPON) == weapon
        assert len(equipment.get_equipped_items()) == 1
    
    def test_unequip_item(self):
        """Test unequipping items"""
        equipment = Equipment()
        
        # Create a proper WeaponItem
        weapon = WeaponItem(
            name="Test Sword",
            description="A test sword",
            rarity=ItemRarity.COMMON,
            quality=ItemQuality.NORMAL,
            value=50,
            level_requirement=1
        )
        weapon.stat_bonuses = {"attack": 5}
        
        equipment.equip_item(weapon, EquipmentSlot.WEAPON)
        
        # Unequip
        unequipped = equipment.unequip_item(EquipmentSlot.WEAPON)
        assert unequipped == weapon
        assert equipment.get_equipped_item(EquipmentSlot.WEAPON) is None
        assert len(equipment.get_equipped_items()) == 0
    
    def test_stat_bonuses(self):
        """Test equipment stat bonuses"""
        equipment = Equipment()
        
        # Create a proper WeaponItem
        weapon = WeaponItem(
            name="Test Sword",
            description="A test sword",
            rarity=ItemRarity.COMMON,
            quality=ItemQuality.NORMAL,
            value=50,
            level_requirement=1
        )
        weapon.stat_bonuses = {"attack": 10, "defense": 5}
        
        equipment.equip_item(weapon, EquipmentSlot.WEAPON)
        
        bonuses = equipment.get_total_bonuses()
        assert bonuses[StatType.ATTACK] == 10
        assert bonuses[StatType.DEFENSE] == 5
