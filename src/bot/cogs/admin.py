"""
Admin commands for PocketRPG Discord bot
Handles administrative functions and bot management
"""

import discord
from discord.ext import commands
from discord import app_commands
from ...utils.emoji_manager import get_emoji_manager


class AdminCog(commands.Cog):
    """Admin commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ping", description="Test bot connectivity")
    async def ping(self, interaction: discord.Interaction):
        """Simple ping command for testing"""
        embed = discord.Embed(
            title=f"{get_emoji_manager().get_ui_emoji('ping')} Pong!",
            description=f"Bot latency: {round(self.bot.latency * 1000)}ms",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, )
    
    @app_commands.command(name="admin_stats", description="View bot statistics (Admin only)")
    async def admin_stats(self, interaction: discord.Interaction):
        """View bot statistics"""
        # Check if user is admin (simplified check)
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} You don't have permission to use this command!",
            )
            return
        
        # Get bot stats
        total_players = len(self.bot.active_players)
        active_combats = len(self.bot.active_combats)
        total_guilds = len(self.bot.guilds)
        
        embed = discord.Embed(
            title=f"{get_emoji_manager().get_ui_emoji('stats')} Bot Statistics",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="👥 Players",
            value=f"**Active Players:** {total_players}\n**Active Combats:** {active_combats}",
            inline=True
        )
        
        embed.add_field(
            name="🏰 Servers",
            value=f"**Total Guilds:** {total_guilds}",
            inline=True
        )
        
        embed.add_field(
            name=f"{get_emoji_manager().get_ui_emoji('character')} Game Data",
            value=f"**Regions:** {len(self.bot.region_manager.get_available_regions())}\n**Activities:** {len(self.bot.region_manager.data_loader.list_activities())}",
            inline=True
        )
        
        embed.set_footer(text=f"Bot Uptime: {self.bot.uptime if hasattr(self.bot, 'uptime') else 'Unknown'}")
        
        await interaction.response.send_message(embed=embed, )
    
    @app_commands.command(name="admin_reload", description="Reload game data (Admin only)")
    async def admin_reload(self, interaction: discord.Interaction):
        """Reload game data"""
        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} You don't have permission to use this command!",
            )
            return
        
        try:
            # Reload data
            self.bot.region_manager.data_loader.reload_data()
            
            embed = discord.Embed(
                title="🔄 Data Reloaded",
                description="Game data has been successfully reloaded!",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name=f"{get_emoji_manager().get_ui_emoji('stats')} Reloaded Data",
                value=f"**Regions:** {len(self.bot.region_manager.data_loader.list_regions())}\n**Activities:** {len(self.bot.region_manager.data_loader.list_activities())}\n**Items:** {len(self.bot.region_manager.data_loader.list_items())}\n**Enemies:** {len(self.bot.region_manager.data_loader.list_enemies())}",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, )
            
        except Exception as e:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} Error reloading data: {str(e)}",
            )
    
    @app_commands.command(name="admin_clear_combats", description="Clear all active combats (Admin only)")
    async def admin_clear_combats(self, interaction: discord.Interaction):
        """Clear all active combats"""
        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} You don't have permission to use this command!",
            )
            return
        
        # Clear combats
        combat_count = len(self.bot.active_combats)
        self.bot.active_combats.clear()
        
        embed = discord.Embed(
            title="🧹 Combats Cleared",
            description=f"Cleared {combat_count} active combats.",
            color=discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed, )
    
    @app_commands.command(name="admin_clear_players", description="Clear all active players (Admin only)")
    async def admin_clear_players(self, interaction: discord.Interaction):
        """Clear all active players"""
        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} You don't have permission to use this command!",
            )
            return
        
        # Clear players
        player_count = len(self.bot.active_players)
        self.bot.active_players.clear()
        
        embed = discord.Embed(
            title="🧹 Players Cleared",
            description=f"Cleared {player_count} active players.",
            color=discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed, )
    
    @app_commands.command(name="admin_sync_commands", description="Manually sync slash commands (Admin only)")
    async def admin_sync_commands(self, interaction: discord.Interaction):
        """Manually sync slash commands"""
        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} You don't have permission to use this command!",
            )
            return
        
        try:
            # Sync commands to current guild
            synced = await self.bot.tree.sync(guild=interaction.guild)
            
            embed = discord.Embed(
                title="🔄 Commands Synced",
                description=f"Successfully synced {len(synced)} slash commands to this server!",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📋 Synced Commands",
                value="\n".join([f"• `/{cmd.name}`" for cmd in synced]),
                inline=False
            )
            
            embed.set_footer(text="Commands should now be available in this server!")
            
            await interaction.response.send_message(embed=embed, )
            
        except Exception as e:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} Error syncing commands: {str(e)}",
            )
    
    @app_commands.command(name="admin_sync_global", description="Sync slash commands to ALL servers (Admin only)")
    async def admin_sync_global(self, interaction: discord.Interaction):
        """Manually sync slash commands to all servers"""
        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} You don't have permission to use this command!",
                ephemeral=True
            )
            return
        
        try:
            # Sync commands globally
            synced = await self.bot.tree.sync()
            
            embed = discord.Embed(
                title="🌍 Global Commands Synced",
                description=f"Successfully synced {len(synced)} slash commands to ALL servers!",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📋 Synced Commands",
                value="\n".join([f"• `/{cmd.name}`" for cmd in synced]),
                inline=False
            )
            
            embed.add_field(
                name="🏰 Servers",
                value=f"Commands synced to {len(self.bot.guilds)} servers",
                inline=True
            )
            
            embed.set_footer(text="All commands should now be available in all servers!")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} Error syncing commands globally: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="admin_clear_commands", description="Clear all slash commands (Admin only)")
    async def admin_clear_commands(self, interaction: discord.Interaction):
        """Clear all slash commands"""
        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} You don't have permission to use this command!",
            )
            return
        
        try:
            # Clear all commands
            self.bot.tree.clear_commands(guild=None)
            for guild in self.bot.guilds:
                self.bot.tree.clear_commands(guild=guild)
            
            # Sync to apply the clearing
            await self.bot.tree.sync()
            
            embed = discord.Embed(
                title="🧹 Commands Cleared",
                description="All slash commands have been cleared and synced!",
                color=discord.Color.orange()
            )
            
            embed.set_footer(text="Restart the bot to reload commands.")
            
            await interaction.response.send_message(embed=embed, )
            
        except Exception as e:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} Error clearing commands: {str(e)}",
            )


async def setup(bot):
    """Load the cog"""
    await bot.add_cog(AdminCog(bot))
