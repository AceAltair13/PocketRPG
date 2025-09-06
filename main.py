"""
PocketRPG - A Discord-based RPG game
Main entry point for the Discord bot application
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from src.bot.bot import run_bot


def main():
    """Main function to start the PocketRPG Discord bot"""
    # Load environment variables
    load_dotenv()
    
    # Get Discord token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token.")
        print("See env.example for reference.")
        return
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎮 PocketRPG Discord Bot - Starting up...")
    print("🤖 Bot is connecting to Discord...")
    
    # Run the bot
    try:
        asyncio.run(run_bot(token))
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        logging.error(f"Bot crashed: {e}")


if __name__ == "__main__":
    main()
