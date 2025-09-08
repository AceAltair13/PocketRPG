"""
Game commands for PocketRPG Discord bot
Handles exploration, activities, and general game features
"""

import discord
from discord.ext import commands
from discord import app_commands
from ...game import data_loader, RegionManager
from ...game.enums import PlayerClass, StatType
# UIEmojis no longer needed - using Emojis constants
from ..utils import Emojis, EmbedUtils


class ScoutEncounterView(discord.ui.View):
    """Minimal controls after a scout encounter: Fight or Flee."""
    
    def __init__(self, player, enemy, bot, enemy_id: str):
        super().__init__(timeout=60)
        self.player = player
        self.enemy = enemy
        self.bot = bot
        self.enemy_id = enemy_id
    
    @discord.ui.button(label="Fight", style=discord.ButtonStyle.danger, emoji=Emojis.ATTACK)
    async def fight(self, interaction: discord.Interaction, button: discord.ui.Button):
        from ...game import Combat
        from .combat import CombatView
        # Start combat session
        combat = Combat([self.player, self.enemy])
        self.bot.set_combat(interaction.channel_id, combat)
        
        # Build combat intro embed
        embed = discord.Embed(
            title=f"{Emojis.ATTACK} Combat Started!",
            description=f"**{self.player.name}** vs **{self.enemy.name}**",
            color=discord.Color.red()
        )
        
        # Set enemy emoji as thumbnail
        if hasattr(self.enemy, 'emoji') and self.enemy.emoji:
            emoji_url = EmbedUtils.emoji_to_url(self.enemy.emoji)
            if emoji_url:
                embed.set_thumbnail(url=emoji_url)
        
        combat_view = CombatView(self.player, self.enemy, self.bot, self.enemy_id)
        embed.set_footer(text="Your turn! Choose your action.")
        await interaction.response.edit_message(embed=embed, view=combat_view)
    
    @discord.ui.button(label="Flee", style=discord.ButtonStyle.secondary, emoji=Emojis.SPEED)
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"{Emojis.SPEED} Fled!",
            description=f"**{self.player.name}** decided not to engage **{self.enemy.name}**.",
            color=discord.Color.yellow()
        )
        embed.set_footer(text="Use /explore or /activity to continue your adventure.")
        await interaction.response.edit_message(embed=embed, view=None)


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
                f"{Emojis.ERROR} You don't have a character yet! Use `/create_character` to create one.",
            )
            return
        
        # Get current region
        region_manager = self.bot.region_manager
        region_manager.set_current_region(player.current_region)
        current_region = region_manager.get_current_region()
        
        if not current_region:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Error loading region data. Please try again later.",
            )
            return
        
        # Create exploration embed
        embed = discord.Embed(
            title=f"{Emojis.EXPLORE} Exploring {current_region.name}",
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
            name=f"{Emojis.STATS} Region Info",
            value=region_info,
            inline=True
        )
        
        # Environmental effects
        effects = current_region.get_environmental_effects()
        if effects:
            embed.add_field(
                name=f"{Emojis.BUFF} Environmental Effects",
                value="\n".join([f"• {effect.title()}" for effect in effects]),
                inline=False
            )
        
        embed.set_footer(text="Use /activity to perform activities in this region!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="activity", description="Perform an activity in your current region")
    @app_commands.describe(activity="The activity you want to perform")
    @app_commands.choices(activity=[
        app_commands.Choice(name="Scout", value="scout"),
        app_commands.Choice(name="Foraging", value="foraging"),
        app_commands.Choice(name="Farming", value="farming"),
        app_commands.Choice(name="Mining", value="mining")
    ])
    async def activity(self, interaction: discord.Interaction, activity: app_commands.Choice[str]):
        """Perform an activity"""
        user_id = interaction.user.id
        player = self.bot.get_player(user_id)
        
        if not player:
            await interaction.response.send_message(
                f"{Emojis.ERROR} You don't have a character yet! Use `/create_character` to create one.",
            )
            return
        
        # Get current region
        region_manager = self.bot.region_manager
        region_manager.set_current_region(player.current_region)
        current_region = region_manager.get_current_region()
        
        if not current_region:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Error loading region data. Please try again later.",
            )
            return
        
        # Check if activity is available
        available_activities = current_region.available_activities
        activity_name = activity.value
        if activity_name.lower() not in available_activities:
            await interaction.response.send_message(
                f"{Emojis.ERROR} **{activity_name.title()}** is not available in {current_region.name}.\n\nAvailable activities: {', '.join([a.title() for a in available_activities])}",
            )
            return
        
        # Load activity data
        activity_data = data_loader.load_activity(activity_name.lower())
        if not activity_data:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Activity data not found for **{activity_name.title()}**.",
            )
            return
        
        # Check energy requirements
        energy_cost = activity_data.get('energy_cost', 0)
        if player.get_stat(StatType.ENERGY) < energy_cost:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Not enough energy! You need {energy_cost} energy to perform **{activity_name.title()}**.",
            )
            return
        
        # Foraging launches the interactive minigame instead of auto-completing
        if activity_name.lower() == "foraging":
            from .foraging_minigame import ForagingMinigameView
            view = ForagingMinigameView(player, self.bot, activity_data)
            await interaction.response.send_message(embed=view.embed, view=view)
            return

        # Scout launches the region's encounter flow (may start combat)
        if activity_name.lower() == "scout":
            # Announce action
            await interaction.response.send_message(
                f"🎯 **{player.name}** is scouting the area...",
            )
            
            # Simulate brief delay
            import asyncio
            await asyncio.sleep(2)

            # Consume energy
            player.modify_stat(StatType.ENERGY, -energy_cost)

            # Determine encounter
            encounter = current_region.get_scout_encounter(player)
            if encounter:
                enemy_data = encounter["enemy_data"]
                encounter_type = encounter["encounter_type"]

                # Discover enemy
                player.discover_enemy(encounter["enemy_id"])

                # Build encounter embed
                embed = discord.Embed(
                    title=f"{Emojis.ATTACK} Enemy Encountered!",
                    description=(
                        f"**{player.name}** has encountered a **{enemy_data['name']}** while scouting!"
                    ),
                    color=discord.Color.red(),
                )

                enemy_emoji = enemy_data.get("emoji", "👹") if enemy_data else "👹"
                emoji_url = EmbedUtils.emoji_to_url(enemy_emoji)
                if emoji_url:
                    embed.set_thumbnail(url=emoji_url)

                embed.add_field(
                    name="👹 Enemy Details",
                    value=(
                        f"**Name:** {enemy_data['name']}\n"
                        f"**Level:** {enemy_data['base_level']}\n"
                        f"**Type:** {encounter_type.title()}"
                    ),
                    inline=True,
                )

                # Create enemy instance and start combat
                from ...game.entities.enemy import Enemy, EnemyType, EnemyBehavior

                enemy_type_map = {
                    "normal": EnemyType.NORMAL,
                    "mini_boss": EnemyType.MINIBOSS,
                    "boss": EnemyType.BOSS,
                }
                enemy_type = enemy_type_map.get(enemy_data.get("type", "normal"), EnemyType.NORMAL)

                enemy_instance = Enemy(
                    name=enemy_data["name"],
                    enemy_type=enemy_type,
                    level=enemy_data["base_level"],
                    behavior=EnemyBehavior.AGGRESSIVE,
                    emoji=enemy_data.get("emoji", "👹"),
                )

                # Load loot table
                for loot_entry in enemy_data.get("loot_table", []):
                    enemy_instance.add_loot_item(
                        item_name=loot_entry["item"],
                        drop_chance=loot_entry["drop_chance"],
                        quantity=(
                            loot_entry["quantity"][0]
                            if isinstance(loot_entry["quantity"], list)
                            else loot_entry["quantity"]
                        ),
                    )

                # Provide simple choice to fight or flee instead of full combat controls
                choice_view = ScoutEncounterView(player, enemy_instance, self.bot, encounter["enemy_id"])
                embed.set_footer(text="Choose to fight or flee.")
                await interaction.followup.send(embed=embed, view=choice_view)
                return

            # No encounter case
            await interaction.followup.send(
                f"{Emojis.INFO} **{player.name}** scouted the area but found no enemies this time.",
            )
            return
        
        # Perform non-minigame activities (simplified)
        await interaction.response.send_message(
            f"🎯 **{player.name}** is performing **{activity_name.title()}**...",
        )
        
        # Simulate activity duration
        import asyncio
        await asyncio.sleep(2)
        
        # Calculate rewards
        experience_reward = activity_data.get('experience_reward', 0)
        player.add_experience(experience_reward)
        
        # Consume energy
        player.modify_stat(StatType.ENERGY, -energy_cost)
        
        # Create results embed
        embed = discord.Embed(
            title=f"{Emojis.SUCCESS} {activity_name.title()} Complete!",
            description=f"**{player.name}** has finished {activity_data['description'].lower()}",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name=f"{Emojis.STATS} Rewards",
            value=f"**Experience:** +{experience_reward}\n**Energy Used:** -{energy_cost}",
            inline=True
        )
        
        if player.level > 1:
            embed.add_field(
                name=f"{Emojis.COMPLETE} Level Up!",
                value=f"**{player.name}** is now level {player.level}!",
                inline=True
            )
        
        embed.set_footer(text="Use /character to view your updated stats!")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="regions", description="View available regions")
    async def regions(self, interaction: discord.Interaction):
        """View available regions"""
        user_id = interaction.user.id
        player = self.bot.get_player(user_id)
        
        if not player:
            await interaction.response.send_message(
                f"{Emojis.ERROR} You don't have a character yet! Use `/create_character` to create one.",
            )
            return
        
        # Get accessible regions
        accessible_regions = self.bot.region_manager.get_accessible_regions(player)
        
        if not accessible_regions:
            await interaction.response.send_message(
                f"{Emojis.ERROR} No regions available.",
            )
            return
        
        embed = discord.Embed(
            title=f"{Emojis.EXPLORE} Available Regions",
            description="Explore different regions to find new challenges and rewards!",
            color=discord.Color.blue()
        )
        
        for region in accessible_regions:
            if region["accessible"]:
                if region["current"]:
                    name = f"📍 {region['name']} (Current)"
                    value = f"**Level:** {region['level']}\n**Status:** {Emojis.SUCCESS} Accessible"
                else:
                    name = f"{Emojis.LOCATION} {region['name']}"
                    value = f"**Level:** {region['level']}\n**Status:** {Emojis.SUCCESS} Accessible"
            else:
                name = f"🔒 {region['name']}"
                value = f"**Level:** {region['level']}\n**Status:** {Emojis.ERROR} {region['reason']}"
            
            embed.add_field(name=name, value=value, inline=True)
        
        embed.set_footer(text="Use /explore to explore your current region!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="help", description="Get help with PocketRPG commands")
    async def help_command(self, interaction: discord.Interaction):
        """Show help information"""
        embed = discord.Embed(
            title=f"{Emojis.CHARACTER} PocketRPG Help",
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
            name=f"{Emojis.ATTACK} Combat Commands",
            value="`/combat` - Start combat with an enemy\n`/attack` - Attack in combat\n`/defend` - Defend in combat",
            inline=False
        )
        
        embed.set_footer(text="PocketRPG - Your adventure awaits!")
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Load the cog"""
    await bot.add_cog(GameCog(bot))
