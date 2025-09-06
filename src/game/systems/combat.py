"""
Combat system for turn-based RPG battles
Handles combat flow, actions, and battle resolution
"""

from typing import List, Dict, Any, Optional, Tuple
import random
from ..entities.entity import Entity, StatType
from ..entities.player import Player
from ..entities.enemy import Enemy
from ..enums import CombatAction, CombatResult


class CombatTurn:
    """Represents a single turn in combat"""
    
    def __init__(self, entity: Entity, action: CombatAction, target: Optional[Entity] = None, 
                 item_name: Optional[str] = None):
        self.entity: Entity = entity
        self.action: CombatAction = action
        self.target: Optional[Entity] = target
        self.item_name: Optional[str] = item_name
        self.damage_dealt: int = 0
        self.healing_done: int = 0
        self.effects_applied: List[str] = []
        self.success: bool = False


class Combat:
    """
    Combat system for handling turn-based battles.
    Manages combat flow, turn order, and battle resolution.
    """
    
    def __init__(self, participants: List[Entity]):
        self.participants: List[Entity] = participants
        self.turn_order: List[Entity] = []
        self.current_turn: int = 0
        self.turn_count: int = 0
        self.combat_log: List[str] = []
        self.is_active: bool = False
        
        # Combat state
        self.players: List[Player] = [p for p in participants if isinstance(p, Player)]
        self.enemies: List[Enemy] = [e for e in participants if isinstance(e, Enemy)]
        
        # Initialize combat
        self._initialize_combat()
    
    def _initialize_combat(self) -> None:
        """Initialize combat state and turn order"""
        # Reset combat state for all participants
        for participant in self.participants:
            participant.reset_combat_state()
        
        # Determine turn order based on speed
        self.turn_order = sorted(self.participants, key=lambda e: e.get_stat(StatType.SPEED), reverse=True)
        
        # Filter out dead participants
        self.turn_order = [p for p in self.turn_order if p.is_alive]
        
        self.current_turn = 0
        self.turn_count = 0
        self.combat_log.clear()
        self.is_active = True
        
        self._log(f"Combat started! Turn order: {[p.name for p in self.turn_order]}")
    
    def start_combat(self) -> CombatResult:
        """Start the combat and return the result"""
        self.is_active = True
        
        while self.is_active:
            result = self._process_turn()
            if result != CombatResult.ONGOING:
                return result
        
        return CombatResult.ONGOING
    
    def _process_turn(self) -> CombatResult:
        """Process a single turn and return combat result"""
        if not self.turn_order:
            return CombatResult.ONGOING
        
        # Get current entity
        current_entity = self.turn_order[self.current_turn]
        
        if not current_entity.is_alive:
            self._next_turn()
            return CombatResult.ONGOING
        
        # Process status effects
        current_entity.process_status_effects()
        
        # Get action from entity
        if isinstance(current_entity, Player):
            # For players, we'd get input from Discord commands
            # For now, use a simple AI
            action = self._get_player_action(current_entity)
        else:
            # Enemy AI
            action = self._get_enemy_action(current_entity)
        
        # Execute action
        turn_result = self._execute_action(action)
        
        # Log the turn
        self._log_turn(turn_result)
        
        # Check for combat end conditions
        result = self._check_combat_end()
        if result != CombatResult.ONGOING:
            return result
        
        # Move to next turn
        self._next_turn()
        
        return CombatResult.ONGOING
    
    def _get_player_action(self, player: Player) -> CombatTurn:
        """Get action for a player (simplified AI for now)"""
        # Simple AI: attack if enemy is alive, otherwise defend
        target = self._get_best_target(player)
        
        if target and target.is_alive:
            return CombatTurn(player, CombatAction.ATTACK, target)
        else:
            return CombatTurn(player, CombatAction.DEFEND)
    
    def _get_enemy_action(self, enemy: Enemy) -> CombatTurn:
        """Get action for an enemy using their AI"""
        # Use enemy's AI to determine action
        target = self._get_best_target(enemy)
        action_name = enemy.get_ai_action(target) if target else "defend"
        
        # Convert action name to CombatAction
        action_mapping = {
            "attack": CombatAction.ATTACK,
            "defend": CombatAction.DEFEND,
            "special_attack": CombatAction.SPECIAL_ABILITY,
            "heal": CombatAction.SPECIAL_ABILITY
        }
        
        action = action_mapping.get(action_name, CombatAction.ATTACK)
        return CombatTurn(enemy, action, target)
    
    def _get_best_target(self, attacker: Entity) -> Optional[Entity]:
        """Get the best target for an attacker"""
        if isinstance(attacker, Player):
            # Players target enemies
            alive_enemies = [e for e in self.enemies if e.is_alive]
            if alive_enemies:
                # Target the weakest enemy
                return min(alive_enemies, key=lambda e: e.get_stat(StatType.HEALTH))
        else:
            # Enemies target players
            alive_players = [p for p in self.players if p.is_alive]
            if alive_players:
                # Target the weakest player
                return min(alive_players, key=lambda p: p.get_stat(StatType.HEALTH))
        
        return None
    
    def _execute_action(self, turn: CombatTurn) -> CombatTurn:
        """Execute a combat action and return the result"""
        entity = turn.entity
        action = turn.action
        target = turn.target
        
        if action == CombatAction.ATTACK:
            if target and target.is_alive:
                damage = self._calculate_damage(entity, target)
                actual_damage = target.take_damage(damage)
                turn.damage_dealt = actual_damage
                turn.success = True
                
                # Check for critical hit
                if self._is_critical_hit(entity):
                    turn.damage_dealt = int(turn.damage_dealt * 1.5)
                    turn.effects_applied.append("critical_hit")
        
        elif action == CombatAction.DEFEND:
            entity.is_defending = True
            turn.success = True
            turn.effects_applied.append("defending")
        
        elif action == CombatAction.USE_ITEM:
            if hasattr(entity, 'inventory') and turn.item_name:
                success = entity.inventory.use_item(turn.item_name, entity)
                turn.success = success
                if success:
                    turn.effects_applied.append(f"used_{turn.item_name}")
        
        elif action == CombatAction.SPECIAL_ABILITY:
            # Handle special abilities
            if isinstance(entity, Enemy):
                turn = self._execute_enemy_special_ability(turn)
            else:
                turn = self._execute_player_special_ability(turn)
        
        elif action == CombatAction.FLEE:
            if isinstance(entity, Player):
                turn.success = True
                turn.effects_applied.append("fled")
        
        return turn
    
    def _execute_enemy_special_ability(self, turn: CombatTurn) -> CombatTurn:
        """Execute enemy special ability"""
        enemy = turn.entity
        target = turn.target
        
        if enemy.enemy_type.value in ["elite", "miniboss", "boss"]:
            # Special attack
            if target and target.is_alive:
                damage = self._calculate_damage(enemy, target) * 1.5
                actual_damage = target.take_damage(int(damage))
                turn.damage_dealt = actual_damage
                turn.success = True
                turn.effects_applied.append("special_attack")
        
        return turn
    
    def _execute_player_special_ability(self, turn: CombatTurn) -> CombatTurn:
        """Execute player special ability"""
        player = turn.entity
        target = turn.target
        
        # Class-specific abilities
        if player.player_class.value == "warrior":
            # Berserker rage
            if target and target.is_alive:
                damage = self._calculate_damage(player, target) * 1.3
                actual_damage = target.take_damage(int(damage))
                turn.damage_dealt = actual_damage
                turn.success = True
                turn.effects_applied.append("berserker_rage")
        
        elif player.player_class.value == "mage":
            # Fireball
            if target and target.is_alive:
                damage = self._calculate_damage(player, target) * 1.4
                actual_damage = target.take_damage(int(damage))
                turn.damage_dealt = actual_damage
                turn.success = True
                turn.effects_applied.append("fireball")
        
        elif player.player_class.value == "cleric":
            # Heal
            if target and target.is_alive:
                healing = 30
                actual_healing = target.heal(healing)
                turn.healing_done = actual_healing
                turn.success = True
                turn.effects_applied.append("heal")
        
        elif player.player_class.value == "rogue":
            # Sneak attack
            if target and target.is_alive:
                damage = self._calculate_damage(player, target) * 1.6
                actual_damage = target.take_damage(int(damage))
                turn.damage_dealt = actual_damage
                turn.success = True
                turn.effects_applied.append("sneak_attack")
        
        return turn
    
    def _calculate_damage(self, attacker: Entity, target: Entity) -> int:
        """Calculate damage dealt by attacker to target"""
        base_damage = attacker.get_stat(StatType.ATTACK)
        
        # Apply defense
        defense = target.get_stat(StatType.DEFENSE)
        
        # If target is defending, reduce damage
        if target.is_defending:
            defense *= 2
        
        # Calculate final damage
        damage = max(1, base_damage - defense)
        
        # Add some randomness
        damage = int(damage * random.uniform(0.8, 1.2))
        
        return damage
    
    def _is_critical_hit(self, attacker: Entity) -> bool:
        """Check if attack is a critical hit"""
        # Base crit chance is 5%
        crit_chance = 0.05
        
        # Increase crit chance based on speed
        speed = attacker.get_stat(StatType.SPEED)
        crit_chance += speed * 0.001
        
        return random.random() < crit_chance
    
    def _check_combat_end(self) -> CombatResult:
        """Check if combat should end"""
        # Check if all players are dead
        alive_players = [p for p in self.players if p.is_alive]
        if not alive_players:
            return CombatResult.DEFEAT
        
        # Check if all enemies are dead
        alive_enemies = [e for e in self.enemies if e.is_alive]
        if not alive_enemies:
            return CombatResult.VICTORY
        
        # Check if any player fled
        for player in self.players:
            if "fled" in [effect for turn in self.combat_log if hasattr(turn, 'effects_applied')]:
                return CombatResult.FLEE
        
        return CombatResult.ONGOING
    
    def _next_turn(self) -> None:
        """Move to the next turn"""
        self.current_turn = (self.current_turn + 1) % len(self.turn_order)
        
        # If we've completed a full round, increment turn count
        if self.current_turn == 0:
            self.turn_count += 1
        
        # Remove dead entities from turn order
        self.turn_order = [p for p in self.turn_order if p.is_alive]
        
        # Reset turn order if empty
        if not self.turn_order:
            self.turn_order = [p for p in self.participants if p.is_alive]
            self.current_turn = 0
    
    def _log_turn(self, turn: CombatTurn) -> None:
        """Log the results of a turn"""
        entity = turn.entity
        action = turn.action
        
        if action == CombatAction.ATTACK and turn.target:
            if turn.damage_dealt > 0:
                self._log(f"{entity.name} attacks {turn.target.name} for {turn.damage_dealt} damage!")
                if "critical_hit" in turn.effects_applied:
                    self._log("Critical hit!")
            else:
                self._log(f"{entity.name} attacks {turn.target.name} but deals no damage!")
        
        elif action == CombatAction.DEFEND:
            self._log(f"{entity.name} defends!")
        
        elif action == CombatAction.USE_ITEM:
            if turn.success:
                self._log(f"{entity.name} uses {turn.item_name}!")
            else:
                self._log(f"{entity.name} tries to use {turn.item_name} but fails!")
        
        elif action == CombatAction.SPECIAL_ABILITY:
            if turn.damage_dealt > 0:
                self._log(f"{entity.name} uses special ability and deals {turn.damage_dealt} damage!")
            elif turn.healing_done > 0:
                self._log(f"{entity.name} uses special ability and heals for {turn.healing_done} HP!")
        
        elif action == CombatAction.FLEE:
            self._log(f"{entity.name} flees from combat!")
    
    def _log(self, message: str) -> None:
        """Add a message to the combat log"""
        self.combat_log.append(f"Turn {self.turn_count + 1}: {message}")
    
    def get_combat_status(self) -> str:
        """Get current combat status"""
        status = f"Combat Status (Turn {self.turn_count + 1}):\n"
        
        # Show player status
        status += "Players:\n"
        for player in self.players:
            if player.is_alive:
                health_pct = player.get_health_percentage()
                status += f"  {player.name}: {player.get_stat(StatType.HEALTH)}/{player.get_stat(StatType.MAX_HEALTH)} HP ({health_pct:.1f}%)\n"
            else:
                status += f"  {player.name}: DEAD\n"
        
        # Show enemy status
        status += "Enemies:\n"
        for enemy in self.enemies:
            if enemy.is_alive:
                health_pct = enemy.get_health_percentage()
                status += f"  {enemy.name}: {enemy.get_stat(StatType.HEALTH)}/{enemy.get_stat(StatType.MAX_HEALTH)} HP ({health_pct:.1f}%)\n"
            else:
                status += f"  {enemy.name}: DEAD\n"
        
        return status
    
    def get_combat_log(self) -> List[str]:
        """Get the combat log"""
        return self.combat_log.copy()
    
    def end_combat(self) -> None:
        """End the combat"""
        self.is_active = False
        
        # Reset combat state for all participants
        for participant in self.participants:
            participant.reset_combat_state()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert combat to dictionary for serialization"""
        return {
            'participants': [p.to_dict() for p in self.participants],
            'turn_order': [p.name for p in self.turn_order],
            'current_turn': self.current_turn,
            'turn_count': self.turn_count,
            'combat_log': self.combat_log,
            'is_active': self.is_active
        }
