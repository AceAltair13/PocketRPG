"""
Shared embed creation utilities to reduce code duplication
"""

import discord
import re
from typing import Optional, Dict, Any, List
from ...utils.ui_emojis import UIEmojis


class EmbedUtils:
    """Utility class for creating common Discord embeds"""
    
    @staticmethod
    def emoji_to_url(emoji: str) -> Optional[str]:
        """
        Convert Discord emoji markdown to proper URL format.
        Converts <:name:id> to https://cdn.discordapp.com/emojis/id.webp
        """
        if not emoji or not isinstance(emoji, str):
            return None
        
        # Check if it's already a URL
        if emoji.startswith('http'):
            return emoji
        
        # Check if it's a Discord emoji markdown
        match = re.match(r'<:(\w+):(\d+)>', emoji)
        if match:
            emoji_id = match.group(2)
            return f"https://cdn.discordapp.com/emojis/{emoji_id}.webp"
        
        # If it's a Unicode emoji, return None (can't be used as thumbnail)
        return None
    
    @staticmethod
    def create_error_embed(message: str, title: str = "Error") -> discord.Embed:
        """Create a standardized error embed"""
        return discord.Embed(
            title=f"{UIEmojis.get_status('error')} {title}",
            description=message,
            color=discord.Color.red()
        )
    
    @staticmethod
    def create_success_embed(message: str, title: str = "Success") -> discord.Embed:
        """Create a standardized success embed"""
        return discord.Embed(
            title=f"{UIEmojis.get_status('success')} {title}",
            description=message,
            color=discord.Color.green()
        )
    
    @staticmethod
    def create_info_embed(message: str, title: str = "Info") -> discord.Embed:
        """Create a standardized info embed"""
        return discord.Embed(
            title=f"{UIEmojis.get_status('info')} {title}",
            description=message,
            color=discord.Color.blue()
        )
    
    @staticmethod
    def create_character_embed(player) -> discord.Embed:
        """Create a character information embed"""
        embed = discord.Embed(
            title=f"{UIEmojis.get_ui('character')} {player.name} - Level {player.level} {player.player_class.value.title()}",
            color=discord.Color.blue()
        )
        
        # Stats section
        stats_text = f"""
**Health:** {player.get_stat('health')}/{player.get_stat('max_health')} ({player.get_health_percentage():.1f}%)
**Mana:** {player.get_stat('mana')}/{player.get_stat('max_mana')} ({player.get_mana_percentage():.1f}%)
**Attack:** {player.get_stat('attack')}
**Defense:** {player.get_stat('defense')}
**Speed:** {player.get_stat('speed')}
        """.strip()
        
        embed.add_field(name=f"{UIEmojis.get_ui('stats')} Stats", value=stats_text, inline=True)
        
        # Equipment section
        equipment_text = ""
        for slot, item in player.equipment.equipped_items.items():
            slot_name = slot.value.replace('_', ' ').title()
            equipment_text += f"**{slot_name}:** {item.name if item else 'Empty'}\n"
        
        embed.add_field(name=f"{UIEmojis.get_ui('equipment')} Equipment", value=equipment_text, inline=False)
        
        # Resources
        info_text = f"**Gold:** {player.gold}\n**Skill Points:** {player.skill_points}"
        embed.add_field(name=f"{UIEmojis.get_ui('gold')} Resources", value=info_text, inline=True)
        
        # Location
        embed.add_field(name=f"{UIEmojis.get_ui('location')} Location", value=f"**{player.current_region.title()}**", inline=True)
        
        return embed
    
    @staticmethod
    def create_inventory_embed(player) -> discord.Embed:
        """Create an inventory display embed"""
        embed = discord.Embed(
            title=f"{UIEmojis.get_ui('inventory')} {player.name}'s Inventory",
            color=discord.Color.blue()
        )
        
        inventory_items = player.inventory.items
        
        if not inventory_items:
            embed.add_field(
                name=f"{UIEmojis.get_ui('inventory')} Inventory",
                value="Your inventory is empty.",
                inline=False
            )
        else:
            # Group items by type
            items_by_type = {}
            for item_name, item in inventory_items.items():
                item_type = item.item_type.value.title()
                if item_type not in items_by_type:
                    items_by_type[item_type] = []
                items_by_type[item_type].append((item, item.quantity))
            
            # Display items by type
            for item_type, items in items_by_type.items():
                item_text = ""
                for item, quantity in items:
                    item_text += f"{item.emoji} **{item.name}** x{quantity}\n"
                
                embed.add_field(
                    name=f"{UIEmojis.get_item_type(item_type.lower())} {item_type}",
                    value=item_text.strip(),
                    inline=True
                )
        
        # Inventory stats
        total_items = sum(item.quantity for item in inventory_items.values())
        embed.add_field(
            name=f"{UIEmojis.get_ui('stats')} Inventory Stats",
            value=f"**Total Items:** {total_items}\n**Slots Used:** {len(inventory_items)}/{player.inventory.max_capacity}",
            inline=False
        )
        
        return embed
    
    @staticmethod
    def create_region_embed(region) -> discord.Embed:
        """Create a region exploration embed"""
        embed = discord.Embed(
            title=f"{UIEmojis.get_ui('explore')} Exploring {region.name}",
            description=region.description,
            color=discord.Color.green()
        )
        
        # Available activities
        activities = region.available_activities
        if activities:
            activity_text = "\n".join([f"• {activity.title()}" for activity in activities])
            embed.add_field(
                name=f"{UIEmojis.get_ui('explore')} Available Activities",
                value=activity_text,
                inline=True
            )
        
        # Region info
        region_info = f"**Level:** {region.level}\n**Loot Multiplier:** {region.loot_multiplier}x"
        embed.add_field(
            name=f"{UIEmojis.get_ui('stats')} Region Info",
            value=region_info,
            inline=True
        )
        
        return embed
