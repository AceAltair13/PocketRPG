"""
Player management commands with Discord UI components
Features interactive buttons, select menus, and modals for better UX
"""

import discord
from discord.ext import commands
from discord import app_commands
from ...game import PlayerCreation, PlayerClass
from ...game.enums import StatType, EquipmentSlot
# UIEmojis no longer needed - using Emojis constants
from ..utils import EmbedUtils, ResponseUtils, PlayerUtils, Emojis


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
        can_create, error_msg = PlayerUtils.check_player_not_exists(self.bot, user_id)
        if not can_create:
            await ResponseUtils.send_error(interaction, error_msg, "Character Exists")
            return
        
        # Validate name
        name = self.name_input.value.strip()
        is_valid, error = PlayerUtils.validate_character_name(name)
        if not is_valid:
            await ResponseUtils.send_error(interaction, f"Invalid character name: {error}", "Invalid Name")
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
                name=f"{Emojis.ATTACK} {player_class.value.title()}",
                value=description,
                inline=False
            )
        
        
        await interaction.response.send_message(embed=embed, view=view, )


class ClassSelectionView(discord.ui.View):
    """View for selecting character class with buttons"""
    
    def __init__(self, character_name: str, bot):
        super().__init__(timeout=60)
        self.character_name = character_name
        self.bot = bot
    
    @discord.ui.button(label="Warrior", style=discord.ButtonStyle.primary, emoji=Emojis.ATTACK)
    async def warrior_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_character(interaction, PlayerClass.WARRIOR)
    
    @discord.ui.button(label="Mage", style=discord.ButtonStyle.primary, emoji=Emojis.MANA)
    async def mage_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_character(interaction, PlayerClass.MAGE)
    
    @discord.ui.button(label="Rogue", style=discord.ButtonStyle.primary, emoji=Emojis.SPEED)
    async def rogue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_character(interaction, PlayerClass.ROGUE)
    
    @discord.ui.button(label="Cleric", style=discord.ButtonStyle.primary, emoji=Emojis.HEALTH)
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
            embed = EmbedUtils.create_success_embed(
                f"Welcome to PocketRPG, **{self.character_name}**!",
                "Character Created"
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
                value=f"**{player.current_region.title()}**\n*Your adventure begins here!*",
                inline=True
            )
            
            # Add action buttons
            view = CharacterActionView(player, self.bot)
            
            embed.set_footer(text="Use the buttons below to get started!")
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        except Exception as e:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Error creating character: {str(e)}",
            )


