"""
Simple UI emoji utility for hardcoded UI elements
"""

class UIEmojis:
    """Simple class with hardcoded UI emojis"""
    
    # Rarity emojis
    RARITY = {
        'common': '⚪',
        'uncommon': '🟢', 
        'rare': '🔵',
        'epic': '🟣',
        'legendary': '🟡'
    }
    
    # Item type emojis
    ITEM_TYPE = {
        'consumable': '🧪',
        'material': '📦',
        'weapon': '⚔️',
        'armor': '🛡️',
        'accessory': '💍',
        'quest': '📜',
        'misc': '🔮'
    }
    
    # UI element emojis
    UI = {
        'inventory': '🎒',
        'stats': '📈',
        'character': '👤',
        'explore': '🗺️',
        'inspect': '🔍',
        'attack': '⚔️',
        'defense': '🛡️',
        'speed': '💨',
        'mana': '💙',
        'health': '❤️',
        'gold': '💰',
        'equipment': '⚔️',
        'location': '📍'
    }
    
    # Status emojis
    STATUS = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'loading': '⏳',
        'complete': '🎉'
    }
    
    # Effect emojis
    EFFECTS = {
        'heal': '💚',
        'damage': '💥',
        'buff': '⬆️',
        'debuff': '⬇️',
        'poison': '☠️',
        'fire': '🔥',
        'ice': '❄️',
        'lightning': '⚡'
    }
    
    # Foraging emojis
    FORAGING = {
        'grid_empty': '⬜',
        'grid_found': '✅',
        'grid_miss': '❌'
    }
    
    @classmethod
    def get_rarity(cls, rarity: str) -> str:
        return cls.RARITY.get(rarity.lower(), '❓')
    
    @classmethod
    def get_item_type(cls, item_type: str) -> str:
        return cls.ITEM_TYPE.get(item_type.lower(), '❓')
    
    @classmethod
    def get_ui(cls, ui_element: str) -> str:
        return cls.UI.get(ui_element.lower(), '❓')
    
    @classmethod
    def get_status(cls, status: str) -> str:
        return cls.STATUS.get(status.lower(), '❓')
    
    @classmethod
    def get_effect(cls, effect: str) -> str:
        return cls.EFFECTS.get(effect.lower(), '❓')
    
    @classmethod
    def get_foraging(cls, grid_state: str) -> str:
        return cls.FORAGING.get(grid_state.lower(), '❓')
