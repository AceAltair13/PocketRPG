"""
Foraging minigame implementation with level-based progression
Grid size and item count increase with foraging skill level
"""

import discord
from discord.ext import commands
import random
from typing import List, Dict, Any, Optional, Tuple
from ...game.entities.player import Player
from ...game import data_loader
from ...game.items.item import ConsumableItem
from ...game.enums import ItemRarity, ItemQuality, StatType
# UIEmojis no longer needed - using Emojis constants
from ..utils import Emojis


class ForagingButton(discord.ui.Button):
    """Individual button in the foraging grid"""
    
    def __init__(self, row: int, col: int, has_loot: bool = False, loot_item: Optional[str] = None):
        # Use UIEmojis directly
        super().__init__(
            style=discord.ButtonStyle.secondary,
            label=Emojis.GRID_EMPTY,
            row=row,
            disabled=False
        )
        self.row = row
        self.col = col
        self.has_loot = has_loot
        self.loot_item = loot_item
        self.clicked = False
    
    async def callback(self, interaction: discord.Interaction):
        """Handle button click"""
        if self.clicked:
            await interaction.response.send_message("You already clicked this spot!", ephemeral=True)
            return
        
        # Get the view from the interaction
        view = self.view
        if not isinstance(view, ForagingMinigameView):
            await interaction.response.send_message("Invalid game state!", ephemeral=True)
            return
        
        # Handle the button click in the view
        await view.handle_button_click(interaction, self)


