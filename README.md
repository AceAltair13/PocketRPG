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
├── src/                # Source code
│   ├── __init__.py
│   └── game/           # Game logic (restructured)
│       ├── __init__.py # Main game module with simplified imports
│       ├── entities/   # Entity classes (Player, Enemy, Entity)
│       ├── items/      # Item system (Item, Inventory, Equipment)
│       ├── systems/    # Game systems (Combat, Effects)
│       └── examples/   # Usage examples and demonstrations
├── tests/              # Test files
└── docs/               # Documentation
    ├── class_diagram.md
    └── restructured_architecture.md
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

# Test simplified imports
python -c "from src.game import Player, Enemy, Combat; print('All imports working!')"
```

## Development

This project is currently in early development. The Discord bot integration will be added in future updates.

## License

[Add your license here]
