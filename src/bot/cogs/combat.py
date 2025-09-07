"""
Combat commands with Discord UI components
Features interactive combat with buttons, select menus, and real-time updates
"""

import discord
from discord.ext import commands
from discord import app_commands
from ...game import Combat, data_loader
from ...game.enums import StatType
from ...utils.emoji_manager import get_emoji_manager


class EnemySelectionView(discord.ui.View):
    """View for selecting enemies to fight"""
    
    def __init__(self, player, bot):
        super().__init__(timeout=60)
        self.player = player
        self.bot = bot
    
    async def create_enemy_buttons(self, interaction: discord.Interaction):
        """Create buttons for available enemies"""
        # Get current region
        region_manager = self.bot.region_manager
        region_manager.set_current_region(self.player.current_region)
        current_region = region_manager.get_current_region()
        
        if not current_region:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} Error loading region data. Please try again later.",
            )
            return
        
        # Get available enemies with discovery status
        available_enemies = current_region.get_enemies_with_discovery(self.player)
        
        if not available_enemies:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} No enemies available in {current_region.name}.",
            )
            return
        
        # Create buttons for each enemy
        for enemy in available_enemies:
            if enemy["discovered"]:
                # Show enemy type with emoji
                type_emoji = {
                    "normal": "👹",
                    "mini_boss": "🔥",
                    "boss": "👑"
                }.get(enemy["type"], "👹")
                
                button = discord.ui.Button(
                    label=f"{enemy['name']} (Lv.{enemy['level']})",
                    style=discord.ButtonStyle.danger,
                    emoji=type_emoji
                )
                button.callback = lambda i, eid=enemy["id"]: self.start_combat(i, eid)
                self.add_item(button)
            else:
                # Show unknown enemy
                button = discord.ui.Button(
                    label="Unknown Enemy",
                    style=discord.ButtonStyle.secondary,
                    emoji="❓"
                )
                button.callback = lambda i, eid=enemy["id"]: self.start_combat(i, eid)
                self.add_item(button)
        
        # Add cancel button
        cancel_button = discord.ui.Button(
            label="Cancel",
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji_manager().get_status_emoji('error')
        )
        cancel_button.callback = self.cancel_combat
        self.add_item(cancel_button)
    
    async def start_combat(self, interaction: discord.Interaction, enemy_id: str):
        """Start combat with selected enemy"""
        # Check if already in combat
        if self.bot.get_combat(interaction.channel_id):
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} There's already an active combat in this channel!",
            )
            return
        
        # Load enemy data
        enemy_data = data_loader.load_enemy(enemy_id)
        if not enemy_data:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} Enemy data not found for **{enemy_id}**.",
            )
            return
        
        # Create enemy instance
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
            behavior=EnemyBehavior.AGGRESSIVE
        )
        
        # Discover the enemy
        self.player.discover_enemy(enemy_id)
        
        # Start combat
        combat = Combat([self.player, enemy_instance])
        self.bot.set_combat(interaction.channel_id, combat)
        
        # Create combat embed
        embed = discord.Embed(
            title=f"{get_emoji_manager().get_activity_emoji('combat')} Combat Started!",
            description=f"**{self.player.name}** vs **{enemy_instance.name}**",
            color=discord.Color.red()
        )
        
        # Player stats
        player_stats = f"**HP:** {self.player.get_stat(StatType.HEALTH)}/{self.player.get_stat(StatType.MAX_HEALTH)}\n**MP:** {self.player.get_stat(StatType.MANA)}/{self.player.get_stat(StatType.MAX_MANA)}"
        embed.add_field(name=f"👤 {self.player.name}", value=player_stats, inline=True)
        
        # Enemy stats
        enemy_stats = f"**HP:** {enemy_instance.get_stat(StatType.HEALTH)}/{enemy_instance.get_stat(StatType.MAX_HEALTH)}\n**Level:** {enemy_instance.level}"
        embed.add_field(name=f"👹 {enemy_instance.name}", value=enemy_stats, inline=True)
        
        embed.add_field(
            name="🎯 Actions",
            value="Choose your action below!",
            inline=False
        )
        
        # Create combat view
        view = CombatView(self.player, enemy_instance, self.bot)
        
        embed.set_footer(text="Combat is active! Choose your action.")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def cancel_combat(self, interaction: discord.Interaction):
        """Cancel combat selection"""
        embed = discord.Embed(
            title=f"{get_emoji_manager().get_status_emoji('error')} Combat Cancelled",
            description="You decided not to fight any enemies.",
            color=discord.Color.gray()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)