class ForagingMinigameView(discord.ui.View):
    """Level-based foraging minigame with progressive grid sizes"""
    
    def __init__(self, player: Player, bot: commands.Bot, activity_data: Dict[str, Any]):
        super().__init__(timeout=120)  # 2 minute timeout
        self.player = player
        self.bot = bot
        self.activity_data = activity_data
        
        # Get foraging level and set grid parameters
        self.foraging_level = player.get_activity_skill_level("foraging")
        self.grid_size, self.num_items, self.max_tries = self._get_level_parameters(self.foraging_level)
        
        # Game state
        self.current_tries = 0
        self.found_items: List[str] = []
        self.collected_items: List[ConsumableItem] = []
        self.game_over = False
        
        # Create the button grid
        self._create_button_grid()
        
        # Create status embed
        self.embed = self._create_initial_embed()
    
    def _get_level_parameters(self, level: int) -> Tuple[int, int, int]:
        """Get grid size, item count, and tries based on foraging level"""
        level_configs = {
            1: (3, 1, 2),  # 1x3 grid, 1 item, 2 tries
            2: (6, 2, 3),  # 2x3 grid, 2 items, 3 tries  
            3: (9, 3, 4),  # 3x3 grid, 3 items, 4 tries
            4: (16, 4, 5), # 4x4 grid, 4 items, 5 tries
            5: (25, 5, 6)  # 5x5 grid, 5 items, 6 tries
        }
        
        # Default to level 1 if level is invalid
        return level_configs.get(level, level_configs[1])
    
    def _create_button_grid(self):
        """Create the button grid based on foraging level"""
        # Clear any existing items
        self.clear_items()
        
        # Calculate grid dimensions
        if self.foraging_level == 1:
            rows, cols = 1, 3  # 1x3
        elif self.foraging_level == 2:
            rows, cols = 2, 3  # 2x3
        elif self.foraging_level == 3:
            rows, cols = 3, 3  # 3x3
        elif self.foraging_level == 4:
            rows, cols = 4, 4  # 4x4
        else:  # level 5+
            rows, cols = 5, 5  # 5x5
        
        # Place loot items randomly
        total_positions = rows * cols
        loot_positions = random.sample(range(total_positions), min(self.num_items, total_positions))
        
        # Create buttons
        for row in range(rows):
            for col in range(cols):
                position = row * cols + col
                has_loot = position in loot_positions
                loot_item = self._get_random_loot_item() if has_loot else None
                
                button = ForagingButton(
                    row=row,
                    col=col,
                    has_loot=has_loot,
                    loot_item=loot_item
                )
                
                self.add_item(button)
    
    def _create_initial_embed(self) -> discord.Embed:
        """Create the initial game embed"""
        # Use UIEmojis directly
        grid_desc = self._get_grid_description()
        
        embed = discord.Embed(
            title=f"{Emojis.EXPLORE} Foraging Minigame (Level {self.foraging_level})",
            description=f"Find the hidden plants and herbs! {grid_desc}",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="🎯 Instructions",
            value="Click the buttons to search for plants. Each button might contain herbs, berries, or mushrooms!",
            inline=False
        )
        
        embed.add_field(
            name=f"{Emojis.STATS} Game Status",
            value=f"**Tries Remaining:** {self.max_tries - self.current_tries}\n**Items Found:** {len(self.found_items)}/{self.num_items}",
            inline=True
        )
        
        embed.add_field(
            name="🎁 Found Items",
            value="None yet" if not self.found_items else "\n".join([f"• {item}" for item in self.found_items]),
            inline=True
        )
        
        embed.set_footer(text="Click the buttons below to start foraging!")
        
        return embed
    
    def _get_grid_description(self) -> str:
        """Get description of current grid configuration"""
        if self.foraging_level == 1:
            return "**Grid:** 1×3 | **Items:** 1 | **Tries:** 2"
        elif self.foraging_level == 2:
            return "**Grid:** 2×3 | **Items:** 2 | **Tries:** 3"
        elif self.foraging_level == 3:
            return "**Grid:** 3×3 | **Items:** 3 | **Tries:** 4"
        elif self.foraging_level == 4:
            return "**Grid:** 4×4 | **Items:** 4 | **Tries:** 5"
        else:
            return "**Grid:** 5×5 | **Items:** 5 | **Tries:** 6"
    
    def _update_embed(self, found_item: Optional[str] = None, button_clicked: Optional[Tuple[int, int]] = None):
        """Update the embed with current game state"""
        self.embed.clear_fields()
        
        # Update description based on game state
        if self.game_over:
            if len(self.found_items) == self.num_items:
                self.embed.description = f"{Emojis.COMPLETE} **Perfect!** You found all {self.num_items} hidden plants!"
                self.embed.color = discord.Color.gold()
            else:
                self.embed.description = f"⏰ **Game Over!** You found {len(self.found_items)} out of {self.num_items} plants."
                self.embed.color = discord.Color.orange()
        else:
            grid_desc = self._get_grid_description()
            self.embed.description = f"{Emojis.EXPLORE} Find the hidden plants and herbs! {grid_desc}"
        
        # Add instructions
        if not self.game_over:
            self.embed.add_field(
                name="🎯 Instructions",
                value="Click the buttons to search for plants. Each button might contain herbs, berries, or mushrooms!",
                inline=False
            )
        
        # Add game status
        status_text = f"**Tries Remaining:** {self.max_tries - self.current_tries}\n**Items Found:** {len(self.found_items)}/{self.num_items}"
        if button_clicked:
            row, col = button_clicked
            status_text += f"\n**Last Click:** Row {row+1}, Col {col+1}"
        
        self.embed.add_field(
            name=f"{Emojis.STATS} Game Status",
            value=status_text,
            inline=True
        )
        
        # Add found items
        if not self.found_items:
            found_text = "None yet"
        else:
            found_items_with_emojis = []
            for item_name in self.found_items:
                # Use material emoji as default for foraging items
                item_emoji = Emojis.MATERIAL
                found_items_with_emojis.append(f"• {item_emoji} {item_name}")
            found_text = "\n".join(found_items_with_emojis)
        self.embed.add_field(
            name="🎁 Found Items",
            value=found_text,
            inline=True
        )
        
        # Add footer
        if self.game_over:
            self.embed.set_footer(text="Game Over! Check your inventory for the items you found.")
        else:
            self.embed.set_footer(text=f"Click buttons to search! {self.max_tries - self.current_tries} tries remaining.")
    
    def _get_random_loot_item(self) -> str:
        """Get a random loot item based on activity data"""
        possible_rewards = self.activity_data.get("possible_rewards", [])
        if not possible_rewards:
            return "Unknown Item"
        
        # Create weighted list based on drop chances
        weighted_items = []
        for reward in possible_rewards:
            item_name = reward.get("item", "Unknown Item")
            chance = reward.get("chance", 0.1)
            # Add item multiple times based on chance (simple weighting)
            for _ in range(int(chance * 100)):
                weighted_items.append(item_name)
        
        if not weighted_items:
            return "Unknown Item"
        
        return random.choice(weighted_items)
    
    def _add_item_to_inventory(self, item_name: str):
        """Add found item to player's inventory"""
        # Get item data
        item_data = data_loader.load_item(item_name)
        if not item_data:
            # Create a basic item if not found
            item_data = {
                "id": item_name,
                "name": item_name.replace("_", " ").title(),
                "type": "material",
                "rarity": "common",
                "value": 1,
                "stackable": True,
                "max_stack": 99
            }
        
        # Map rarity from string to enum
        rarity_map = {
            "common": ItemRarity.COMMON,
            "uncommon": ItemRarity.UNCOMMON,
            "rare": ItemRarity.RARE,
            "epic": ItemRarity.EPIC,
            "legendary": ItemRarity.LEGENDARY
        }
        
        rarity = rarity_map.get(item_data.get("rarity", "common"), ItemRarity.COMMON)
        
        # Create the item
        item = ConsumableItem(
            name=item_data.get("name", item_name.replace("_", " ").title()),
            description=item_data.get("description", f"A {item_name.replace('_', ' ')} found while foraging."),
            rarity=rarity,
            value=item_data.get("value", 1),
            max_stack=item_data.get("max_stack", 99),
            emoji=item_data.get("emoji", "❓")
        )
        
        # Add to player inventory
        self.player.inventory.add_item(item, quantity=1)
        self.collected_items.append(item)
    
    async def handle_button_click(self, interaction: discord.Interaction, button: ForagingButton):
        """Handle button click in the minigame"""
        if self.game_over:
            await interaction.response.send_message(f"{Emojis.ERROR} The game is already over!", ephemeral=True)
            return
        
        if interaction.user.id != self.player.user_id:
            await interaction.response.send_message(f"{Emojis.ERROR} This isn't your foraging game!", ephemeral=True)
            return
        
        # Mark button as clicked
        button.clicked = True
        button.disabled = True
        self.current_tries += 1
        
        # Check if button has loot
        if button.has_loot and button.loot_item:
            # Found an item!
            # Use UIEmojis directly
            button.style = discord.ButtonStyle.success
            button.label = Emojis.GRID_FOUND
            self.found_items.append(button.loot_item)
            self._add_item_to_inventory(button.loot_item)
            
            # Check if all items found
            if len(self.found_items) >= self.num_items:
                self.game_over = True
                self._end_game()
                await interaction.response.edit_message(embed=self.embed, view=self)
                await interaction.followup.send(self._get_success_message())
                return
        else:
            # No loot found
            # Use UIEmojis directly
            button.style = discord.ButtonStyle.danger
            button.label = Emojis.GRID_MISS
        
        # Check if out of tries
        if self.current_tries >= self.max_tries:
            self.game_over = True
            self._end_game()
            await interaction.response.edit_message(embed=self.embed, view=self)
            await interaction.followup.send(self._get_failure_message())
            return
        
        # Update embed and continue
        self._update_embed(button_clicked=(button.row, button.col))
        await interaction.response.edit_message(embed=self.embed, view=self)
    
    def _end_game(self):
        """End the game and apply rewards"""
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        # Apply experience reward
        experience_reward = self.activity_data.get('experience_reward', 0)
        leveled_up = self.player.add_experience(experience_reward)
        
        # Add foraging experience (simplified - just add 1 per successful item found)
        foraging_leveled_up = self.player.add_activity_experience("foraging", len(self.found_items))
        
        # Consume energy
        energy_cost = self.activity_data.get('energy_cost', 0)
        self.player.modify_stat(StatType.MANA, -energy_cost)
        
        # Store level up info for messages
        self.player_leveled_up = leveled_up
        self.foraging_leveled_up = foraging_leveled_up
    
    def _get_success_message(self) -> str:
        """Get success message with rewards"""
        message = f"{Emojis.COMPLETE} **{self.player.name}** successfully foraged all items!\n\n"
        
        if self.collected_items:
            message += "**Collected Items:**\n"
            for item in self.collected_items:
                # Get item emoji
                # Use UIEmojis directly
                item_emoji = item.emoji
                message += f"• {item_emoji} {item.name}\n"
        
        message += f"\n**Experience Gained:** +{self.activity_data.get('experience_reward', 0)}\n"
        message += f"**Energy Used:** -{self.activity_data.get('energy_cost', 0)}\n"
        
        if hasattr(self, 'foraging_leveled_up') and self.foraging_leveled_up:
            new_level = self.player.get_activity_skill_level("foraging")
            message += f"\n🌟 **Foraging Level Up!** You're now level {new_level}!"
        
        if hasattr(self, 'player_leveled_up') and self.player_leveled_up:
            message += f"\n🎊 **Character Level Up!** You're now level {self.player.level}!"
        
        return message
    
    def _get_failure_message(self) -> str:
        """Get failure message with partial rewards"""
        message = f"😔 **{self.player.name}** ran out of tries while foraging.\n\n"
        
        if self.collected_items:
            message += "**Collected Items:**\n"
            for item in self.collected_items:
                # Get item emoji
                # Use UIEmojis directly
                item_emoji = item.emoji
                message += f"• {item_emoji} {item.name}\n"
            message += f"\n**Experience Gained:** +{self.activity_data.get('experience_reward', 0) // 2}\n"
        else:
            message += "**No items found this time.**\n"
            message += f"\n**Experience Gained:** +{self.activity_data.get('experience_reward', 0) // 4}\n"
        
        message += f"**Energy Used:** -{self.activity_data.get('energy_cost', 0)}\n"
        
        return message