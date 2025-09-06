"""
Player management commands for PocketRPG Discord bot
Handles character creation, stats, and player information
"""

import discord
from discord.ext import commands
from discord import app_commands
from ...game import PlayerCreation, PlayerClass
from ...game.enums import StatType


class PlayerCog(commands.Cog):
    """Player management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="create_character", description="Create a new character")
    @app_commands.describe(
        name="Your character's name",
        player_class="Your character's class"
    )
    @app_commands.choices(player_class=[
        app_commands.Choice(name="Warrior", value="warrior"),
        app_commands.Choice(name="Mage", value="mage"),
        app_commands.Choice(name="Rogue", value="rogue"),
        app_commands.Choice(name="Cleric", value="cleric")
    ])
    async def create_character(self, interaction: discord.Interaction, name: str, player_class: str):
        """Create a new character"""
        user_id = interaction.user.id
        
        # Check if player already exists
        if self.bot.get_player(user_id):
            await interaction.response.send_message(
                "❌ You already have a character! Use `/character` to view your stats.",
                ephemeral=True
            )
            return
        
        # Validate name
        is_valid, error = PlayerCreation.validate_player_name(name)
        if not is_valid:
            await interaction.response.send_message(
                f"❌ Invalid character name: {error}",
                ephemeral=True
            )
            return
        
        # Create player
        try:
            class_enum = PlayerClass(player_class.upper())
            player = PlayerCreation.create_player(name, class_enum)
            player.set_user_id(user_id)
            
            # Store player
            self.bot.set_player(user_id, player)
            
            # Create embed
            embed = discord.Embed(
                title="🎮 Character Created!",
                description=f"Welcome to PocketRPG, **{name}**!",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Class",
                value=f"{class_enum.value.title()} - {PlayerCreation.get_class_description(class_enum)}",
                inline=False
            )
            
            embed.add_field(
                name="Starting Stats",
                value=f"**Level:** {player.level}\n**Health:** {player.get_stat(StatType.HEALTH)}/{player.get_stat(StatType.MAX_HEALTH)}\n**Mana:** {player.get_stat(StatType.MANA)}/{player.get_stat(StatType.MAX_MANA)}\n**Gold:** {player.gold}",
                inline=True
            )
            
            embed.add_field(
                name="Location",
                value=f"🌱 **{player.current_region.title()}**\n*Your adventure begins here!*",
                inline=True
            )
            
            embed.set_footer(text="Use /character to view your stats anytime!")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error creating character: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="character", description="View your character's stats and information")
    async def character(self, interaction: discord.Interaction):
        """View character information"""
        user_id = interaction.user.id
        player = self.bot.get_player(user_id)
        
        if not player:
            await interaction.response.send_message(
                "❌ You don't have a character yet! Use `/create_character` to create one.",
                ephemeral=True
            )
            return
        
        # Create character embed
        embed = discord.Embed(
            title=f"📊 {player.name} - Level {player.level} {player.player_class.value.title()}",
            color=discord.Color.blue()
        )
        
        # Stats section
        stats_text = f"""
**Health:** {player.get_stat(StatType.HEALTH)}/{player.get_stat(StatType.MAX_HEALTH)} ({player.get_health_percentage():.1f}%)
**Mana:** {player.get_stat(StatType.MANA)}/{player.get_stat(StatType.MAX_MANA)} ({player.get_mana_percentage():.1f}%)
**Attack:** {player.get_stat(StatType.ATTACK)}
**Defense:** {player.get_stat(StatType.DEFENSE)}
**Speed:** {player.get_stat(StatType.SPEED)}
        """.strip()
        
        embed.add_field(name="📈 Stats", value=stats_text, inline=True)
        
        # Equipment section
        equipped_weapon = player.equipment.get_equipped_item(player.equipment.equipped_items.keys().__iter__().__next__())
        equipment_text = f"**Weapon:** {equipped_weapon.name if equipped_weapon else 'None'}\n**Gold:** {player.gold}\n**Skill Points:** {player.skill_points}"
        
        embed.add_field(name="⚔️ Equipment", value=equipment_text, inline=True)
        
        # Location section
        embed.add_field(name="🗺️ Location", value=f"**{player.current_region.title()}**", inline=True)
        
        # Experience section
        exp_text = f"**Experience:** {player.get_stat(StatType.EXPERIENCE)}\n**Next Level:** {player.get_experience_to_next_level()}"
        embed.add_field(name="⭐ Experience", value=exp_text, inline=True)
        
        embed.set_footer(text=f"Character ID: {player.id[:8]}...")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="classes", description="View available character classes")
    async def classes(self, interaction: discord.Interaction):
        """View available character classes"""
        embed = discord.Embed(
            title="🎭 Available Character Classes",
            description="Choose your class wisely - each has unique strengths and abilities!",
            color=discord.Color.purple()
        )
        
        classes = PlayerCreation.get_available_classes()
        for player_class in classes:
            description = PlayerCreation.get_class_description(player_class)
            embed.add_field(
                name=f"⚔️ {player_class.value.title()}",
                value=description,
                inline=False
            )
        
        embed.set_footer(text="Use /create_character to create your character!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="delete_character", description="Delete your character (cannot be undone!)")
    async def delete_character(self, interaction: discord.Interaction):
        """Delete character with confirmation"""
        user_id = interaction.user.id
        player = self.bot.get_player(user_id)
        
        if not player:
            await interaction.response.send_message(
                "❌ You don't have a character to delete!",
                ephemeral=True
            )
            return
        
        # Create confirmation embed
        embed = discord.Embed(
            title="⚠️ Delete Character",
            description=f"Are you sure you want to delete **{player.name}**?\n\n**This action cannot be undone!**",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Character Details",
            value=f"**Name:** {player.name}\n**Class:** {player.player_class.value.title()}\n**Level:** {player.level}",
            inline=False
        )
        
        view = CharacterDeleteView(player.name, user_id, self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class CharacterDeleteView(discord.ui.View):
    """View for character deletion confirmation"""
    
    def __init__(self, character_name: str, user_id: int, bot):
        super().__init__(timeout=60)
        self.character_name = character_name
        self.user_id = user_id
        self.bot = bot
    
    @discord.ui.button(label="Delete Character", style=discord.ButtonStyle.danger)
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirm character deletion"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ You can only delete your own character!",
                ephemeral=True
            )
            return
        
        # Delete character
        self.bot.remove_player(self.user_id)
        
        embed = discord.Embed(
            title="🗑️ Character Deleted",
            description=f"**{self.character_name}** has been permanently deleted.",
            color=discord.Color.red()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel character deletion"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ You can only cancel your own deletion!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="✅ Deletion Cancelled",
            description="Your character is safe!",
            color=discord.Color.green()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot):
    """Load the cog"""
    await bot.add_cog(PlayerCog(bot))
