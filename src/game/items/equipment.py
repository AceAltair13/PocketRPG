"""
Equipment system for managing equipped items and stat bonuses
Handles equipment slots and stat calculations
"""

from typing import Dict, List, Optional, Any
from .item import Item, ItemType, EquipmentItem
from ..entities.entity import StatType
from ..enums import EquipmentSlot


class Equipment:
    """
    Equipment system for managing equipped items and their stat bonuses.
    Handles equipment slots, stat calculations, and equipment swapping.
    """
    
    def __init__(self):
        # Equipment slots
        self.equipped_items: Dict[EquipmentSlot, Optional[EquipmentItem]] = {
            slot: None for slot in EquipmentSlot
        }
        
        # Equipment-specific properties
        self.set_bonuses: Dict[str, int] = {}  # Set bonuses from equipment sets
    
    def equip_item(self, item: EquipmentItem, slot: Optional[EquipmentSlot] = None) -> bool:
        """
        Equip an item to a specific slot.
        Returns True if successful, False if slot is occupied or item can't be equipped.
        """
        if not isinstance(item, EquipmentItem):
            return False
        
        # Determine the slot if not specified
        if slot is None:
            slot = self._get_item_slot(item)
        
        if slot is None:
            return False
        
        # Check if slot is already occupied
        if self.equipped_items[slot] is not None:
            return False
        
        # Equip the item
        self.equipped_items[slot] = item
        self._update_set_bonuses()
        
        return True
    
    def unequip_item(self, slot: EquipmentSlot) -> Optional[EquipmentItem]:
        """
        Unequip an item from a specific slot.
        Returns the unequipped item or None if slot is empty.
        """
        item = self.equipped_items[slot]
        if item is not None:
            self.equipped_items[slot] = None
            self._update_set_bonuses()
        return item
    
    def get_equipped_item(self, slot: EquipmentSlot) -> Optional[EquipmentItem]:
        """Get the item equipped in a specific slot"""
        return self.equipped_items[slot]
    
    def get_equipped_items(self) -> List[EquipmentItem]:
        """Get all equipped items"""
        return [item for item in self.equipped_items.values() if item is not None]
    
    def get_total_bonuses(self) -> Dict[StatType, int]:
        """Get total stat bonuses from all equipped items"""
        bonuses = {stat: 0 for stat in StatType}
        
        # Add bonuses from equipped items
        for item in self.get_equipped_items():
            if hasattr(item, 'stat_bonuses'):
                for stat_name, bonus in item.stat_bonuses.items():
                    try:
                        stat_type = StatType(stat_name)
                        bonuses[stat_type] += bonus
                    except ValueError:
                        # Handle custom stats if needed
                        pass
        
        # Add set bonuses
        for stat_name, bonus in self.set_bonuses.items():
            try:
                stat_type = StatType(stat_name)
                bonuses[stat_type] += bonus
            except ValueError:
                # Handle custom stats if needed
                pass
        
        return bonuses
    
    def get_equipment_set_bonuses(self) -> Dict[str, int]:
        """Get bonuses from equipment sets"""
        return self.set_bonuses.copy()
    
    def get_equipment_summary(self) -> Dict[str, Any]:
        """Get a summary of all equipped items"""
        summary = {}
        for slot, item in self.equipped_items.items():
            if item is not None:
                summary[slot.value] = {
                    'name': item.name,
                    'type': item.item_type.value,
                    'rarity': item.rarity.value,
                    'quality': item.quality.value,
                    'stat_bonuses': item.stat_bonuses.copy() if hasattr(item, 'stat_bonuses') else {}
                }
            else:
                summary[slot.value] = None
        
        return summary
    
    def get_equipment_value(self) -> int:
        """Get the total value of all equipped items"""
        total_value = 0
        for item in self.get_equipped_items():
            total_value += item.value
        return total_value
    
    def get_equipment_durability(self) -> Dict[str, int]:
        """Get durability information for all equipped items"""
        durability_info = {}
        for slot, item in self.equipped_items.items():
            if item is not None and hasattr(item, 'durability'):
                durability_info[slot.value] = {
                    'current': item.durability,
                    'max': item.max_durability,
                    'percentage': (item.durability / item.max_durability) * 100 if item.max_durability > 0 else 0
                }
        return durability_info
    
    def repair_all_equipment(self, amount: int = None) -> int:
        """Repair all equipped items"""
        repaired_items = 0
        for item in self.get_equipped_items():
            if hasattr(item, 'repair'):
                item.repair(amount)
                repaired_items += 1
        return repaired_items
    
    def damage_all_equipment(self, amount: int = 1) -> None:
        """Damage all equipped items (e.g., from combat)"""
        for item in self.get_equipped_items():
            if hasattr(item, 'damage'):
                item.damage(amount)
    
    def get_broken_equipment(self) -> List[EquipmentItem]:
        """Get list of broken equipped items"""
        broken_items = []
        for item in self.get_equipped_items():
            if hasattr(item, 'is_broken') and item.is_broken():
                broken_items.append(item)
        return broken_items
    
    def can_equip_item(self, item: EquipmentItem, slot: Optional[EquipmentSlot] = None) -> bool:
        """Check if an item can be equipped to a specific slot"""
        if not isinstance(item, EquipmentItem):
            return False
        
        # Determine the slot if not specified
        if slot is None:
            slot = self._get_item_slot(item)
        
        if slot is None:
            return False
        
        # Check if slot is already occupied
        return self.equipped_items[slot] is None
    
    def _get_item_slot(self, item: EquipmentItem) -> Optional[EquipmentSlot]:
        """Determine which slot an item should be equipped to"""
        if item.item_type == ItemType.WEAPON:
            return EquipmentSlot.WEAPON
        elif item.item_type == ItemType.ARMOR:
            if hasattr(item, 'slot'):
                slot_mapping = {
                    'head': EquipmentSlot.HEAD,
                    'chest': EquipmentSlot.CHEST,
                    'legs': EquipmentSlot.LEGS,
                    'feet': EquipmentSlot.FEET,
                    'hands': EquipmentSlot.HANDS
                }
                return slot_mapping.get(item.slot)
        elif item.item_type == ItemType.ACCESSORY:
            # For accessories, find an empty slot
            accessory_slots = [EquipmentSlot.RING_1, EquipmentSlot.RING_2, EquipmentSlot.NECKLACE, EquipmentSlot.ACCESSORY]
            for slot in accessory_slots:
                if self.equipped_items[slot] is None:
                    return slot
        
        return None
    
    def _update_set_bonuses(self) -> None:
        """Update set bonuses based on equipped items"""
        self.set_bonuses.clear()
        
        # Count items by set (this would need set information in items)
        # For now, we'll implement a simple example
        set_counts = {}
        
        for item in self.get_equipped_items():
            if hasattr(item, 'set_name') and item.set_name:
                set_name = item.set_name
                set_counts[set_name] = set_counts.get(set_name, 0) + 1
        
        # Apply set bonuses based on counts
        for set_name, count in set_counts.items():
            if count >= 2:
                # 2-piece set bonus
                self.set_bonuses['attack'] = self.set_bonuses.get('attack', 0) + 5
            if count >= 4:
                # 4-piece set bonus
                self.set_bonuses['defense'] = self.set_bonuses.get('defense', 0) + 10
            if count >= 6:
                # 6-piece set bonus
                self.set_bonuses['health'] = self.set_bonuses.get('health', 0) + 50
    
    def swap_equipment(self, item: EquipmentItem, slot: EquipmentSlot) -> Optional[EquipmentItem]:
        """
        Swap an item with the currently equipped item in a slot.
        Returns the previously equipped item.
        """
        old_item = self.equipped_items[slot]
        self.equipped_items[slot] = item
        self._update_set_bonuses()
        return old_item
    
    def get_equipment_display(self) -> str:
        """Get a formatted display of all equipped items"""
        lines = ["Equipped Items:"]
        
        slot_names = {
            EquipmentSlot.WEAPON: "Weapon",
            EquipmentSlot.HEAD: "Head",
            EquipmentSlot.CHEST: "Chest",
            EquipmentSlot.LEGS: "Legs",
            EquipmentSlot.FEET: "Feet",
            EquipmentSlot.HANDS: "Hands",
            EquipmentSlot.RING_1: "Ring 1",
            EquipmentSlot.RING_2: "Ring 2",
            EquipmentSlot.NECKLACE: "Necklace",
            EquipmentSlot.ACCESSORY: "Accessory"
        }
        
        for slot, item in self.equipped_items.items():
            slot_name = slot_names.get(slot, slot.value)
            if item is not None:
                lines.append(f"  {slot_name}: {item.get_display_name()}")
            else:
                lines.append(f"  {slot_name}: [Empty]")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert equipment to dictionary for serialization"""
        return {
            'equipped_items': {
                slot.value: item.to_dict() if item is not None else None
                for slot, item in self.equipped_items.items()
            },
            'set_bonuses': self.set_bonuses
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load equipment from dictionary"""
        # This would need proper item reconstruction
        # For now, we'll store the raw data
        self.set_bonuses = data.get('set_bonuses', {})
        
        # Recreate equipped items from dictionary
        equipped_data = data.get('equipped_items', {})
        for slot_name, item_data in equipped_data.items():
            try:
                slot = EquipmentSlot(slot_name)
                if item_data is not None:
                    # This would need proper item reconstruction
                    self.equipped_items[slot] = item_data
                else:
                    self.equipped_items[slot] = None
            except ValueError:
                continue
    
    def __str__(self) -> str:
        """String representation of the equipment"""
        return self.get_equipment_display()
    
    def __len__(self) -> int:
        """Return the number of equipped items"""
        return len(self.get_equipped_items())
