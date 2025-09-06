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
