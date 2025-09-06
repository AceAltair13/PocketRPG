"""
Player management commands with Discord UI components
Features interactive buttons, select menus, and modals for better UX
"""

import discord
from discord.ext import commands
from discord import app_commands
from ...game import PlayerCreation, PlayerClass
from ...game.enums import StatType


class CharacterCreationModal(discord.ui.Modal):
    """Modal for character creation with name input"""
    
    def __init__(self, bot):
        super().__init__(title="Create Your Character")
        self.bot = bot
        
        self.name_input = discord.ui.TextInput(
            label="Character Name",
            placeholder="Enter your character's name...",
            min_length=2,
            max_length=20,
            required=True
        )
        self.add_item(self.name_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle character creation form submission"""
        user_id = interaction.user.id
        
        # Check if player already exists
        if self.bot.get_player(user_id):
            await interaction.response.send_message(
                "❌ You already have a character! Use `/character` to view your stats.",
                ephemeral=True
            )
            return
        
        # Validate name
        name = self.name_input.value.strip()
        is_valid, error = PlayerCreation.validate_player_name(name)
        if not is_valid:
            await interaction.response.send_message(
                f"❌ Invalid character name: {error}",
                ephemeral=True
            )
            return
        
        # Create class selection view
        view = ClassSelectionView(name, self.bot)
        
        embed = discord.Embed(
            title="🎭 Choose Your Class",
            description=f"**{name}**, select your character class:",
            color=discord.Color.blue()
        )
        
        # Add class descriptions
        classes = PlayerCreation.get_available_classes()
        for player_class in classes:
            description = PlayerCreation.get_class_description(player_class)
            embed.add_field(
                name=f"⚔️ {player_class.value.title()}",
                value=description,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class ClassSelectionView(discord.ui.View):
    """View for selecting character class with buttons"""
    
    def __init__(self, character_name: str, bot):
        super().__init__(timeout=60)
        self.character_name = character_name
        self.bot = bot
    
    @discord.ui.button(label="Warrior", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def warrior_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_character(interaction, PlayerClass.WARRIOR)
    
    @discord.ui.button(label="Mage", style=discord.ButtonStyle.primary, emoji="🔮")
    async def mage_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_character(interaction, PlayerClass.MAGE)
    
    @discord.ui.button(label="Rogue", style=discord.ButtonStyle.primary, emoji="🗡️")
    async def rogue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_character(interaction, PlayerClass.ROGUE)
    
    @discord.ui.button(label="Cleric", style=discord.ButtonStyle.primary, emoji="⛑️")
    async def cleric_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_character(interaction, PlayerClass.CLERIC)
    
    async def create_character(self, interaction: discord.Interaction, player_class: PlayerClass):
        """Create character with selected class"""
        try:
            # Create player
            player = PlayerCreation.create_player(self.character_name, player_class)
            player.set_user_id(interaction.user.id)
            
            # Store player
            self.bot.set_player(interaction.user.id, player)
            
            # Create success embed
            embed = discord.Embed(
                title="🎮 Character Created!",
                description=f"Welcome to PocketRPG, **{self.character_name}**!",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Class",
                value=f"{player_class.value.title()} - {PlayerCreation.get_class_description(player_class)}",
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
            
            # Add action buttons
            view = CharacterActionView(player, self.bot)
            
            embed.set_footer(text="Use the buttons below to get started!")
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error creating character: {str(e)}",
                ephemeral=True
            )


class CharacterActionView(discord.ui.View):
    """View with action buttons for new characters"""
    
    def __init__(self, player, bot):
        super().__init__(timeout=300)
        self.player = player
        self.bot = bot
    
    @discord.ui.button(label="View Character", style=discord.ButtonStyle.secondary, emoji="📊")
    async def view_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View character details"""
        embed = self.create_character_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Explore", style=discord.ButtonStyle.success, emoji="🗺️")
    async def explore(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Start exploring"""
        # Get current region
        region_manager = self.bot.region_manager
        region_manager.set_current_region(self.player.current_region)
        current_region = region_manager.get_current_region()
        
        if not current_region:
            await interaction.response.send_message(
                "❌ Error loading region data. Please try again later.",
                ephemeral=True
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
        
        # Available enemies with discovery status
        enemies = current_region.get_enemies_with_discovery(self.player)
        if enemies:
            enemy_data = []
            for enemy in enemies:
                if enemy["discovered"]:
                    # Show enemy type with emoji
                    type_emoji = {
                        "normal": "👹",
                        "mini_boss": "🔥",
                        "boss": "👑"
                    }.get(enemy["type"], "👹")
                    
                    enemy_data.append(f"{type_emoji} {enemy['name']} (Level {enemy['level']})")
                else:
                    enemy_data.append(f"❓ Unknown Enemy")
            
            if enemy_data:
                embed.add_field(
                    name="👹 Enemies",
                    value="\n".join(enemy_data),
                    inline=True
                )
        
        # Add activity selection
        view = ActivitySelectionView(self.player, self.bot)
        
        embed.set_footer(text="Choose an activity to get started!")
        
        await interaction.response.send_message(embed=embed, view=view)
    
    def create_character_embed(self):
        """Create character information embed"""
        embed = discord.Embed(
            title=f"📊 {self.player.name} - Level {self.player.level} {self.player.player_class.value.title()}",
            color=discord.Color.blue()
        )
        
        # Stats section
        stats_text = f"""
**Health:** {self.player.get_stat(StatType.HEALTH)}/{self.player.get_stat(StatType.MAX_HEALTH)} ({self.player.get_health_percentage():.1f}%)
**Mana:** {self.player.get_stat(StatType.MANA)}/{self.player.get_stat(StatType.MAX_MANA)} ({self.player.get_mana_percentage():.1f}%)
**Attack:** {self.player.get_stat(StatType.ATTACK)}
**Defense:** {self.player.get_stat(StatType.DEFENSE)}
**Speed:** {self.player.get_stat(StatType.SPEED)}
        """.strip()
        
        embed.add_field(name="📈 Stats", value=stats_text, inline=True)
        
        # Equipment section
        equipped_weapon = None
        for slot, item in self.player.equipment.equipped_items.items():
            if item is not None:
                equipped_weapon = item
                break
        
        equipment_text = f"**Weapon:** {equipped_weapon.name if equipped_weapon else 'None'}\n**Gold:** {self.player.gold}\n**Skill Points:** {self.player.skill_points}"
        
        embed.add_field(name="⚔️ Equipment", value=equipment_text, inline=True)
        
        # Location section
        embed.add_field(name="🗺️ Location", value=f"**{self.player.current_region.title()}**", inline=True)
        
        return embed


class ActivitySelectionView(discord.ui.View):
    """View for selecting activities with buttons"""
    
    def __init__(self, player, bot):
        super().__init__(timeout=60)
        self.player = player
        self.bot = bot
    
    @discord.ui.button(label="Scout", style=discord.ButtonStyle.danger, emoji="🔍")
    async def scout_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.start_activity(interaction, "scout")
    
    @discord.ui.button(label="Foraging", style=discord.ButtonStyle.success, emoji="🌿")
    async def foraging_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.start_activity(interaction, "foraging")
    
    @discord.ui.button(label="Farming", style=discord.ButtonStyle.success, emoji="🌾")
    async def farming_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.start_activity(interaction, "farming")
    
    @discord.ui.button(label="Mining", style=discord.ButtonStyle.secondary, emoji="⛏️")
    async def mining_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.start_activity(interaction, "mining")
    
    async def start_activity(self, interaction: discord.Interaction, activity: str):
        """Start the selected activity"""
        # Get current region
        region_manager = self.bot.region_manager
        region_manager.set_current_region(self.player.current_region)
        current_region = region_manager.get_current_region()
        
        if not current_region:
            await interaction.response.send_message(
                "❌ Error loading region data. Please try again later.",
                ephemeral=True
            )
            return
        
        # Check if activity is available
        available_activities = current_region.available_activities
        if activity.lower() not in available_activities:
            await interaction.response.send_message(
                f"❌ **{activity.title()}** is not available in {current_region.name}.",
                ephemeral=True
            )
            return
        
        # Load activity data
        activity_data = self.bot.region_manager.data_loader.load_activity(activity.lower())
        if not activity_data:
            await interaction.response.send_message(
                f"❌ Activity data not found for **{activity.title()}**.",
                ephemeral=True
            )
            return
        
        # Check energy requirements
        energy_cost = activity_data.get('energy_cost', 0)
        if self.player.get_stat(StatType.MANA) < energy_cost:  # Using mana as energy for now
            await interaction.response.send_message(
                f"❌ Not enough energy! You need {energy_cost} energy to perform **{activity.title()}**.",
                ephemeral=True
            )
            return
        
        # Perform activity
        await interaction.response.send_message(
            f"🎯 **{self.player.name}** is performing **{activity.title()}**...",
            ephemeral=True
        )
        
        # Simulate activity duration
        import asyncio
        await asyncio.sleep(2)  # Simulate activity time
        
        # Consume energy first
        self.player.modify_stat(StatType.MANA, -energy_cost)
        
        # Handle scout activity specially
        if activity.lower() == "scout":
            encounter = current_region.get_scout_encounter(self.player)
            
            if encounter:
                # Enemy encountered!
                enemy_data = encounter["enemy_data"]
                encounter_type = encounter["encounter_type"]
                
                # Discover the enemy
                self.player.discover_enemy(encounter["enemy_id"])
                
                # Create encounter embed
                embed = discord.Embed(
                    title="⚔️ Enemy Encountered!",
                    description=f"**{self.player.name}** has encountered a **{enemy_data['name']}** while scouting!",
                    color=discord.Color.red()
                )
                
                # Show enemy type with emoji
                type_emoji = {
                    "normal": "👹",
                    "mini_boss": "🔥",
                    "boss": "👑"
                }.get(encounter_type, "👹")
                
                embed.add_field(
                    name=f"{type_emoji} Enemy Details",
                    value=f"**Name:** {enemy_data['name']}\n**Level:** {enemy_data['base_level']}\n**Type:** {encounter_type.title()}",
                    inline=True
                )
                
                # Add combat button
                from .combat import CombatView
                combat_view = CombatView(self.player, encounter["enemy_id"], self.bot)
                embed.set_footer(text="Choose your action!")
                
                await interaction.followup.send(embed=embed, view=combat_view)
                return
            else:
                # No encounter
                embed = discord.Embed(
                    title="🔍 Scout Complete",
                    description=f"**{self.player.name}** scouted the area but found no enemies.",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="📈 Results",
                    value=f"**Energy Used:** -{energy_cost}\n**Status:** Area is clear",
                    inline=True
                )
        else:
            # Regular activity
            experience_reward = activity_data.get('experience_reward', 0)
            self.player.add_experience(experience_reward)
            
            # Create results embed
            embed = discord.Embed(
                title=f"✅ {activity.title()} Complete!",
                description=f"**{self.player.name}** has finished {activity_data['description'].lower()}",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📈 Rewards",
                value=f"**Experience:** +{experience_reward}\n**Energy Used:** -{energy_cost}",
                inline=True
            )
        
        # Check for level up
        if self.player.level > 1:  # Simple level up check
            embed.add_field(
                name="🎉 Level Up!",
                value=f"**{self.player.name}** is now level {self.player.level}!",
                inline=True
            )
        
        # Add continue button
        view = ContinueView(self.player, self.bot)
        
        embed.set_footer(text="Choose your next action!")
        
        # Send follow-up message
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class ContinueView(discord.ui.View):
    """View for continuing after activity completion"""
    
    def __init__(self, player, bot):
        super().__init__(timeout=60)
        self.player = player
        self.bot = bot
    
    @discord.ui.button(label="Continue Exploring", style=discord.ButtonStyle.primary, emoji="🗺️")
    async def continue_exploring(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Continue exploring"""
        # Get current region
        region_manager = self.bot.region_manager
        region_manager.set_current_region(self.player.current_region)
        current_region = region_manager.get_current_region()
        
        if not current_region:
            await interaction.response.send_message(
                "❌ Error loading region data. Please try again later.",
                ephemeral=True
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
        
        # Add activity selection
        view = ActivitySelectionView(self.player, self.bot)
        
        embed.set_footer(text="Choose an activity to continue!")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="View Character", style=discord.ButtonStyle.secondary, emoji="📊")
    async def view_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View character details"""
        embed = self.create_character_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def create_character_embed(self):
        """Create character information embed"""
        embed = discord.Embed(
            title=f"📊 {self.player.name} - Level {self.player.level} {self.player.player_class.value.title()}",
            color=discord.Color.blue()
        )
        
        # Stats section
        stats_text = f"""
**Health:** {self.player.get_stat(StatType.HEALTH)}/{self.player.get_stat(StatType.MAX_HEALTH)} ({self.player.get_health_percentage():.1f}%)
**Mana:** {self.player.get_stat(StatType.MANA)}/{self.player.get_stat(StatType.MAX_MANA)} ({self.player.get_mana_percentage():.1f}%)
**Attack:** {self.player.get_stat(StatType.ATTACK)}
**Defense:** {self.player.get_stat(StatType.DEFENSE)}
**Speed:** {self.player.get_stat(StatType.SPEED)}
        """.strip()
        
        embed.add_field(name="📈 Stats", value=stats_text, inline=True)
        
        # Equipment section
        equipped_weapon = None
        for slot, item in self.player.equipment.equipped_items.items():
            if item is not None:
                equipped_weapon = item
                break
        
        equipment_text = f"**Weapon:** {equipped_weapon.name if equipped_weapon else 'None'}\n**Gold:** {self.player.gold}\n**Skill Points:** {self.player.skill_points}"
        
        embed.add_field(name="⚔️ Equipment", value=equipment_text, inline=True)
        
        # Location section
        embed.add_field(name="🗺️ Location", value=f"**{self.player.current_region.title()}**", inline=True)
        
        return embed


class PlayerCog(commands.Cog):
    """Player management commands with interactive UI components"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="create_character", description="Create a new character with interactive UI")
    async def create_character(self, interaction: discord.Interaction):
        """Create a new character using a modal"""
        user_id = interaction.user.id
        
        # Check if player already exists
        if self.bot.get_player(user_id):
            await interaction.response.send_message(
                "❌ You already have a character! Use `/character` to view your stats.",
                ephemeral=True
            )
            return
        
        # Show character creation modal
        modal = CharacterCreationModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="character", description="View your character's stats with interactive buttons")
    async def character(self, interaction: discord.Interaction):
        """View character information with action buttons"""
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
        equipped_weapon = None
        for slot, item in player.equipment.equipped_items.items():
            if item is not None:
                equipped_weapon = item
                break
        
        equipment_text = f"**Weapon:** {equipped_weapon.name if equipped_weapon else 'None'}\n**Gold:** {player.gold}\n**Skill Points:** {player.skill_points}"
        
        embed.add_field(name="⚔️ Equipment", value=equipment_text, inline=True)
        
        # Location section
        embed.add_field(name="🗺️ Location", value=f"**{player.current_region.title()}**", inline=True)
        
        # Add action buttons
        view = CharacterActionView(player, self.bot)
        
        embed.set_footer(text="Use the buttons below to take action!")
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    """Load the player cog"""
    await bot.add_cog(PlayerCog(bot))