class CombatView(discord.ui.View):
    """View for combat actions"""
    
    def __init__(self, player, enemy, bot):
        super().__init__(timeout=60)
        self.player = player
        self.enemy = enemy
        self.bot = bot
    
    @discord.ui.button(label="Attack", style=discord.ButtonStyle.danger, emoji=get_emoji_manager().get_ui_emoji('attack'))
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Attack the enemy"""
        await self.perform_attack(interaction)
    
    @discord.ui.button(label="Defend", style=discord.ButtonStyle.primary, emoji=get_emoji_manager().get_ui_emoji('defense'))
    async def defend_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Defend against enemy attack"""
        await self.perform_defend(interaction)
    
    @discord.ui.button(label="Use Item", style=discord.ButtonStyle.secondary, emoji=get_emoji_manager().get_item_emoji('consumable'))
    async def use_item_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Use an item in combat"""
        await self.show_items(interaction)
    
    @discord.ui.button(label="Flee", style=discord.ButtonStyle.secondary, emoji=get_emoji_manager().get_ui_emoji('speed'))
    async def flee_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Flee from combat"""
        await self.perform_flee(interaction)
    
    async def perform_attack(self, interaction: discord.Interaction):
        """Perform attack action"""
        # Check if in combat
        combat = self.bot.get_combat(interaction.channel_id)
        if not combat:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} You're not in combat!",
            )
            return
        
        # Calculate damage
        player_attack = self.player.get_stat(StatType.ATTACK)
        enemy_defense = self.enemy.get_stat(StatType.DEFENSE)
        damage = max(1, player_attack - enemy_defense)
        
        # Apply damage
        self.enemy.take_damage(damage)
        
        # Create attack embed
        embed = discord.Embed(
            title=f"{get_emoji_manager().get_ui_emoji('attack')} Attack!",
            description=f"**{self.player.name}** attacks **{self.enemy.name}** for **{damage}** damage!",
            color=discord.Color.orange()
        )
        
        # Check if enemy is defeated
        if not self.enemy.is_alive:
            embed.add_field(
                name=f"{get_emoji_manager().get_effects_emoji('debuff')} Enemy Defeated!",
                value=f"**{self.enemy.name}** has been defeated!",
                inline=False
            )
            
            # Give rewards
            exp_reward = self.enemy.experience_reward
            gold_reward = self.enemy.gold_reward
            self.player.add_experience(exp_reward)
            self.player.add_gold(gold_reward)
            
            # Generate and give loot drops
            loot_drops = self.enemy.generate_loot()
            loot_text = ""
            
            if loot_drops:
                for loot in loot_drops:
                    item_id = loot['item_name']
                    quantity = loot['quantity']
                    
                    # Load item data
                    item_data = self.bot.region_manager.data_loader.load_item(item_id)
                    if item_data:
                        # Create item instance
                        from ...game.items.item import Item
                        from ...game.enums import ItemType, ItemRarity, ItemQuality
                        
                        item = Item(
                            name=item_data['name'],
                            item_type=ItemType(item_data['type']),
                            description=item_data['description'],
                            rarity=ItemRarity(item_data['rarity']),
                            quality=ItemQuality(item_data['quality']),
                            value=item_data['value']
                        )
                        
                        # Add to player inventory
                        self.player.inventory.add_item(item, quantity)
                        
                        # Add to loot display
                        loot_text += f"• **{item.name}** x{quantity}\n"
            
            # Create rewards text
            rewards_text = f"**Experience:** +{exp_reward}\n**Gold:** +{gold_reward}"
            if loot_text:
                rewards_text += f"\n\n**Loot Drops:**\n{loot_text.strip()}"
            
            embed.add_field(
                name="🎁 Rewards",
                value=rewards_text,
                inline=True
            )
            
            # End combat
            self.bot.remove_combat(interaction.channel_id)
            
            # Add continue button
            view = ContinueAfterCombatView(self.player, self.bot)
            
            embed.set_footer(text="Combat ended! Choose your next action.")
        else:
            # Show current health
            embed.add_field(
                name="💔 Enemy Health",
                value=f"**{self.enemy.name}:** {self.enemy.get_stat(StatType.HEALTH)}/{self.enemy.get_stat(StatType.MAX_HEALTH)} HP",
                inline=True
            )
            
            # Enemy's turn
            await self.enemy_turn(embed)
            
            # Check if player is defeated
            if not self.player.is_alive:
                embed.add_field(
                    name=f"{get_emoji_manager().get_effects_emoji('debuff')} Defeat!",
                    value=f"**{self.player.name}** has been defeated!",
                    inline=False
                )
                
                # End combat
                self.bot.remove_combat(interaction.channel_id)
                
                embed.set_footer(text="Combat ended! You were defeated.")
                view = None
            else:
                # Continue combat
                view = CombatView(self.player, self.enemy, self.bot)
                embed.set_footer(text="Your turn! Choose your action.")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def perform_defend(self, interaction: discord.Interaction):
        """Perform defend action"""
        # Set defending state
        self.player.is_defending = True
        
        embed = discord.Embed(
            title=f"{get_emoji_manager().get_ui_emoji('defense')} Defend!",
            description=f"**{self.player.name}** takes a defensive stance!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name=f"{get_emoji_manager().get_ui_emoji('defense')} Defense Active",
            value="You will take reduced damage from the next attack!",
            inline=False
        )
        
        # Enemy's turn
        await self.enemy_turn(embed)
        
        # Check if player is defeated
        if not self.player.is_alive:
            embed.add_field(
                name="💀 Defeat!",
                value=f"**{self.player.name}** has been defeated!",
                inline=False
            )
            
            # End combat
            self.bot.remove_combat(interaction.channel_id)
            
            embed.set_footer(text="Combat ended! You were defeated.")
            view = None
        else:
            # Continue combat
            view = CombatView(self.player, self.enemy, self.bot)
            embed.set_footer(text="Your turn! Choose your action.")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_items(self, interaction: discord.Interaction):
        """Show available items"""
        # Check if player has items
        if not self.player.inventory.items:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} You don't have any items to use!",
            )
            return
        
        # Create item selection view
        view = ItemSelectionView(self.player, self.enemy, self.bot)
        
        embed = discord.Embed(
            title=f"{get_emoji_manager().get_item_emoji('consumable')} Use Item",
            description="Select an item to use in combat:",
            color=discord.Color.purple()
        )
        
        # Add item buttons
        for item_name, item_data in self.player.inventory.items.items():
            if item_data['quantity'] > 0:
                button = discord.ui.Button(
                    label=f"{item_name} x{item_data['quantity']}",
                    style=discord.ButtonStyle.secondary,
                    emoji=get_emoji_manager().get_item_emoji('consumable')
                )
                button.callback = lambda i, name=item_name: self.use_item(i, name)
                view.add_item(button)
        
        # Add back button
        back_button = discord.ui.Button(
            label="Back to Combat",
            style=discord.ButtonStyle.secondary,
            emoji=get_emoji_manager().get_ui_emoji('inspect')
        )
        back_button.callback = self.back_to_combat
        view.add_item(back_button)
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def use_item(self, interaction: discord.Interaction, item_name: str):
        """Use selected item"""
        # This would implement item usage logic
        embed = discord.Embed(
            title=f"{get_emoji_manager().get_item_emoji('consumable')} Item Used",
            description=f"**{self.player.name}** used **{item_name}**!",
            color=discord.Color.purple()
        )
        
        # For now, just show a message
        embed.add_field(
            name="Effect",
            value="Item effect would be applied here!",
            inline=False
        )
        
        # Continue combat
        view = CombatView(self.player, self.enemy, self.bot)
        embed.set_footer(text="Your turn! Choose your action.")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def back_to_combat(self, interaction: discord.Interaction):
        """Return to combat view"""
        embed = discord.Embed(
            title=f"{get_emoji_manager().get_activity_emoji('combat')} Combat",
            description=f"**{self.player.name}** vs **{self.enemy.name}**",
            color=discord.Color.red()
        )
        
        # Player stats
        player_stats = f"**HP:** {self.player.get_stat(StatType.HEALTH)}/{self.player.get_stat(StatType.MAX_HEALTH)}\n**MP:** {self.player.get_stat(StatType.MANA)}/{self.player.get_stat(StatType.MAX_MANA)}"
        embed.add_field(name=f"👤 {self.player.name}", value=player_stats, inline=True)
        
        # Enemy stats
        enemy_stats = f"**HP:** {self.enemy.get_stat(StatType.HEALTH)}/{self.enemy.get_stat(StatType.MAX_HEALTH)}\n**Level:** {self.enemy.level}"
        embed.add_field(name=f"👹 {self.enemy.name}", value=enemy_stats, inline=True)
        
        embed.add_field(
            name="🎯 Actions",
            value="Choose your action below!",
            inline=False
        )
        
        view = CombatView(self.player, self.enemy, self.bot)
        embed.set_footer(text="Combat is active! Choose your action.")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def perform_flee(self, interaction: discord.Interaction):
        """Perform flee action"""
        # End combat
        self.bot.remove_combat(interaction.channel_id)
        
        embed = discord.Embed(
            title=f"{get_emoji_manager().get_ui_emoji('speed')} Fled!",
            description=f"**{self.player.name}** has fled from combat!",
            color=discord.Color.yellow()
        )
        
        embed.set_footer(text="Combat ended! Use /explore to continue your adventure.")
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    async def enemy_turn(self, embed: discord.Embed):
        """Handle enemy's turn"""
        # Simple enemy AI - just attack
        enemy_attack = self.enemy.get_stat(StatType.ATTACK)
        player_defense = self.player.get_stat(StatType.DEFENSE)
        
        # Reduce damage if defending
        if self.player.is_defending:
            player_defense += 5  # Defense bonus
            self.player.is_defending = False  # Reset defense
        
        damage = max(1, enemy_attack - player_defense)
        self.player.take_damage(damage)
        
        embed.add_field(
            name="👹 Enemy Attack!",
            value=f"**{self.enemy.name}** attacks **{self.player.name}** for **{damage}** damage!",
            inline=False
        )