class CharacterActionView(discord.ui.View):
    """View with action buttons for character actions and continuing after activities"""
    
    def __init__(self, player, bot, show_enemies=False):
        super().__init__(timeout=300)
        self.player = player
        self.bot = bot
        self.show_enemies = show_enemies
    
    @discord.ui.button(label="Explore", style=discord.ButtonStyle.success, emoji=Emojis.EXPLORE)
    async def explore(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Start exploring"""
        await self._show_exploration_view(interaction)
    
    @discord.ui.button(label="View Character", style=discord.ButtonStyle.secondary, emoji=Emojis.CHARACTER)
    async def view_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View character details"""
        embed = EmbedUtils.create_character_embed(self.player)
        await interaction.response.send_message(embed=embed, )
    
    @discord.ui.button(label="Inventory", style=discord.ButtonStyle.secondary, emoji=Emojis.INVENTORY)
    async def view_inventory(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View inventory contents"""
        embed = EmbedUtils.create_inventory_embed(self.player)
        view = InventoryView(self.player, self.bot)
        await interaction.response.send_message(embed=embed, view=view)
    
    async def _show_exploration_view(self, interaction: discord.Interaction):
        """Shared method to show exploration view"""
        # Get current region
        region_manager = self.bot.region_manager
        region_manager.set_current_region(self.player.current_region)
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
        
        # Available activities (only unlocked ones)
        unlocked_activities = current_region.get_unlocked_activities(self.player)
        if unlocked_activities:
            activity_text = "\n".join([f"• {activity.title()}" for activity in unlocked_activities])
            embed.add_field(
                name="🎯 Available Activities",
                value=activity_text,
                inline=True
            )
        
        # Show locked activities with unlock hints
        all_activities = current_region.available_activities
        locked_activities = [activity for activity in all_activities if not self.player.has_activity_unlocked(activity)]
        if locked_activities:
            locked_text = "\n".join([f"🔒 {activity.title()} (Coming Soon)" for activity in locked_activities])
            embed.add_field(
                name="🔒 Locked Activities",
                value=locked_text,
                inline=True
            )
        
        # Available enemies with discovery status
        enemies = current_region.get_enemies_with_discovery(self.player)
        if enemies:
            enemy_data = []
            for enemy in enemies:
                if enemy["discovered"]:
                    # Get enemy emoji from emoji manager
                    enemy_emoji = enemy["data"]["emoji"] if enemy["data"] else "👹"
                    
                    enemy_data.append(f"{enemy_emoji} {enemy['name']} (Level {enemy['level']})")
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


class InventoryView(discord.ui.View):
    """View for inventory actions"""
    
    def __init__(self, player, bot):
        super().__init__(timeout=300)
        self.player = player
        self.bot = bot
    
    @discord.ui.button(label="Inspect Item", style=discord.ButtonStyle.primary, emoji=Emojis.INSPECT)
    async def inspect_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open modal to inspect an item"""
        # Check if player has any items
        if not self.player.inventory.items:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Your inventory is empty! There's nothing to inspect.",
                ephemeral=True
            )
            return
        
        # Create and show the inspect view
        view = ItemInspectView(self.player)
        embed = discord.Embed(
            title=f"{Emojis.INSPECT} Inspect Item",
            description="Select an item from your inventory to view its details:",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class ItemInspectView(discord.ui.View):
    """View for selecting an item to inspect"""
    
    def __init__(self, player):
        super().__init__(timeout=300)
        self.player = player
        
        # Create dropdown with inventory items
        self.item_select = ItemSelectDropdown(player)
        self.add_item(self.item_select)


class ItemSelectDropdown(discord.ui.Select):
    """Dropdown for selecting items to inspect"""
    
    def __init__(self, player):
        self.player = player
        
        # Add options for each item in inventory
        options = []
        for item_name, item in player.inventory.items.items():
            # Add item emoji (try specific item first, then fallback to item type)
            # Use UIEmojis directly
            item_emoji = item.emoji
            
            label = f"{item_emoji} {item.name} x{item.quantity}"
            description = f"{item.item_type.value.title()} • {item.rarity.value.title()}"
            
            options.append(discord.SelectOption(
                label=label,
                description=description,
                value=item_name
            ))
        
        super().__init__(
            placeholder="Choose an item to inspect...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle item selection"""
        selected_item_name = self.values[0]
        item = self.player.inventory.get_item(selected_item_name)
        
        if not item:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Item not found in inventory!",
                ephemeral=True
            )
            return
        
        # Create detailed item embed
        embed = self.create_item_detail_embed(item)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def create_item_detail_embed(self, item) -> discord.Embed:
        """Create detailed item information embed"""
        # Get rarity color
        rarity_colors = {
            "common": discord.Color.light_grey(),
            "uncommon": discord.Color.green(),
            "rare": discord.Color.blue(),
            "epic": discord.Color.purple(),
            "legendary": discord.Color.gold()
        }
        
        color = rarity_colors.get(item.rarity.value, discord.Color.light_grey())
        
        # Get item emoji (try specific item first, then fallback to item type)
        # Use UIEmojis directly
        item_emoji = item.emoji
        
        embed = discord.Embed(
            title=f"{item_emoji} {item.name}",
            description=item.description or "No description available.",
            color=color
        )
        
        # Basic item info
        embed.add_field(
            name="📋 Basic Info",
            value=f"**Type:** {item.item_type.value.title()}\n**Rarity:** {item.rarity.value.title()}\n**Quality:** {item.quality.value.title()}\n**Value:** {item.value} gold",
            inline=True
        )
        
        # Quantity and stack info
        embed.add_field(
            name="📦 Inventory",
            value=f"**Quantity:** {item.quantity}\n**Stackable:** {'Yes' if item.stackable else 'No'}\n**Max Stack:** {item.max_stack}",
            inline=True
        )
        
        # Requirements
        requirements = []
        if item.level_requirement > 1:
            requirements.append(f"Level {item.level_requirement}")
        if item.class_requirement:
            requirements.append(f"{item.class_requirement.title()} Class")
        
        if requirements:
            embed.add_field(
                name="⚡ Requirements",
                value="\n".join(requirements),
                inline=True
            )
        
        # Item-specific details
        if hasattr(item, 'effects') and item.effects:
            effects_text = ""
            for effect in item.effects:
                effect_type = effect.get('type', 'unknown')
                amount = effect.get('amount', 0)
                if effect_type == 'heal':
                    effects_text += f"• Heals {amount} HP\n"
                elif effect_type == 'mana_restore':
                    effects_text += f"• Restores {amount} Mana\n"
                elif effect_type == 'stat_boost':
                    stat = effect.get('stat', 'unknown')
                    duration = effect.get('duration', 0)
                    effects_text += f"• +{amount} {stat.title()} for {duration} turns\n"
                else:
                    effects_text += f"• {effect_type.title()}: {amount}\n"
            
            if effects_text:
                embed.add_field(
                    name=f"{Emojis.BUFF} Effects",
                    value=effects_text.strip(),
                    inline=False
                )
        
        # Equipment-specific details
        if hasattr(item, 'damage') and item.damage:
            embed.add_field(
                name=f"{Emojis.ATTACK} Weapon Stats",
                value=f"**Damage:** {item.damage}",
                inline=True
            )
        
        if hasattr(item, 'defense') and item.defense:
            embed.add_field(
                name=f"{Emojis.DEFENSE} Armor Stats",
                value=f"**Defense:** {item.defense}",
                inline=True
            )
        
        # Stat bonuses
        if hasattr(item, 'stat_bonuses') and item.stat_bonuses:
            bonuses_text = ""
            for stat, bonus in item.stat_bonuses.items():
                bonuses_text += f"• +{bonus} {stat.title()}\n"
            
            if bonuses_text:
                embed.add_field(
                    name=f"{Emojis.STATS} Stat Bonuses",
                    value=bonuses_text.strip(),
                    inline=True
                )
        
        embed.set_footer(text=f"Item ID: {item.name}")
        
        return embed


class ActivitySelectionView(discord.ui.View):
    """View for selecting activities with buttons"""
    
    def __init__(self, player, bot):
        super().__init__(timeout=60)
        self.player = player
        self.bot = bot
        
        # Add buttons dynamically based on unlocked activities
        self._add_activity_buttons()
    
    def _add_activity_buttons(self):
        """Add buttons for unlocked activities"""
        # Get current region and unlocked activities
        region_manager = self.bot.region_manager
        region_manager.set_current_region(self.player.current_region)
        current_region = region_manager.get_current_region()
        
        if not current_region:
            return
        
        unlocked_activities = current_region.get_unlocked_activities(self.player)
        
        # Activity button configurations
        activity_configs = {
            "scout": {"label": "Scout", "style": discord.ButtonStyle.danger, "emoji": Emojis.INSPECT},
            "foraging": {"label": "Foraging", "style": discord.ButtonStyle.success, "emoji": Emojis.EXPLORE},
            "farming": {"label": "Farming", "style": discord.ButtonStyle.success, "emoji": Emojis.EXPLORE},
            "mining": {"label": "Mining", "style": discord.ButtonStyle.secondary, "emoji": Emojis.EXPLORE}
        }
        
        # Add buttons for unlocked activities
        for activity in unlocked_activities:
            if activity in activity_configs:
                config = activity_configs[activity]
                button = discord.ui.Button(
                    label=config["label"],
                    style=config["style"],
                    emoji=config["emoji"]
                )
                button.callback = lambda i, act=activity: self.start_activity(i, act)
                self.add_item(button)
    
    async def start_activity(self, interaction: discord.Interaction, activity: str):
        """Start the selected activity"""
        # Get current region
        region_manager = self.bot.region_manager
        region_manager.set_current_region(self.player.current_region)
        current_region = region_manager.get_current_region()
        
        if not current_region:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Error loading region data. Please try again later.",
            )
            return
        
        # Check if activity is unlocked
        if not self.player.has_activity_unlocked(activity.lower()):
            # Show placeholder message for locked activities
            placeholder_messages = {
                "farming": f"{Emojis.EXPLORE} **Farming** will be coming soon! This will be a minigame where you can grow crops and harvest resources.",
                "mining": f"{Emojis.EXPLORE} **Mining** will be coming soon! This will be a minigame where you can extract valuable minerals and ores."
            }
            
            message = placeholder_messages.get(activity.lower(), f"🔒 **{activity.title()}** is not yet available.")
            
            embed = discord.Embed(
                title="🚧 Coming Soon!",
                description=message,
                color=discord.Color.orange()
            )
            
            embed.add_field(
                name="💡 Tip",
                value="Try foraging to gather materials that might unlock new activities!",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            return
        
        # Check if activity is available in region
        available_activities = current_region.available_activities
        if activity.lower() not in available_activities:
            await interaction.response.send_message(
                f"{Emojis.ERROR} **{activity.title()}** is not available in {current_region.name}."
            )
            return
        
        # Load activity data
        activity_data = self.bot.region_manager.data_loader.load_activity(activity.lower())
        if not activity_data:
            await interaction.response.send_message(
                f"{Emojis.ERROR} Activity data not found for **{activity.title()}**.",
            )
            return
        
        # Check energy requirements
        energy_cost = activity_data.get('energy_cost', 0)
        if self.player.get_stat(StatType.MANA) < energy_cost:  # Using mana as energy for now
            await interaction.response.send_message(
                f"{Emojis.ERROR} Not enough energy! You need {energy_cost} energy to perform **{activity.title()}**.",
            )
            return
        
        # Perform activity
        await interaction.response.send_message(
            f"🎯 **{self.player.name}** is performing **{activity.title()}**...",
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
                    title=f"{Emojis.ATTACK} Enemy Encountered!",
                    description=f"**{self.player.name}** has encountered a **{enemy_data['name']}** while scouting!",
                    color=discord.Color.red()
                )
                
                # Get enemy emoji and set as thumbnail
                enemy_emoji = encounter["enemy_data"]["emoji"] if encounter["enemy_data"] else "👹"
                if enemy_emoji:
                    embed.set_thumbnail(url=enemy_emoji)
                
                embed.add_field(
                    name="👹 Enemy Details",
                    value=f"**Name:** {enemy_data['name']}\n**Level:** {enemy_data['base_level']}\n**Type:** {encounter_type.title()}",
                    inline=True
                )
                
                # Create enemy instance for combat
                from ...game.entities.enemy import Enemy, EnemyType, EnemyBehavior
                
                # Map enemy type from data to enum
                enemy_type_map = {
                    "normal": EnemyType.NORMAL,
                    "mini_boss": EnemyType.MINIBOSS,
                    "boss": EnemyType.BOSS
                }
                
                enemy_type = enemy_type_map.get(enemy_data.get('type', 'normal'), EnemyType.NORMAL)
                
                enemy_instance = Enemy(
                    name=enemy_data['name'],
                    enemy_type=enemy_type,
                    level=enemy_data['base_level'],
                    behavior=EnemyBehavior.AGGRESSIVE,
                    emoji=enemy_data.get('emoji', '👹')
                )
                
                # Load loot table from enemy data
                loot_table = enemy_data.get('loot_table', [])
                for loot_entry in loot_table:
                    enemy_instance.add_loot_item(
                        item_name=loot_entry['item'],
                        drop_chance=loot_entry['drop_chance'],
                        quantity=loot_entry['quantity'][0] if isinstance(loot_entry['quantity'], list) else loot_entry['quantity']
                    )
                
                # Start combat
                from ...game import Combat
                combat = Combat([self.player, enemy_instance])
                self.bot.set_combat(interaction.channel_id, combat)
                
                # Add combat button
                from .combat import CombatView
                combat_view = CombatView(self.player, enemy_instance, self.bot, encounter["enemy_id"])
                embed.set_footer(text="Choose your action!")
                
                await interaction.followup.send(embed=embed, view=combat_view)
                return
            else:
                # No encounter
                embed = discord.Embed(
                    title=f"{Emojis.INSPECT} Scout Complete",
                    description=f"**{self.player.name}** scouted the area but found no enemies.",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name=f"{Emojis.STATS} Results",
                    value=f"**Energy Used:** -{energy_cost}\n**Status:** Area is clear",
                    inline=True
                )
        else:
            # Regular activity - handle foraging minigame
            if activity.lower() == "foraging":
                # Start foraging minigame
                from .foraging_minigame import ForagingMinigameView
                
                # Create minigame view
                minigame_view = ForagingMinigameView(self.player, self.bot, activity_data)
                
                # Send minigame
                await interaction.followup.send(
                    embed=minigame_view.embed,
                    view=minigame_view
                )
                return
            
            # Show placeholder for other unimplemented activities
            embed = discord.Embed(
                title=f"🚧 {activity.title()} Coming Soon!",
                description=f"**{activity.title()}** will be implemented as a minigame in a future update.",
                color=discord.Color.orange()
            )
            
            embed.add_field(
                name="💡 Tip",
                value="Try foraging to gather materials that might unlock new activities!",
                inline=False
            )
            
            embed.add_field(
                name=f"{Emojis.STATS} Energy Used",
                value=f"-{energy_cost}",
                inline=True
            )
            
            # Send placeholder message
            await interaction.followup.send(embed=embed)
            return
        
        # Check for level up
        if self.player.level > 1:  # Simple level up check
            embed.add_field(
                name=f"{Emojis.COMPLETE} Level Up!",
                value=f"**{self.player.name}** is now level {self.player.level}!",
                inline=True
            )
        
        # Add continue button
        view = CharacterActionView(self.player, self.bot)
        
        embed.set_footer(text="Choose your next action!")
        
        # Send follow-up message
        await interaction.followup.send(embed=embed, view=view, )



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
                f"{Emojis.ERROR} You already have a character! Use `/character` to view your stats.",
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
                f"{Emojis.ERROR} You don't have a character yet! Use `/create_character` to create one.",
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
        
        embed.add_field(name=f"{Emojis.STATS} Stats", value=stats_text, inline=True)
        
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
        
        await interaction.response.send_message(embed=embed, view=view, )
    
    
    @app_commands.command(name="inventory", description="View your inventory and inspect items")
    async def inventory(self, interaction: discord.Interaction):
        """View inventory contents with inspect functionality"""
        user_id = interaction.user.id
        player, error_msg = PlayerUtils.get_player_or_error(self.bot, user_id)
        if not player:
            await ResponseUtils.send_error(interaction, error_msg, "No Character")
            return
        
        # Create inventory embed
        embed = EmbedUtils.create_inventory_embed(player)
        view = InventoryView(player, self.bot)
        
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    """Load the player cog"""
    await bot.add_cog(PlayerCog(bot))
