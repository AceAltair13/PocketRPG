"""
Main Discord bot class for PocketRPG
Handles bot initialization, event handling, and command registration
"""

import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional
from ..game import PlayerCreation, RegionManager, data_loader
from ..game.enums import PlayerClass


class PocketRPG(commands.Bot):
    """
    Main Discord bot class for PocketRPG.
    Integrates the game systems with Discord functionality.
    """
    
    def __init__(self, command_prefix: str = "!", intents: discord.Intents = None):
        # Set up intents
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
        
        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            help_command=None,  # We'll create a custom help command
            case_insensitive=True
        )
        
        # Game systems
        self.region_manager = RegionManager()
        self.active_players = {}  # user_id -> Player
        self.active_combats = {}  # channel_id -> Combat
        
        # Bot configuration
        self.logger = logging.getLogger('PocketRPG')
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        self.logger.info("Setting up PocketRPG bot...")
        
        # Load all cogs (command modules)
        await self.load_cogs()
        
        # Sync slash commands to all guilds
        try:
            # Sync to all guilds the bot is in
            synced = await self.tree.sync()
            self.logger.info(f"Synced {len(synced)} slash commands globally")
            
            # Also sync to each guild individually for faster updates
            for guild in self.guilds:
                try:
                    guild_synced = await self.tree.sync(guild=guild)
                    self.logger.info(f"Synced {len(guild_synced)} commands to guild: {guild.name}")
                except Exception as guild_error:
                    self.logger.warning(f"Failed to sync commands to guild {guild.name}: {guild_error}")
                    
        except Exception as e:
            self.logger.error(f"Failed to sync commands: {e}")
    
    async def load_cogs(self):
        """Load all command cogs"""
        cogs = [
            'src.bot.cogs.player',
            'src.bot.cogs.game',
            'src.bot.cogs.combat',
            'src.bot.cogs.admin'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                self.logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                self.logger.error(f"Failed to load cog {cog}: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        self.logger.info(f"PocketRPG bot is ready! Logged in as {self.user}")
        self.logger.info(f"Bot is in {len(self.guilds)} guilds")
        
        # Set bot status
        activity = discord.Game(name="PocketRPG | /help")
        await self.change_presence(activity=activity)
    
    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild"""
        self.logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Sync commands to the new guild
        try:
            synced = await self.tree.sync(guild=guild)
            self.logger.info(f"Synced {len(synced)} commands to new guild: {guild.name}")
        except Exception as e:
            self.logger.error(f"Failed to sync commands to new guild {guild.name}: {e}")
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
            return
        
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument: {error}")
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
            return
        
        # Log unexpected errors
        self.logger.error(f"Unexpected error in command {ctx.command}: {error}")
        await ctx.send("❌ An unexpected error occurred. Please try again later.")
    
    def get_player(self, user_id: int):
        """Get a player by Discord user ID"""
        return self.active_players.get(user_id)
    
    def set_player(self, user_id: int, player):
        """Set a player for a Discord user ID"""
        self.active_players[user_id] = player
    
    def remove_player(self, user_id: int):
        """Remove a player from active players"""
        if user_id in self.active_players:
            del self.active_players[user_id]
    
    def get_combat(self, channel_id: int):
        """Get active combat in a channel"""
        return self.active_combats.get(channel_id)
    
    def set_combat(self, channel_id: int, combat):
        """Set active combat in a channel"""
        self.active_combats[channel_id] = combat
    
    def remove_combat(self, channel_id: int):
        """Remove active combat from a channel"""
        if channel_id in self.active_combats:
            del self.active_combats[channel_id]
    
    async def close(self):
        """Clean up when bot is shutting down"""
        self.logger.info("Shutting down PocketRPG bot...")
        await super().close()


def create_bot() -> PocketRPG:
    """Create and configure the PocketRPG bot"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    
    return PocketRPG()


async def run_bot(token: str):
    """Run the bot with the given token"""
    bot = create_bot()
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.close()
    except Exception as e:
        logging.error(f"Bot crashed: {e}")
        await bot.close()