class ItemSelectionView(discord.ui.View):
    """View for selecting items to use"""
    
    def __init__(self, player, enemy, bot):
        super().__init__(timeout=60)
        self.player = player
        self.enemy = enemy
        self.bot = bot


class ContinueAfterCombatView(discord.ui.View):
    """View for actions after combat"""
    
    def __init__(self, player, bot):
        super().__init__(timeout=60)
        self.player = player
        self.bot = bot
    
    @discord.ui.button(label="Continue Exploring", style=discord.ButtonStyle.primary, emoji=get_emoji_manager().get_ui_emoji('explore'))
    async def continue_exploring(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Continue exploring after combat"""
        # Get current region
        region_manager = self.bot.region_manager
        region_manager.set_current_region(self.player.current_region)
        current_region = region_manager.get_current_region()
        
        if not current_region:
            await interaction.response.send_message(
                f"{get_emoji_manager().get_status_emoji('error')} Error loading region data. Please try again later.",
            )
            return
        
        # Create exploration embed
        embed = discord.Embed(
            title=f"{get_emoji_manager().get_ui_emoji('explore')} Exploring {current_region.name}",
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
                enemy = self.bot.region_manager.data_loader.load_enemy(enemy_id)
                if enemy:
                    enemy_data.append(f"• {enemy['name']} (Level {enemy['base_level']})")
            
            if enemy_data:
                embed.add_field(
                    name="👹 Enemies",
                    value="\n".join(enemy_data),
                    inline=True
                )
        
        # Add activity selection
        from .player import ActivitySelectionView
        view = ActivitySelectionView(self.player, self.bot)
        
        embed.set_footer(text="Choose an activity to continue!")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="View Character", style=discord.ButtonStyle.secondary, emoji=get_emoji_manager().get_ui_emoji('character'))
    async def view_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View character details"""
        embed = self.create_character_embed()
        await interaction.response.send_message(embed=embed, )
    
    def create_character_embed(self):
        """Create character information embed"""
        embed = discord.Embed(
            title=f"{get_emoji_manager().get_ui_emoji('character')} {self.player.name} - Level {self.player.level} {self.player.player_class.value.title()}",
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
        
        embed.add_field(name=f"{get_emoji_manager().get_ui_emoji('stats')} Stats", value=stats_text, inline=True)
        
        # Equipment section
        equipped_weapon = None
        for slot, item in self.player.equipment.equipped_items.items():
            if item is not None:
                equipped_weapon = item
                break
        
        equipment_text = f"**Weapon:** {equipped_weapon.name if equipped_weapon else 'None'}\n**Gold:** {self.player.gold}\n**Skill Points:** {self.player.skill_points}"
        
        embed.add_field(name=f"{get_emoji_manager().get_ui_emoji('equipment')} Equipment", value=equipment_text, inline=True)
        
        # Location section
        embed.add_field(name=f"{get_emoji_manager().get_ui_emoji('location')} Location", value=f"**{self.player.current_region.title()}**", inline=True)
        
        return embed


class CombatCog(commands.Cog):
    """Combat commands with interactive UI components"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # Combat command removed - use scout activity instead


async def setup(bot):
    """Load the combat cog"""
    await bot.add_cog(CombatCog(bot))
