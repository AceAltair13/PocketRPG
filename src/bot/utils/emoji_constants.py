"""
Emoji constants to reduce repetitive UIEmojis.get_ calls
"""

from ...utils.ui_emojis import UIEmojis


class Emojis:
    """Constants for commonly used emojis"""
    
    # UI Emojis
    CHARACTER = UIEmojis.get_ui('character')
    INVENTORY = UIEmojis.get_ui('inventory')
    STATS = UIEmojis.get_ui('stats')
    EXPLORE = UIEmojis.get_ui('explore')
    ATTACK = UIEmojis.get_ui('attack')
    DEFENSE = UIEmojis.get_ui('defense')
    SPEED = UIEmojis.get_ui('speed')
    MANA = UIEmojis.get_ui('mana')
    HEALTH = UIEmojis.get_ui('health')
    GOLD = UIEmojis.get_ui('gold')
    EQUIPMENT = UIEmojis.get_ui('equipment')
    LOCATION = UIEmojis.get_ui('location')
    INSPECT = UIEmojis.get_ui('inspect')
    
    # Status Emojis
    SUCCESS = UIEmojis.get_status('success')
    ERROR = UIEmojis.get_status('error')
    WARNING = UIEmojis.get_status('warning')
    INFO = UIEmojis.get_status('info')
    COMPLETE = UIEmojis.get_status('complete')
    
    # Effect Emojis
    BUFF = UIEmojis.get_effect('buff')
    DEBUFF = UIEmojis.get_effect('debuff')
    HEAL = UIEmojis.get_effect('heal')
    DAMAGE = UIEmojis.get_effect('damage')
    
    # Item Type Emojis
    CONSUMABLE = UIEmojis.get_item_type('consumable')
    MATERIAL = UIEmojis.get_item_type('material')
    WEAPON = UIEmojis.get_item_type('weapon')
    ARMOR = UIEmojis.get_item_type('armor')
    ACCESSORY = UIEmojis.get_item_type('accessory')
    
    # Rarity Emojis
    COMMON = UIEmojis.get_rarity('common')
    UNCOMMON = UIEmojis.get_rarity('uncommon')
    RARE = UIEmojis.get_rarity('rare')
    EPIC = UIEmojis.get_rarity('epic')
    LEGENDARY = UIEmojis.get_rarity('legendary')
    
    # Foraging Emojis
    GRID_EMPTY = UIEmojis.get_foraging('grid_empty')
    GRID_FOUND = UIEmojis.get_foraging('grid_found')
    GRID_MISS = UIEmojis.get_foraging('grid_miss')
    
    # Player Class Emojis
    WARRIOR = UIEmojis.get_player_class('warrior')
    MAGE = UIEmojis.get_player_class('mage')
    ROGUE = UIEmojis.get_player_class('rogue')
    CLERIC = UIEmojis.get_player_class('cleric')
