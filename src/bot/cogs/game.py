"""
Game commands for PocketRPG Discord bot
Handles exploration, activities, and general game features
"""

import discord
from discord.ext import commands
from discord import app_commands
from ...game import data_loader, RegionManager
from ...game.enums import PlayerClass


class GameCog(commands.Cog):
    """Game commands for exploration and activities"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="explore", description="Explore your current region")
    async def explore(self, interaction: discord.Interaction):
        """Explore the current region"""
        user_id = interaction.user.id
        player = self.bot.get_player(user_id)
        
        if not player:
            await interaction.response.send_message(
                "❌ You don't have a character yet! Use `/create_character` to create one.",
            )
            return
        
        # Get current region
        region_manager = self.bot.region_manager
        region_manager.set_current_region(player.current_region)
        current_region = region_manager.get_current_region()
        
        if not current_region:
            await interaction.response.send_message(
                "❌ Error loading region data. Please try again later.",
            )
            return
        
        # Create exploration embed
        embed = discord.Embed(
            title=f"🗺️ Exploring {current_region.name}",
            description=current_region.description,
            color=discord.Color.green()
        )
        
        # Available activities
        activities = current_region.available_activities
        if activities:
            activity_text = "\n".join([f"• {activity.title()}" for activity in activities])
            embed.add_field(
                name="🎯 Available Activities",
                value=activity_text,
                inline=True
            )
        
        # Available enemies
        enemies = current_region.get_available_enemies()
        if enemies:
            enemy_data = []
            for enemy_id in enemies:
                enemy = data_loader.load_enemy(enemy_id)
                if enemy:
                    enemy_data.append(f"• {enemy['name']} (Level {enemy['base_level']})")
            
            if enemy_data:
                embed.add_field(
                    name="👹 Enemies",
                    value="\n".join(enemy_data),
                    inline=True
                )
        
        # Region info
        region_info = f"**Level:** {current_region.level}\n**Loot Multiplier:** {current_region.loot_multiplier}x\n**Enemy Bonus:** +{current_region.enemy_level_bonus}"
        embed.add_field(
            name="📊 Region Info",
            value=region_info,
            inline=True
        )
        
        # Environmental effects
        effects = current_region.get_environmental_effects()
        if effects:
            embed.add_field(
                name="🌤️ Environmental Effects",
                value="\n".join([f"• {effect.title()}" for effect in effects]),
                inline=False
            )
        
        embed.set_footer(text="Use /activity to perform activities in this region!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="activity", description="Perform an activity in your current region")
    @app_commands.describe(activity="The activity you want to perform")
    async def activity(self, interaction: discord.Interaction, activity: str):
        """Perform an activity"""
        user_id = interaction.user.id
        player = self.bot.get_player(user_id)
        
        if not player:
            await interaction.response.send_message(
                "❌ You don't have a character yet! Use `/create_character` to create one.",
            )
            return
        
        # Get current region
        region_manager = self.bot.region_manager
        region_manager.set_current_region(player.current_region)
        current_region = region_manager.get_current_region()
        
        if not current_region:
            await interaction.response.send_message(
                "❌ Error loading region data. Please try again later.",
            )
            return
        
        # Check if activity is available
        available_activities = current_region.available_activities
        if activity.lower() not in available_activities:
            await interaction.response.send_message(
                f"❌ **{activity.title()}** is not available in {current_region.name}.\n\nAvailable activities: {', '.join([a.title() for a in available_activities])}",
            )
            return
        
        # Load activity data
        activity_data = data_loader.load_activity(activity.lower())
        if not activity_data:
            await interaction.response.send_message(
                f"❌ Activity data not found for **{activity.title()}**.",
            )
            return
        
        # Check energy requirements
        energy_cost = activity_data.get('energy_cost', 0)
        if player.get_stat(player.stats[StatType.MANA]) < energy_cost:  # Using mana as energy for now
            await interaction.response.send_message(
                f"❌ Not enough energy! You need {energy_cost} energy to perform **{activity.title()}**.",
            )
            return
        
        # Perform activity (simplified for now)
        await interaction.response.send_message(
            f"🎯 **{player.name}** is performing **{activity.title()}**...",
        )
        
        # Simulate activity duration
        import asyncio
        await asyncio.sleep(2)  # Simulate activity time
        
        # Calculate rewards
        experience_reward = activity_data.get('experience_reward', 0)
        player.add_experience(experience_reward)
        
        # Consume energy
        player.modify_stat(StatType.MANA, -energy_cost)
        
        # Create results embed
        embed = discord.Embed(
            title=f"✅ {activity.title()} Complete!",
            description=f"**{player.name}** has finished {activity_data['description'].lower()}",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📈 Rewards",
            value=f"**Experience:** +{experience_reward}\n**Energy Used:** -{energy_cost}",
            inline=True
        )
        
        # Check for level up
        if player.level > 1:  # Simple level up check
            embed.add_field(
                name="🎉 Level Up!",
                value=f"**{player.name}** is now level {player.level}!",
                inline=True
            )
        
        embed.set_footer(text="Use /character to view your updated stats!")
        
        # Send follow-up message
        await interaction.followup.send(embed=embed, )
    
    @app_commands.command(name="regions", description="View available regions")
    async def regions(self, interaction: discord.Interaction):
        """View available regions"""
        user_id = interaction.user.id
        player = self.bot.get_player(user_id)
        
        if not player:
            await interaction.response.send_message(
                "❌ You don't have a character yet! Use `/create_character` to create one.",
            )
            return
        
        # Get accessible regions
        accessible_regions = self.bot.region_manager.get_accessible_regions(player)
        
        if not accessible_regions:
            await interaction.response.send_message(
                "❌ No regions available.",
            )
            return
        
        embed = discord.Embed(
            title="🗺️ Available Regions",
            description="Explore different regions to find new challenges and rewards!",
            color=discord.Color.blue()
        )
        
        for region in accessible_regions:
            if region["accessible"]:
                if region["current"]:
                    name = f"📍 {region['name']} (Current)"
                    value = f"**Level:** {region['level']}\n**Status:** ✅ Accessible"
                else:
                    name = f"🌱 {region['name']}"
                    value = f"**Level:** {region['level']}\n**Status:** ✅ Accessible"
            else:
                name = f"🔒 {region['name']}"
                value = f"**Level:** {region['level']}\n**Status:** ❌ {region['reason']}"
            
            embed.add_field(name=name, value=value, inline=True)
        
        embed.set_footer(text="Use /explore to explore your current region!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="help", description="Get help with PocketRPG commands")
    async def help_command(self, interaction: discord.Interaction):
        """Show help information"""
        embed = discord.Embed(
            title="🎮 PocketRPG Help",
            description="Welcome to PocketRPG! Here are the available commands:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="👤 Character Commands",
            value="`/create_character` - Create a new character\n`/character` - View your character\n`/classes` - View available classes\n`/delete_character` - Delete your character",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Game Commands",
            value="`/explore` - Explore your current region\n`/activity` - Perform an activity\n`/regions` - View available regions\n`/help` - Show this help",
            inline=False
        )
        
        embed.add_field(
            name="⚔️ Combat Commands",
            value="`/combat` - Start combat with an enemy\n`/attack` - Attack in combat\n`/defend` - Defend in combat",
            inline=False
        )
        
        embed.set_footer(text="PocketRPG - Your adventure awaits!")
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Load the cog"""
    await bot.add_cog(GameCog(bot))
