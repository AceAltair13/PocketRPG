# PocketRPG - Restructured Architecture

## New Directory Structure

The codebase has been reorganized into a more logical and maintainable structure:

```
src/game/
├── __init__.py              # Main game module with simplified imports
├── entities/                # Entity-related classes
│   ├── __init__.py
│   ├── entity.py           # Base Entity class
│   ├── player.py           # Player class
│   └── enemy.py            # Enemy class
├── items/                   # Item-related classes and systems
│   ├── __init__.py
│   ├── item.py             # Item hierarchy (Item, ConsumableItem, EquipmentItem, etc.)
│   ├── inventory.py        # Inventory management system
│   └── equipment.py        # Equipment and stat bonus system
├── systems/                 # Game systems and mechanics
│   ├── __init__.py
│   ├── combat.py           # Turn-based combat system
│   └── effect.py           # Status effects and buffs/debuffs
└── examples/                # Example usage and demonstrations
    ├── __init__.py
    └── example.py          # Example combat scenarios and demonstrations
```

## Benefits of the New Structure

### 1. **Logical Grouping**
- **Entities**: All living things in the game (players, enemies, NPCs)
- **Items**: All item-related functionality (items, inventory, equipment)
- **Systems**: Core game mechanics (combat, effects, etc.)
- **Examples**: Demonstrations and usage examples

### 2. **Improved Maintainability**
- Related functionality is grouped together
- Easier to find and modify specific features
- Clear separation of concerns
- Better code organization for team development

### 3. **Simplified Imports**
- Main classes available through `from src.game import ...`
- Module-specific imports still available
- Cleaner import statements throughout the codebase

### 4. **Scalability**
- Easy to add new entity types in `entities/`
- Simple to extend item system in `items/`
- New game systems can be added to `systems/`
- Examples can be organized by feature in `examples/`

## Import Examples

### Simplified Imports (Recommended)
```python
# Import main classes directly from game module
from src.game import Player, Enemy, Combat, Item, Effect

# Create a player and enemy
player = Player("Hero", PlayerClass.WARRIOR)
enemy = Enemy("Goblin", EnemyType.NORMAL)

# Start combat
combat = Combat([player, enemy])
result = combat.start_combat()
```

### Module-Specific Imports
```python
# Import from specific modules
from src.game.entities import Player, Enemy, PlayerClass, EnemyType
from src.game.items import Item, Inventory, Equipment
from src.game.systems import Combat, Effect, CombatResult
```

### Individual File Imports
```python
# Import from individual files (for specific functionality)
from src.game.entities.player import Player, PlayerClass
from src.game.items.inventory import Inventory
from src.game.systems.combat import Combat, CombatAction
```

## Module Responsibilities

### Entities Module (`src/game/entities/`)
- **entity.py**: Base class for all living entities with stats, health, and status effects
- **player.py**: Player-specific functionality including classes, inventory, equipment
- **enemy.py**: Enemy AI, behaviors, and loot systems

### Items Module (`src/game/items/`)
- **item.py**: Item hierarchy (consumables, equipment, weapons, armor, quest items)
- **inventory.py**: Item storage, stacking, and management
- **equipment.py**: Equipment slots, stat bonuses, and set bonuses

### Systems Module (`src/game/systems/`)
- **combat.py**: Turn-based combat flow, actions, and battle resolution
- **effect.py**: Status effects, buffs, debuffs, and custom effects

### Examples Module (`src/game/examples/`)
- **example.py**: Demonstrations of game systems and usage examples

## Migration Guide

### For Existing Code
If you have existing code that imports from the old structure:

**Old imports:**
```python
from src.game.player import Player
from src.game.enemy import Enemy
from src.game.combat import Combat
```

**New imports (recommended):**
```python
from src.game import Player, Enemy, Combat
```

### For New Development
Use the simplified imports for cleaner code:
```python
from src.game import Player, PlayerClass, Enemy, EnemyType, Combat, Item, Effect
```

## Testing the Restructure

The restructured code has been tested and verified to work correctly:

```bash
# Test the example combat
python -c "from src.game.examples.example import run_example_combat; run_example_combat()"

# Test simplified imports
python -c "from src.game import Player, Enemy, Combat, run_example_combat; run_example_combat()"
```

## Future Extensions

The new structure makes it easy to add new features:

1. **New Entity Types**: Add to `src/game/entities/`
2. **New Item Types**: Extend `src/game/items/item.py`
3. **New Game Systems**: Add to `src/game/systems/`
4. **New Examples**: Add to `src/game/examples/`

This structure provides a solid foundation for the Discord bot integration and future game features.
