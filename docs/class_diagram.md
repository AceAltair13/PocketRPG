# PocketRPG - Low Level Design (LLD) Class Diagram

## Core Entity Hierarchy

```
Entity (Abstract Base Class)
├── Player
└── Enemy
```

## Entity Class
- **Purpose**: Base class for all living entities in the game
- **Key Attributes**:
  - `id`, `name`, `entity_type`, `level`
  - `stats` (Dict[StatType, int])
  - `status_effects` (List[Effect])
  - `is_alive`, `is_stunned`, `is_defending`
- **Key Methods**:
  - `take_damage()`, `heal()`, `add_experience()`
  - `add_status_effect()`, `process_status_effects()`
  - `get_stat()`, `set_stat()`, `modify_stat()`

## Player Class (extends Entity)
- **Purpose**: User-controlled characters
- **Additional Attributes**:
  - `player_class` (PlayerClass enum)
  - `user_id` (Discord user ID)
  - `gold`, `skill_points`
  - `inventory` (Inventory), `equipment` (Equipment)
- **Key Methods**:
  - `add_gold()`, `spend_gold()`
  - `get_effective_stats()` (includes equipment bonuses)
  - `learn_skill()`, `get_available_actions()`

## Enemy Class (extends Entity)
- **Purpose**: AI-controlled opponents
- **Additional Attributes**:
  - `enemy_type` (EnemyType enum)
  - `behavior` (EnemyBehavior enum)
  - `experience_reward`, `gold_reward`
  - `loot_table`, `ai_cooldowns`
- **Key Methods**:
  - `get_ai_action()`, `generate_loot()`
  - `add_loot_item()`

## Item System Hierarchy

```
Item (Abstract Base Class)
├── ConsumableItem
├── EquipmentItem
│   ├── WeaponItem
│   └── ArmorItem
└── QuestItem
```

## Item Classes
- **Item**: Base class with common properties (name, rarity, quality, value)
- **ConsumableItem**: Items that can be consumed (potions, food)
- **EquipmentItem**: Items that can be equipped for stat bonuses
- **WeaponItem**: Weapons with damage, crit chance, weapon type
- **ArmorItem**: Armor pieces with defense and resistances
- **QuestItem**: Story/quest specific items

## Effect System

```
Effect (Abstract Base Class)
├── StatModifierEffect
├── DamageOverTimeEffect
├── HealOverTimeEffect
├── StatusEffect
└── CustomEffect
```

## Effect Classes
- **Effect**: Base class for all status effects
- **StatModifierEffect**: Modifies entity stats (buffs/debuffs)
- **DamageOverTimeEffect**: Deals damage over time
- **HealOverTimeEffect**: Heals over time
- **StatusEffect**: Changes entity behavior/status
- **CustomEffect**: Effects with custom behavior

## Supporting Systems

### Inventory System
- **Inventory**: Manages item storage, stacking, capacity
- **Key Methods**: `add_item()`, `remove_item()`, `use_item()`, `sort_items()`

### Equipment System
- **Equipment**: Manages equipped items and stat bonuses
- **Key Methods**: `equip_item()`, `unequip_item()`, `get_total_bonuses()`

### Combat System
- **Combat**: Handles turn-based combat flow
- **CombatTurn**: Represents a single turn in combat
- **Key Methods**: `start_combat()`, `_process_turn()`, `_execute_action()`

## Enums and Constants

### EntityType
- PLAYER, ENEMY, NPC, BOSS

### StatType
- HEALTH, MAX_HEALTH, MANA, MAX_MANA
- ATTACK, DEFENSE, SPEED, LEVEL, EXPERIENCE

### PlayerClass
- WARRIOR, MAGE, ROGUE, CLERIC

### EnemyType
- NORMAL, ELITE, BOSS, MINIBOSS

### EnemyBehavior
- AGGRESSIVE, DEFENSIVE, BALANCED, HEALER, SPELLCASTER

### ItemType
- CONSUMABLE, WEAPON, ARMOR, ACCESSORY, QUEST, MATERIAL, MISC

### ItemRarity
- COMMON, UNCOMMON, RARE, EPIC, LEGENDARY

### EffectType
- BUFF, DEBUFF, DOT, HOT, STATUS

### CombatAction
- ATTACK, DEFEND, USE_ITEM, FLEE, SPECIAL_ABILITY

## Key Design Patterns Used

1. **Inheritance**: Entity base class with Player/Enemy specialization
2. **Composition**: Player contains Inventory and Equipment
3. **Strategy Pattern**: Different AI behaviors for enemies
4. **Factory Pattern**: CommonItems and CommonEffects for creating standard items/effects
5. **Observer Pattern**: Status effects that modify entity behavior
6. **Command Pattern**: Combat actions as objects

## Data Flow

1. **Combat Flow**:
   - Combat → CombatTurn → Entity Action → Effect Application
   - Status effects processed each turn
   - Turn order based on speed stat

2. **Item Flow**:
   - Items created → Added to Inventory → Equipped → Stat bonuses applied
   - Consumables used → Effects applied → Item consumed

3. **Effect Flow**:
   - Effect created → Applied to Entity → Processed each turn → Removed when expired

## Extensibility Points

1. **New Entity Types**: Extend Entity class
2. **New Item Types**: Extend Item class hierarchy
3. **New Effects**: Extend Effect class or use CustomEffect
4. **New Combat Actions**: Add to CombatAction enum and implement in Combat class
5. **New AI Behaviors**: Add to EnemyBehavior enum and implement in Enemy class

## Serialization Support

All major classes implement `to_dict()` and `from_dict()` methods for:
- Saving/loading game state
- Discord bot integration
- Database storage
- Network communication
