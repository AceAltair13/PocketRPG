"""
Inventory system for managing player items
Handles item storage, stacking, and basic operations
"""

from typing import Dict, List, Optional, Any
from .item import Item


class Inventory:
    """
    Inventory system for storing and managing items.
    Handles item stacking, capacity limits, and basic operations.
    """
    
    def __init__(self, max_capacity: int = 50):
        self.max_capacity: int = max_capacity
        self.items: Dict[str, Item] = {}  # item_name -> Item
        self.item_order: List[str] = []  # Maintain order of items
    
    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """
        Add an item to the inventory.
        Returns True if successful, False if inventory is full.
        """
        if quantity <= 0:
            return False
        
        # Check if we can add the item
        if not self._can_add_item(item, quantity):
            return False
        
        # If item is stackable and already exists, add to existing stack
        if item.stackable and item.name in self.items:
            existing_item = self.items[item.name]
            if existing_item.quantity + quantity <= existing_item.max_stack:
                existing_item.quantity += quantity
                return True
            else:
                # Partial stack, add what we can
                can_add = existing_item.max_stack - existing_item.quantity
                existing_item.quantity = existing_item.max_stack
                return self.add_item(item, quantity - can_add)
        
        # Add new item
        new_item = self._create_item_copy(item)
        new_item.quantity = quantity
        self.items[item.name] = new_item
        self.item_order.append(item.name)
        
        return True
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """
        Remove an item from the inventory.
        Returns True if successful, False if item not found or insufficient quantity.
        """
        if item_name not in self.items:
            return False
        
        item = self.items[item_name]
        
        if item.quantity < quantity:
            return False
        
        item.quantity -= quantity
        
        # Remove item if quantity reaches 0
        if item.quantity <= 0:
            del self.items[item_name]
            if item_name in self.item_order:
                self.item_order.remove(item_name)
        
        return True
    
    def get_item(self, item_name: str) -> Optional[Item]:
        """Get an item from the inventory by name"""
        return self.items.get(item_name)
    
    def has_item(self, item_name: str, quantity: int = 1) -> bool:
        """Check if inventory has a specific item in the required quantity"""
        if item_name not in self.items:
            return False
        return self.items[item_name].quantity >= quantity
    
    def get_item_count(self, item_name: str) -> int:
        """Get the quantity of a specific item"""
        if item_name not in self.items:
            return 0
        return self.items[item_name].quantity
    
    def get_all_items(self) -> List[Item]:
        """Get all items in the inventory"""
        return [self.items[name] for name in self.item_order if name in self.items]
    
    def get_items_by_type(self, item_type) -> List[Item]:
        """Get all items of a specific type"""
        return [item for item in self.get_all_items() if item.item_type == item_type]
    
    def get_consumables(self) -> List[Item]:
        """Get all consumable items"""
        from .item import ItemType
        return self.get_items_by_type(ItemType.CONSUMABLE)
    
    def get_equipment(self) -> List[Item]:
        """Get all equipment items"""
        from .item import ItemType
        equipment_types = [ItemType.WEAPON, ItemType.ARMOR, ItemType.ACCESSORY]
        return [item for item in self.get_all_items() if item.item_type in equipment_types]
    
    def use_item(self, item_name: str, user) -> bool:
        """Use an item from the inventory"""
        if not self.has_item(item_name):
            return False
        
        item = self.items[item_name]
        
        if not item.can_use(user):
            return False
        
        # Use the item
        success = item.use(user)
        
        # Remove item if it was consumed
        if success and item.item_type.value == "consumable":
            self.remove_item(item_name, 1)
        
        return success
    
    def get_total_value(self) -> int:
        """Get the total value of all items in the inventory"""
        total = 0
        for item in self.get_all_items():
            total += item.value * item.quantity
        return total
    
    def get_used_capacity(self) -> int:
        """Get the number of item slots used"""
        return len(self.items)
    
    def get_free_capacity(self) -> int:
        """Get the number of free item slots"""
        return self.max_capacity - self.get_used_capacity()
    
    def is_full(self) -> bool:
        """Check if the inventory is full"""
        return self.get_used_capacity() >= self.max_capacity
    
    def can_add_item(self, item: Item, quantity: int = 1) -> bool:
        """Check if an item can be added to the inventory"""
        return self._can_add_item(item, quantity)
    
    def _can_add_item(self, item: Item, quantity: int) -> bool:
        """Internal method to check if item can be added"""
        # If item is stackable and already exists, check if we can add to existing stack
        if item.stackable and item.name in self.items:
            existing_item = self.items[item.name]
            return existing_item.quantity + quantity <= existing_item.max_stack
        
        # If inventory is full and item is not stackable, can't add
        if self.is_full() and not item.stackable:
            return False
        
        # If inventory is full and item is stackable but doesn't exist, can't add
        if self.is_full() and item.stackable and item.name not in self.items:
            return False
        
        return True
    
    def _create_item_copy(self, item: Item) -> Item:
        """Create a copy of an item"""
        # This is a simplified copy method
        # In a real implementation, you might want to use deepcopy or implement __copy__
        import copy
        return copy.deepcopy(item)
    
    def sort_items(self, sort_by: str = "name") -> None:
        """Sort items in the inventory"""
        if sort_by == "name":
            self.item_order.sort(key=lambda name: self.items[name].name.lower())
        elif sort_by == "type":
            self.item_order.sort(key=lambda name: self.items[name].item_type.value)
        elif sort_by == "rarity":
            from .item import ItemRarity
            rarity_order = {rarity: i for i, rarity in enumerate(ItemRarity)}
            self.item_order.sort(key=lambda name: rarity_order.get(self.items[name].rarity, 0))
        elif sort_by == "value":
            self.item_order.sort(key=lambda name: self.items[name].value, reverse=True)
    
    def clear(self) -> None:
        """Clear all items from the inventory"""
        self.items.clear()
        self.item_order.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert inventory to dictionary for serialization"""
        return {
            'max_capacity': self.max_capacity,
            'items': {name: item.to_dict() for name, item in self.items.items()},
            'item_order': self.item_order
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load inventory from dictionary"""
        self.max_capacity = data.get('max_capacity', 50)
        self.item_order = data.get('item_order', [])
        
        # Recreate items from dictionary
        self.items = {}
        for name, item_data in data.get('items', {}).items():
            # This would need proper item reconstruction based on item_type
            # For now, we'll store the raw data
            self.items[name] = item_data
    
    def __str__(self) -> str:
        """String representation of the inventory"""
        if not self.items:
            return "Inventory is empty"
        
        lines = [f"Inventory ({self.get_used_capacity()}/{self.max_capacity}):"]
        for item in self.get_all_items():
            lines.append(f"  - {item}")
        
        return "\n".join(lines)
    
    def __len__(self) -> int:
        """Return the number of different items in the inventory"""
        return len(self.items)
    
    def __contains__(self, item_name: str) -> bool:
        """Check if an item is in the inventory"""
        return item_name in self.items
