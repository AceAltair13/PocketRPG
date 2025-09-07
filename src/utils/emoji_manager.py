"""
Emoji Manager for PocketRPG Discord Bot
Centralized system for managing custom and fallback emojis
"""

import json
import os
from typing import Optional, Dict, Any, List
import discord


class EmojiManager:
    """
    Centralized emoji management system.
    Handles custom Discord emojis with fallback to Unicode emojis.
    """
    
    def __init__(self, bot: Optional[discord.Client] = None):
        self.bot = bot
        self.emoji_data = {}
        self._load_emoji_data()
    
    def _load_emoji_data(self):
        """Load emoji data from JSON file"""
        try:
            # Get the path to the emojis.json file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            emoji_file = os.path.join(current_dir, '..', '..', 'data', 'emojis.json')
            
            with open(emoji_file, 'r', encoding='utf-8') as f:
                self.emoji_data = json.load(f)
        except FileNotFoundError:
            print("Warning: emojis.json not found, using fallback emojis")
            self.emoji_data = {}
        except json.JSONDecodeError as e:
            print(f"Error loading emoji data: {e}")
            self.emoji_data = {}
    
    def get_emoji(self, category: str, key: str) -> str:
        """
        Get an emoji by category and key.
        
        Args:
            category: The category (e.g., 'rarity', 'items', 'ui')
            key: The specific emoji key (e.g., 'common', 'weapon', 'inventory')
        
        Returns:
            The emoji string (custom Discord emoji or fallback Unicode)
        """
        try:
            emoji_info = self.emoji_data.get(category, {}).get(key, {})
            emoji_markdown = emoji_info.get('emoji', '')
            
            # If we have a Discord emoji markdown and bot is available, try to get the custom emoji
            if emoji_markdown.startswith('<:') and emoji_markdown.endswith('>') and self.bot:
                try:
                    # Extract emoji ID from markdown: <:name:id>
                    emoji_id = int(emoji_markdown.split(':')[-1].rstrip('>'))
                    custom_emoji = self.bot.get_emoji(emoji_id)
                    if custom_emoji:
                        return str(custom_emoji)
                except (ValueError, IndexError, Exception):
                    pass  # Fall back to default emoji
            
            # Return the fallback emoji
            return emoji_info.get('fallback', emoji_markdown if emoji_markdown else '❓')
            
        except Exception:
            return '❓'  # Ultimate fallback
    
    def get_rarity_emoji(self, rarity: str) -> str:
        """Get emoji for item rarity"""
        return self.get_emoji('rarity', rarity.lower())
    
    def get_item_type_emoji(self, item_type: str) -> str:
        """Get emoji for item type"""
        return self.get_emoji('items', item_type.lower())
    
    def get_ui_emoji(self, ui_element: str) -> str:
        """Get emoji for UI elements"""
        return self.get_emoji('ui', ui_element.lower())
    
    def get_activity_emoji(self, activity: str) -> str:
        """Get emoji for activities"""
        return self.get_emoji('activities', activity.lower())
    
    def get_effect_emoji(self, effect: str) -> str:
        """Get emoji for effects"""
        return self.get_emoji('effects', effect.lower())
    
    def get_status_emoji(self, status: str) -> str:
        """Get emoji for status indicators"""
        return self.get_emoji('status', status.lower())
    
    def get_foraging_emoji(self, grid_state: str) -> str:
        """Get emoji for foraging grid states"""
        return self.get_emoji('foraging', grid_state.lower())
    
    def update_emoji_id(self, category: str, key: str, discord_id: int):
        """
        Update the Discord emoji ID for a specific emoji.
        This should be called when custom emojis are uploaded to the bot.
        
        Args:
            category: The category (e.g., 'rarity', 'items', 'ui')
            key: The specific emoji key
            discord_id: The Discord emoji ID
        """
        if category not in self.emoji_data:
            self.emoji_data[category] = {}
        
        if key not in self.emoji_data[category]:
            self.emoji_data[category][key] = {}
        
        self.emoji_data[category][key]['discord_id'] = discord_id
    
    def save_emoji_data(self):
        """Save emoji data back to JSON file"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            emoji_file = os.path.join(current_dir, '..', '..', 'data', 'emojis.json')
            
            with open(emoji_file, 'w', encoding='utf-8') as f:
                json.dump(self.emoji_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving emoji data: {e}")
    
    def get_all_emojis(self) -> Dict[str, Any]:
        """Get all emoji data"""
        return self.emoji_data
    
    def list_custom_emojis(self) -> Dict[str, Dict[str, int]]:
        """
        List all emojis that have custom Discord IDs.
        Returns a dictionary of category -> key -> discord_id
        """
        custom_emojis = {}
        
        for category, emojis in self.emoji_data.items():
            custom_emojis[category] = {}
            for key, emoji_info in emojis.items():
                if emoji_info.get('discord_id'):
                    custom_emojis[category][key] = emoji_info['discord_id']
        
        return custom_emojis
    
    def validate_emoji_ids(self) -> Dict[str, List[str]]:
        """
        Validate that all custom emoji IDs are still valid.
        Returns a dictionary of invalid emojis by category.
        """
        invalid_emojis = {}
        
        if not self.bot:
            return invalid_emojis
        
        for category, emojis in self.emoji_data.items():
            invalid_emojis[category] = []
            for key, emoji_info in emojis.items():
                if emoji_info.get('discord_id'):
                    try:
                        custom_emoji = self.bot.get_emoji(emoji_info['discord_id'])
                        if not custom_emoji:
                            invalid_emojis[category].append(key)
                    except Exception:
                        invalid_emojis[category].append(key)
        
        # Remove empty categories
        invalid_emojis = {k: v for k, v in invalid_emojis.items() if v}
        
        return invalid_emojis
    
    def add_emoji_from_markdown(self, category: str, key: str, markdown: str, fallback: str = "❓"):
        """
        Add an emoji from Discord's markdown format.
        
        Args:
            category: The category (e.g., 'items', 'rarity')
            key: The emoji key
            markdown: Discord emoji markdown like '<:wild_berries:1414025312693391494>'
            fallback: Fallback emoji if custom emoji fails
        """
        import re
        
        # Parse Discord emoji markdown: <:name:id>
        match = re.match(r'<:([^:]+):(\d+)>', markdown)
        if match:
            emoji_name, emoji_id = match.groups()
            emoji_id = int(emoji_id)
            
            # Add to emoji data
            if category not in self.emoji_data:
                self.emoji_data[category] = {}
            
            self.emoji_data[category][key] = {
                "emoji": markdown,
                "discord_id": emoji_id,
                "fallback": fallback
            }
            
            return True
        else:
            print(f"Invalid emoji markdown format: {markdown}")
            return False
    
    def get_item_emoji(self, item_name: str) -> str:
        """
        Get emoji for a specific item by name.
        This is useful for items that have their own custom emojis.
        """
        # First try to get from items category
        item_emoji = self.get_emoji('items', item_name.lower())
        if item_emoji != '❓':
            return item_emoji
        
        # Fallback to item type
        return self.get_emoji('items', 'material')  # Default fallback
    
    def get_enemy_emoji(self, enemy_id: str) -> str:
        """
        Get emoji for a specific enemy by ID.
        """
        return self.get_emoji('enemies', enemy_id.lower())


# Global emoji manager instance
emoji_manager = EmojiManager()


def get_emoji_manager() -> EmojiManager:
    """Get the global emoji manager instance"""
    return emoji_manager


def set_bot(bot: discord.Client):
    """Set the bot instance for the global emoji manager"""
    emoji_manager.bot = bot
