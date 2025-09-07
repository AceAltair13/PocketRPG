"""
Enemy class for AI-controlled opponents in the RPG
Inherits from Entity and adds enemy-specific functionality
"""

from typing import Dict, List, Optional, Any, Tuple
from .entity import Entity, EntityType, StatType
from ..enums import EnemyType, EnemyBehavior


class Enemy(Entity):
    """
    Enemy class representing AI-controlled opponents.
    Extends Entity with enemy-specific features like AI behavior and loot drops.
    """
    
    def __init__(self, name: str, enemy_type: EnemyType, level: int = 1, 
                 behavior: EnemyBehavior = EnemyBehavior.BALANCED, emoji: str = "👹"):
        # Initialize as enemy entity type
        super().__init__(name, EntityType.ENEMY, level)
        
        self.enemy_type: EnemyType = enemy_type
        self.behavior: EnemyBehavior = behavior
        self.emoji: str = emoji  # Emoji for this enemy
        
        # Enemy-specific attributes
        self.experience_reward: int = 0
        self.gold_reward: int = 0
        self.loot_table: List[Dict[str, Any]] = []  # Items that can drop
        
        # AI state
        self.ai_cooldowns: Dict[str, int] = {}  # Cooldowns for special abilities
        self.last_action: Optional[str] = None
        self.aggression_level: int = 50  # 0-100, affects AI decisions
        
        # Initialize enemy-specific stats
        self._initialize_enemy_stats()
    
    def _initialize_stats(self) -> None:
        """Initialize base enemy stats"""
        # Base stats for all enemies
        self.stats.update({
            StatType.HEALTH: 80,
            StatType.MAX_HEALTH: 80,
            StatType.MANA: 40,
            StatType.MAX_MANA: 40,
            StatType.ATTACK: 8,
            StatType.DEFENSE: 4,
            StatType.SPEED: 8,
            StatType.EXPERIENCE: 0
        })
    
    def _initialize_enemy_stats(self) -> None:
        """Initialize enemy-specific stat bonuses based on type"""
        type_bonuses = {
            EnemyType.NORMAL: {
                StatType.HEALTH: 0,
                StatType.ATTACK: 0,
                StatType.DEFENSE: 0
            },
            EnemyType.ELITE: {
                StatType.HEALTH: 50,
                StatType.ATTACK: 5,
                StatType.DEFENSE: 3,
                StatType.SPEED: 2
            },
            EnemyType.MINIBOSS: {
                StatType.HEALTH: 100,
                StatType.ATTACK: 8,
                StatType.DEFENSE: 5,
                StatType.SPEED: 3
            },
            EnemyType.BOSS: {
                StatType.HEALTH: 200,
                StatType.ATTACK: 15,
                StatType.DEFENSE: 10,
                StatType.SPEED: 5
            }
        }
        
        # Apply type bonuses
        bonuses = type_bonuses.get(self.enemy_type, {})
        for stat, bonus in bonuses.items():
            current_value = self.get_stat(stat)
            self.set_stat(stat, current_value + bonus)
        
        # Set rewards based on type and level
        self._set_rewards()
    
    def _set_rewards(self) -> None:
        """Set experience and gold rewards based on enemy type and level"""
        base_exp = self.level * 10
        base_gold = self.level * 5
        
        type_multipliers = {
            EnemyType.NORMAL: (1.0, 1.0),
            EnemyType.ELITE: (1.5, 1.5),
            EnemyType.MINIBOSS: (2.0, 2.0),
            EnemyType.BOSS: (3.0, 3.0)
        }
        
        exp_mult, gold_mult = type_multipliers.get(self.enemy_type, (1.0, 1.0))
        self.experience_reward = int(base_exp * exp_mult)
        self.gold_reward = int(base_gold * gold_mult)
    
    def _apply_level_up_bonuses(self) -> None:
        """Apply level up bonuses for enemies"""
        # Enemies get smaller bonuses than players
        self.modify_stat(StatType.MAX_HEALTH, 8)
        self.modify_stat(StatType.MAX_MANA, 3)
        self.modify_stat(StatType.ATTACK, 1)
        self.modify_stat(StatType.DEFENSE, 1)
        self.modify_stat(StatType.SPEED, 1)
        
        # Update rewards
        self._set_rewards()
    
    def add_loot_item(self, item_name: str, drop_chance: float, quantity: int = 1) -> None:
        """Add an item to the enemy's loot table"""
        self.loot_table.append({
            'item_name': item_name,
            'drop_chance': drop_chance,
            'quantity': quantity
        })
    
    def generate_loot(self) -> List[Dict[str, Any]]:
        """Generate loot drops based on loot table"""
        import random
        dropped_items = []
        
        for loot_entry in self.loot_table:
            if random.random() < loot_entry['drop_chance']:
                dropped_items.append({
                    'item_name': loot_entry['item_name'],
                    'quantity': loot_entry['quantity']
                })
        
        return dropped_items
    
    def get_ai_action(self, target: Entity) -> str:
        """Get the AI's next action based on behavior and current state"""
        # Update cooldowns
        self._update_cooldowns()
        
        # Get available actions
        available_actions = self._get_available_actions()
        
        # Choose action based on behavior
        if self.behavior == EnemyBehavior.AGGRESSIVE:
            return self._aggressive_ai(target, available_actions)
        elif self.behavior == EnemyBehavior.DEFENSIVE:
            return self._defensive_ai(target, available_actions)
        elif self.behavior == EnemyBehavior.HEALER:
            return self._healer_ai(target, available_actions)
        elif self.behavior == EnemyBehavior.SPELLCASTER:
            return self._spellcaster_ai(target, available_actions)
        else:  # BALANCED
            return self._balanced_ai(target, available_actions)
    
    def _get_available_actions(self) -> List[str]:
        """Get list of available actions for the enemy"""
        actions = ["attack", "defend"]
        
        # Add special abilities based on enemy type
        if self.enemy_type in [EnemyType.ELITE, EnemyType.MINIBOSS, EnemyType.BOSS]:
            actions.append("special_attack")
        
        if self.enemy_type in [EnemyType.MINIBOSS, EnemyType.BOSS]:
            actions.append("area_attack")
        
        # Add healing if enemy has mana
        if self.get_stat(StatType.MANA) > 10:
            actions.append("heal")
        
        return actions
    
    def _aggressive_ai(self, target: Entity, actions: List[str]) -> str:
        """AI behavior for aggressive enemies"""
        # Always prefer attacking
        if "attack" in actions:
            return "attack"
        elif "special_attack" in actions and self._can_use_ability("special_attack"):
            return "special_attack"
        else:
            return "defend"
    
    def _defensive_ai(self, target: Entity, actions: List[str]) -> str:
        """AI behavior for defensive enemies"""
        # Defend if health is low
        if self.get_health_percentage() < 30:
            return "defend"
        elif "attack" in actions:
            return "attack"
        else:
            return "defend"
    
    def _healer_ai(self, target: Entity, actions: List[str]) -> str:
        """AI behavior for healer enemies"""
        # Heal if health is low
        if self.get_health_percentage() < 50 and "heal" in actions:
            return "heal"
        elif "attack" in actions:
            return "attack"
        else:
            return "defend"
    
    def _spellcaster_ai(self, target: Entity, actions: List[str]) -> str:
        """AI behavior for spellcaster enemies"""
        # Prefer magic attacks
        if "special_attack" in actions and self._can_use_ability("special_attack"):
            return "special_attack"
        elif "attack" in actions:
            return "attack"
        else:
            return "defend"
    
    def _balanced_ai(self, target: Entity, actions: List[str]) -> str:
        """AI behavior for balanced enemies"""
        import random
        
        # Heal if very low health
        if self.get_health_percentage() < 25 and "heal" in actions:
            return "heal"
        
        # Use special abilities occasionally
        if "special_attack" in actions and self._can_use_ability("special_attack") and random.random() < 0.3:
            return "special_attack"
        
        # Otherwise random choice between attack and defend
        return random.choice(["attack", "defend"])
    
    def _can_use_ability(self, ability_name: str) -> bool:
        """Check if an ability is off cooldown"""
        cooldown = self.ai_cooldowns.get(ability_name, 0)
        return cooldown <= 0
    
    def _update_cooldowns(self) -> None:
        """Update all ability cooldowns"""
        for ability in self.ai_cooldowns:
            if self.ai_cooldowns[ability] > 0:
                self.ai_cooldowns[ability] -= 1
    
    def set_ability_cooldown(self, ability_name: str, turns: int) -> None:
        """Set cooldown for an ability"""
        self.ai_cooldowns[ability_name] = turns
    
    def get_effective_attack(self) -> int:
        """Get attack power including any temporary modifiers"""
        return self.get_stat(StatType.ATTACK)
    
    def get_effective_defense(self) -> int:
        """Get defense including any temporary modifiers"""
        return self.get_stat(StatType.DEFENSE)
    
    def get_description(self) -> str:
        """Get description of the enemy"""
        type_descriptions = {
            EnemyType.NORMAL: "A common enemy",
            EnemyType.ELITE: "A stronger than average enemy",
            EnemyType.MINIBOSS: "A powerful enemy that guards important areas",
            EnemyType.BOSS: "An extremely powerful enemy that rules over others"
        }
        
        behavior_descriptions = {
            EnemyBehavior.AGGRESSIVE: "This enemy is very aggressive and will attack relentlessly.",
            EnemyBehavior.DEFENSIVE: "This enemy prefers to defend and wait for opportunities.",
            EnemyBehavior.BALANCED: "This enemy uses a balanced approach to combat.",
            EnemyBehavior.HEALER: "This enemy can heal itself and others.",
            EnemyBehavior.SPELLCASTER: "This enemy prefers to use magical attacks."
        }
        
        type_desc = type_descriptions.get(self.enemy_type, "An unknown enemy")
        behavior_desc = behavior_descriptions.get(self.behavior, "")
        
        return f"{type_desc}. {behavior_desc}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert enemy to dictionary for serialization"""
        base_dict = super().to_dict()
        base_dict.update({
            'enemy_type': self.enemy_type.value,
            'behavior': self.behavior.value,
            'experience_reward': self.experience_reward,
            'gold_reward': self.gold_reward,
            'loot_table': self.loot_table,
            'ai_cooldowns': self.ai_cooldowns,
            'aggression_level': self.aggression_level
        })
        return base_dict
    
    def __str__(self) -> str:
        """String representation of the enemy"""
        type_name = self.enemy_type.value.title()
        return f"{self.name} ({type_name}) (Lv.{self.level}) - HP: {self.get_stat(StatType.HEALTH)}/{self.get_stat(StatType.MAX_HEALTH)}"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"Enemy(name='{self.name}', type={self.enemy_type.value}, level={self.level}, behavior={self.behavior.value})"
