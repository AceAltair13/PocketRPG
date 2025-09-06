# PocketRPG

A Discord-based RPG game where players can embark on adventures, battle monsters, and level up their characters using simple commands.

## Features (Planned)

- Character creation and management
- Turn-based combat system
- Quest system
- Inventory management
- Level progression
- Discord bot integration

## Project Structure

```
PocketRPG/
├── main.py              # Main entry point
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore file
├── data/               # Game content (JSON files)
│   ├── regions/        # Region definitions
│   ├── activities/     # Activity definitions
│   ├── items/          # Item definitions
│   └── enemies/        # Enemy definitions
├── src/                # Source code
│   ├── __init__.py
│   └── game/           # Game logic
│       ├── __init__.py # Main game module
│       ├── entities/   # Entity classes
│       ├── items/      # Item system
│       ├── systems/    # Game systems
│       ├── examples/   # Usage examples
│       ├── enums.py    # Game constants
│       ├── utils/      # Utility classes
│       ├── data_loader.py      # Data loading system
│       ├── player_creation.py  # Player creation
│       └── region.py           # Region system
└── tests/              # Test files
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up Discord bot:
   - Create a Discord application at https://discord.com/developers/applications
   - Create a bot and copy the token
   - Create a `.env` file with your Discord token:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

## Running the Project

```bash
python main.py
```

## Testing the Game Systems

```bash
# Run the example combat scenario
python -c "from src.game import run_example_combat; run_example_combat()"

# Test the new foundation systems
python -c "from src.game.examples.game_foundation_example import demonstrate_integration; demonstrate_integration()"

# Test simplified imports
python -c "from src.game import Player, Enemy, Combat, PlayerCreation; print('All imports working!')"
```

## Game Foundation

The game now has a solid foundation with:

- **Data-driven content**: All game content is defined in JSON files in the `data/` folder
- **Player creation system**: Create players with default stats and starting equipment
- **Region system**: Players start in "Grasslands" and can unlock new regions
- **Activity system**: Foundation for farming, mining, foraging, and combat
- **Incremental updates**: Add new content by simply adding JSON files
- **Discord bot integration**: Full Discord bot with slash commands and interactive gameplay

## Discord Bot Features

The Discord bot includes:

- **Interactive Character Management**: 
  - Modal-based character creation with name input
  - Button-based class selection (Warrior, Mage, Rogue, Cleric)
  - Interactive character stats with action buttons
- **Rich Exploration System**: 
  - Button-based activity selection (Combat, Foraging, Farming, Mining)
  - Interactive region exploration with enemy/activity buttons
  - Seamless activity flow with continue options
- **Engaging Combat System**: 
  - Button-based enemy selection
  - Interactive combat with Attack/Defend/Use Item/Flee buttons
  - Real-time combat updates with action buttons
  - Post-combat continuation options
- **Modern UI Components**: 
  - Discord Modals for text input
  - Interactive Buttons for actions
  - Rich Embeds for information display
  - Seamless user experience with UI components
- **Admin Tools**: Bot management and data reloading

### Adding New Content

To add new content, simply create JSON files in the appropriate `data/` subfolder:

- **New regions**: Add to `data/regions/`
- **New activities**: Add to `data/activities/`
- **New items**: Add to `data/items/`
- **New enemies**: Add to `data/enemies/`

## Development

This project is currently in early development. The Discord bot integration will be added in future updates.

## License

[Add your license here]
