"""
Combat commands with Discord UI components
Features interactive combat with buttons, select menus, and real-time updates
"""

import discord
from discord.ext import commands
from discord import app_commands
from ...game import Combat, data_loader
from ...game.enums import StatType
# UIEmojis no longer needed - using Emojis constants
from ..utils import Emojis




class CombatView(discord.ui.View):
    """View for combat actions"""
    
    def __init__(self, player, enemy, bot, enemy_id=None):
        super().__init__(timeout=60)
        self.player = player
        self.enemy = enemy
        self.bot = bot
        self.enemy_id = enemy_id
    
    @staticmethod
    def _health_bar(current: int, maximum: int, length: int = 12) -> str:
        current = max(0, min(current, maximum))
        filled = int(round(length * (current / maximum))) if maximum > 0 else 0
        empty = max(0, length - filled)
        return f"[{'█' * filled}{'—' * empty}]"

    def _append_health_fields(self, embed: discord.Embed) -> None:
        """Append single set of player/enemy HP fields with bars to the embed."""
        player_hp = self.player.get_stat(StatType.HEALTH)
        player_hp_max = self.player.get_stat(StatType.MAX_HEALTH)
        enemy_hp = self.enemy.get_stat(StatType.HEALTH)
        enemy_hp_max = self.enemy.get_stat(StatType.MAX_HEALTH)

        player_bar = self._health_bar(player_hp, player_hp_max)
        enemy_bar = self._health_bar(enemy_hp, enemy_hp_max)

        embed.add_field(
            name=f"👤 {self.player.name} HP",
            value=f"{player_hp}/{player_hp_max} {player_bar}\nEN: {self.player.get_stat(StatType.ENERGY)}/{self.player.get_stat(StatType.MAX_ENERGY)}",
            inline=True
        )
        enemy_emoji = self.enemy.emoji if self.enemy_id else "👹"
        embed.add_field(
            name=f"{enemy_emoji} {self.enemy.name} HP",
            value=f"{enemy_hp}/{enemy_hp_max} {enemy_bar}",
            inline=True
        )
    
    @discord.ui.button(label="Attack", style=discord.ButtonStyle.danger, emoji=Emojis.ATTACK)
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Attack the enemy"""
        await self.perform_attack(interaction)
    
    @discord.ui.button(label="Defend", style=discord.ButtonStyle.primary, emoji=Emojis.DEFENSE)
    async def defend_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Defend against enemy attack"""
        await self.perform_defend(interaction)
    
    @discord.ui.button(label="Use Item", style=discord.ButtonStyle.secondary, emoji=Emojis.CONSUMABLE)
    async def use_item_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Use an item in combat"""
        await self.show_items(interaction)
    
    @discord.ui.button(label="Flee", style=discord.ButtonStyle.secondary, emoji=Emojis.SPEED)
    async def flee_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Flee from combat"""
        await self.perform_flee(interaction)
    
    async def perform_attack(self, interaction: discord.Interaction):
        """Perform attack action"""
        # Check if in combat
        combat = self.bot.get_combat(interaction.channel_id)
        if not combat:
            await interaction.response.send_message(
                f"{Emojis.ERROR} You're not in combat!",
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
            title=f"{Emojis.ATTACK} Attack!",
            description=f"**{self.player.name}** attacks **{self.enemy.name}** for **{damage}** damage!",
            color=discord.Color.orange()
        )
        
        # Check if enemy is defeated
        if not self.enemy.is_alive:
            embed.add_field(
                name=f"{Emojis.DEBUFF} Enemy Defeated!",
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
                        # Create item instance using the proper item creation method
                        from ...game.items.item import ConsumableItem, WeaponItem, ArmorItem, EquipmentItem
                        from ...game.enums import ItemType, ItemRarity, ItemQuality
                        
                        item_type = ItemType(item_data['type'])
                        item_rarity = ItemRarity(item_data['rarity'])
                        item_quality = ItemQuality(item_data['quality'])
                        item_emoji = item_data.get('emoji', '❓')
                        
                        # Create the appropriate item subclass based on type
                        if item_type == ItemType.CONSUMABLE:
                            item = ConsumableItem(
                                name=item_data['name'],
                                description=item_data['description'],
                                rarity=item_rarity,
                                quality=item_quality,
                                value=item_data['value'],
                                emoji=item_emoji
                            )
                        elif item_type == ItemType.WEAPON:
                            item = WeaponItem(
                                name=item_data['name'],
                                description=item_data['description'],
                                rarity=item_rarity,
                                quality=item_quality,
                                value=item_data['value'],
                                level_requirement=item_data.get('level_requirement', 1),
                                emoji=item_emoji
                            )
                        elif item_type == ItemType.ARMOR:
                            item = ArmorItem(
                                name=item_data['name'],
                                description=item_data['description'],
                                rarity=item_rarity,
                                quality=item_quality,
                                value=item_data['value'],
                                level_requirement=item_data.get('level_requirement', 1),
                                emoji=item_emoji
                            )
                        else:
                            # Default to EquipmentItem for other types
                            item = EquipmentItem(
                                name=item_data['name'],
                                item_type=item_type,
                                description=item_data['description'],
                                rarity=item_rarity,
                                quality=item_quality,
                                value=item_data['value'],
                                emoji=item_emoji
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
            from .player import CharacterActionView
            view = CharacterActionView(self.player, self.bot, show_enemies=True)
            
            embed.set_footer(text="Combat ended! Choose your next action.")
        else:
            # Enemy's turn (enemy_turn will append health bars once)
            await self.enemy_turn(embed)
            
            # Check if player is defeated
            if not self.player.is_alive:
                embed.add_field(
                    name=f"{Emojis.DEBUFF} Defeat!",
                    value=f"**{self.player.name}** has been defeated!",
                    inline=False
                )
                
                # End combat
                self.bot.remove_combat(interaction.channel_id)
                
                embed.set_footer(text="Combat ended! You were defeated.")
                view = None
            else:
                # Continue combat
                view = CombatView(self.player, self.enemy, self.bot, self.enemy_id)
                embed.set_footer(text="Your turn! Choose your action.")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def perform_defend(self, interaction: discord.Interaction):
        """Perform defend action"""
        # Set defending state
        self.player.is_defending = True
        
        embed = discord.Embed(
            title=f"{Emojis.DEFENSE} Defend!",
            description=f"**{self.player.name}** takes a defensive stance!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name=f"{Emojis.DEFENSE} Defense Active",
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
            view = CombatView(self.player, self.enemy, self.bot, self.enemy_id)
            embed.set_footer(text="Your turn! Choose your action.")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_items(self, interaction: discord.Interaction):
        """Show available items"""
        # Check if player has items
        if not self.player.inventory.items:
            await interaction.response.send_message(
                f"{Emojis.ERROR} You don't have any items to use!",
            )
            return
        
        # Create item selection view
        view = ItemSelectionView(self.player, self.enemy, self.bot)
        
        embed = discord.Embed(
            title=f"{Emojis.CONSUMABLE} Use Item",
            description="Select an item to use in combat:",
            color=discord.Color.purple()
        )
        
        # Add item buttons (iterate actual Item objects)
        for item in self.player.inventory.get_all_items():
            if getattr(item, 'quantity', 0) > 0:
                item_emoji = getattr(item, 'emoji', Emojis.MATERIAL)
                button = discord.ui.Button(
                    label=f"{item.name} x{item.quantity}",
                    style=discord.ButtonStyle.secondary,
                    emoji=item_emoji
                )
                button.callback = (lambda i, name=item.name: self.use_item(i, name))
                view.add_item(button)
        
        # Add back button
        back_button = discord.ui.Button(
            label="Back to Combat",
            style=discord.ButtonStyle.secondary,
            emoji=Emojis.INSPECT
        )
        back_button.callback = self.back_to_combat
        view.add_item(back_button)
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def use_item(self, interaction: discord.Interaction, item_name: str):
        """Use selected item"""
        # This would implement item usage logic
        embed = discord.Embed(
            title=f"{Emojis.CONSUMABLE} Item Used",
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
        view = CombatView(self.player, self.enemy, self.bot, self.enemy_id)
        embed.set_footer(text="Your turn! Choose your action.")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def back_to_combat(self, interaction: discord.Interaction):
        """Return to combat view"""
        embed = discord.Embed(
            title=f"{Emojis.ATTACK} Combat",
            description=f"**{self.player.name}** vs **{self.enemy.name}**",
            color=discord.Color.red()
        )
        
        # Set enemy emoji as thumbnail
        if hasattr(self.enemy, 'emoji') and self.enemy.emoji:
            from ..utils import EmbedUtils
            emoji_url = EmbedUtils.emoji_to_url(self.enemy.emoji)
            if emoji_url:
                embed.set_thumbnail(url=emoji_url)
        
        # Player and enemy health with bars
        self._append_health_fields(embed)
        embed.add_field(name="Level", value=f"{self.enemy.level}", inline=True)
        
        embed.add_field(
            name="🎯 Actions",
            value="Choose your action below!",
            inline=False
        )
        
        view = CombatView(self.player, self.enemy, self.bot, self.enemy_id)
        embed.set_footer(text="Combat is active! Choose your action.")
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def perform_flee(self, interaction: discord.Interaction):
        """Perform flee action"""
        # End combat
        self.bot.remove_combat(interaction.channel_id)
        
        embed = discord.Embed(
            title=f"{Emojis.SPEED} Fled!",
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

        # Append current HP bars once after damage
        self._append_health_fields(embed)


class ItemSelectionView(discord.ui.View):
    """View for selecting items to use"""
    
    def __init__(self, player, enemy, bot):
        super().__init__(timeout=60)
        self.player = player
        self.enemy = enemy
        self.bot = bot




class CombatCog(commands.Cog):
    """Combat commands with interactive UI components"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # Combat command removed - use scout activity instead


async def setup(bot):
    """Load the combat cog"""
    await bot.add_cog(CombatCog(bot))
