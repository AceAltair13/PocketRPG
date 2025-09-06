"""
Combat commands for PocketRPG Discord bot
Handles combat initiation, actions, and management
"""

import discord
from discord.ext import commands
from discord import app_commands
from ...game import Combat, data_loader
from ...game.enums import StatType


class CombatCog(commands.Cog):
    """Combat commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="combat", description="Start combat with an enemy")
    @app_commands.describe(enemy="The enemy you want to fight")
    async def start_combat(self, interaction: discord.Interaction, enemy: str):
        """Start combat with an enemy"""
        user_id = interaction.user.id
        player = self.bot.get_player(user_id)
        
        if not player:
            await interaction.response.send_message(
                "❌ You don't have a character yet! Use `/create_character` to create one.",
                ephemeral=True
            )
            return
        
        # Check if already in combat
        if self.bot.get_combat(interaction.channel_id):
            await interaction.response.send_message(
                "❌ There's already an active combat in this channel!",
                ephemeral=True
            )
            return
        
        # Get current region
        region_manager = self.bot.region_manager
        region_manager.set_current_region(player.current_region)
        current_region = region_manager.get_current_region()
        
        if not current_region:
            await interaction.response.send_message(
                "❌ Error loading region data. Please try again later.",
                ephemeral=True
            )
            return
        
        # Check if enemy is available in region
        available_enemies = current_region.get_available_enemies()
        if enemy.lower() not in [e.lower() for e in available_enemies]:
            await interaction.response.send_message(
                f"❌ **{enemy.title()}** is not available in {current_region.name}.\n\nAvailable enemies: {', '.join([e.title() for e in available_enemies])}",
                ephemeral=True
            )
            return
        
        # Load enemy data
        enemy_data = data_loader.load_enemy(enemy.lower())
        if not enemy_data:
            await interaction.response.send_message(
                f"❌ Enemy data not found for **{enemy.title()}**.",
                ephemeral=True
            )
            return
        
        # Create enemy instance (simplified for now)
        from ...game.entities.enemy import Enemy, EnemyType, EnemyBehavior
        enemy_instance = Enemy(
            name=enemy_data['name'],
            enemy_type=EnemyType.NORMAL,
            level=enemy_data['base_level'],
            behavior=EnemyBehavior.AGGRESSIVE
        )
        
        # Start combat
        combat = Combat([player, enemy_instance])
        self.bot.set_combat(interaction.channel_id, combat)
        
        # Create combat embed
        embed = discord.Embed(
            title="⚔️ Combat Started!",
            description=f"**{player.name}** vs **{enemy_instance.name}**",
            color=discord.Color.red()
        )
        
        # Player stats
        player_stats = f"**HP:** {player.get_stat(StatType.HEALTH)}/{player.get_stat(StatType.MAX_HEALTH)}\n**MP:** {player.get_stat(StatType.MANA)}/{player.get_stat(StatType.MAX_MANA)}"
        embed.add_field(name=f"👤 {player.name}", value=player_stats, inline=True)
        
        # Enemy stats
        enemy_stats = f"**HP:** {enemy_instance.get_stat(StatType.HEALTH)}/{enemy_instance.get_stat(StatType.MAX_HEALTH)}\n**Level:** {enemy_instance.level}"
        embed.add_field(name=f"👹 {enemy_instance.name}", value=enemy_stats, inline=True)
        
        embed.add_field(
            name="🎯 Actions",
            value="Use `/attack` to attack or `/defend` to defend!",
            inline=False
        )
        
        embed.set_footer(text="Combat is active! Choose your action.")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="attack", description="Attack in combat")
    async def attack(self, interaction: discord.Interaction):
        """Attack in combat"""
        user_id = interaction.user.id
        player = self.bot.get_player(user_id)
        
        if not player:
            await interaction.response.send_message(
                "❌ You don't have a character yet! Use `/create_character` to create one.",
                ephemeral=True
            )
            return
        
        # Check if in combat
        combat = self.bot.get_combat(interaction.channel_id)
        if not combat:
            await interaction.response.send_message(
                "❌ You're not in combat! Use `/combat` to start a fight.",
                ephemeral=True
            )
            return
        
        # Check if it's player's turn (simplified)
        if combat.turn_order[combat.current_turn] != player:
            await interaction.response.send_message(
                "❌ It's not your turn! Wait for your turn to attack.",
                ephemeral=True
            )
            return
        
        # Perform attack (simplified)
        enemy = None
        for participant in combat.participants:
            if participant != player:
                enemy = participant
                break
        
        if not enemy:
            await interaction.response.send_message(
                "❌ No enemy found in combat!",
                ephemeral=True
            )
            return
        
        # Calculate damage
        player_attack = player.get_stat(StatType.ATTACK)
        enemy_defense = enemy.get_stat(StatType.DEFENSE)
        damage = max(1, player_attack - enemy_defense)
        
        # Apply damage
        enemy.take_damage(damage)
        
        # Create attack embed
        embed = discord.Embed(
            title="⚔️ Attack!",
            description=f"**{player.name}** attacks **{enemy.name}** for **{damage}** damage!",
            color=discord.Color.orange()
        )
        
        # Check if enemy is defeated
        if not enemy.is_alive:
            embed.add_field(
                name="💀 Enemy Defeated!",
                value=f"**{enemy.name}** has been defeated!",
                inline=False
            )
            
            # Give rewards
            exp_reward = enemy.experience_reward
            gold_reward = enemy.gold_reward
            player.add_experience(exp_reward)
            player.add_gold(gold_reward)
            
            embed.add_field(
                name="🎁 Rewards",
                value=f"**Experience:** +{exp_reward}\n**Gold:** +{gold_reward}",
                inline=True
            )
            
            # End combat
            self.bot.remove_combat(interaction.channel_id)
            
            embed.set_footer(text="Combat ended! Use /explore to continue your adventure.")
        else:
            # Show current health
            embed.add_field(
                name="💔 Enemy Health",
                value=f"**{enemy.name}:** {enemy.get_stat(StatType.HEALTH)}/{enemy.get_stat(StatType.MAX_HEALTH)} HP",
                inline=True
            )
            
            embed.set_footer(text="Enemy's turn! Use /defend to reduce incoming damage.")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="defend", description="Defend in combat")
    async def defend(self, interaction: discord.Interaction):
        """Defend in combat"""
        user_id = interaction.user.id
        player = self.bot.get_player(user_id)
        
        if not player:
            await interaction.response.send_message(
                "❌ You don't have a character yet! Use `/create_character` to create one.",
                ephemeral=True
            )
            return
        
        # Check if in combat
        combat = self.bot.get_combat(interaction.channel_id)
        if not combat:
            await interaction.response.send_message(
                "❌ You're not in combat! Use `/combat` to start a fight.",
                ephemeral=True
            )
            return
        
        # Check if it's player's turn (simplified)
        if combat.turn_order[combat.current_turn] != player:
            await interaction.response.send_message(
                "❌ It's not your turn! Wait for your turn to defend.",
                ephemeral=True
            )
            return
        
        # Set defending state
        player.is_defending = True
        
        embed = discord.Embed(
            title="🛡️ Defend!",
            description=f"**{player.name}** takes a defensive stance!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🛡️ Defense Active",
            value="You will take reduced damage from the next attack!",
            inline=False
        )
        
        embed.set_footer(text="Enemy's turn! Your defense will reduce incoming damage.")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="flee", description="Flee from combat")
    async def flee(self, interaction: discord.Interaction):
        """Flee from combat"""
        user_id = interaction.user.id
        player = self.bot.get_player(user_id)
        
        if not player:
            await interaction.response.send_message(
                "❌ You don't have a character yet! Use `/create_character` to create one.",
                ephemeral=True
            )
            return
        
        # Check if in combat
        combat = self.bot.get_combat(interaction.channel_id)
        if not combat:
            await interaction.response.send_message(
                "❌ You're not in combat! Use `/combat` to start a fight.",
                ephemeral=True
            )
            return
        
        # End combat
        self.bot.remove_combat(interaction.channel_id)
        
        embed = discord.Embed(
            title="🏃‍♂️ Fled!",
            description=f"**{player.name}** has fled from combat!",
            color=discord.Color.yellow()
        )
        
        embed.set_footer(text="Combat ended! Use /explore to continue your adventure.")
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Load the cog"""
    await bot.add_cog(CombatCog(bot))
