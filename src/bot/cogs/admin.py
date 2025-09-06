"""
Admin commands for PocketRPG Discord bot
Handles administrative functions and bot management
"""

import discord
from discord.ext import commands
from discord import app_commands


class AdminCog(commands.Cog):
    """Admin commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="admin_stats", description="View bot statistics (Admin only)")
    async def admin_stats(self, interaction: discord.Interaction):
        """View bot statistics"""
        # Check if user is admin (simplified check)
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command!",
                ephemeral=True
            )
            return
        
        # Get bot stats
        total_players = len(self.bot.active_players)
        active_combats = len(self.bot.active_combats)
        total_guilds = len(self.bot.guilds)
        
        embed = discord.Embed(
            title="📊 Bot Statistics",
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
            name="🎮 Game Data",
            value=f"**Regions:** {len(self.bot.region_manager.get_available_regions())}\n**Activities:** {len(self.bot.region_manager.data_loader.list_activities())}",
            inline=True
        )
        
        embed.set_footer(text=f"Bot Uptime: {self.bot.uptime if hasattr(self.bot, 'uptime') else 'Unknown'}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="admin_reload", description="Reload game data (Admin only)")
    async def admin_reload(self, interaction: discord.Interaction):
        """Reload game data"""
        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command!",
                ephemeral=True
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
                name="📊 Reloaded Data",
                value=f"**Regions:** {len(self.bot.region_manager.data_loader.list_regions())}\n**Activities:** {len(self.bot.region_manager.data_loader.list_activities())}\n**Items:** {len(self.bot.region_manager.data_loader.list_items())}\n**Enemies:** {len(self.bot.region_manager.data_loader.list_enemies())}",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error reloading data: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="admin_clear_combats", description="Clear all active combats (Admin only)")
    async def admin_clear_combats(self, interaction: discord.Interaction):
        """Clear all active combats"""
        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command!",
                ephemeral=True
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
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="admin_clear_players", description="Clear all active players (Admin only)")
    async def admin_clear_players(self, interaction: discord.Interaction):
        """Clear all active players"""
        # Check if user is admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command!",
                ephemeral=True
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
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    """Load the cog"""
    await bot.add_cog(AdminCog(bot))
