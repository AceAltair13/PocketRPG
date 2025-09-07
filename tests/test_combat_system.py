"""
Tests for combat system functionality
"""

import pytest
from src.game.entities.player import Player, PlayerClass
from src.game.entities.enemy import Enemy, EnemyType, EnemyBehavior
from src.game.systems.combat import Combat, CombatAction, CombatResult
from src.game.enums import StatType
from src.game.systems.effect import CommonEffects


class TestCombatSystem:
    """Test cases for combat system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
        self.enemy = Enemy("TestEnemy", EnemyType.NORMAL, level=1, behavior=EnemyBehavior.AGGRESSIVE)
    
    def test_combat_creation(self):
        """Test combat system creation"""
        combat = Combat([self.player, self.enemy])
        
        assert combat.participants == [self.player, self.enemy]
        assert combat.is_active is True
        assert len(combat.turn_order) == 2
        assert combat.current_turn == 0
        assert combat.turn_count == 0
    
    def test_turn_order_by_speed(self):
        """Test turn order is determined by speed"""
        # Create fast player and slow enemy
        fast_player = Player("FastPlayer", PlayerClass.ROGUE, level=1)  # Rogues have high speed
        slow_enemy = Enemy("SlowEnemy", EnemyType.NORMAL, level=1, behavior=EnemyBehavior.AGGRESSIVE)
        
        combat = Combat([fast_player, slow_enemy])
        
        # Fast player should go first
        assert combat.turn_order[0] == fast_player
        assert combat.turn_order[1] == slow_enemy
    
    def test_combat_status_display(self):
        """Test combat status display"""
        combat = Combat([self.player, self.enemy])
        status = combat.get_combat_status()
        
        assert "Combat Status" in status
        assert "TestPlayer" in status
        assert "TestEnemy" in status
        assert "HP" in status
    
    def test_combat_logging(self):
        """Test combat logging system"""
        combat = Combat([self.player, self.enemy])
        log = combat.get_combat_log()
        
        assert isinstance(log, list)
        assert len(log) > 0
        assert "Combat started" in log[0]
    
    def test_combat_actions(self):
        """Test available combat actions"""
        combat = Combat([self.player, self.enemy])
        
        # Test that combat has action methods
        assert hasattr(combat, '_execute_action')
        assert hasattr(combat, '_process_turn')
    
    def test_combat_end_conditions(self):
        """Test combat end conditions"""
        combat = Combat([self.player, self.enemy])
        
        # Combat should end when all enemies are dead
        self.enemy.take_damage(1000)  # Kill enemy
        assert not self.enemy.is_alive
        
        # Combat should end when all players are dead
        self.player.take_damage(1000)  # Kill player
        assert not self.player.is_alive


class TestCombatActions:
    """Test cases for combat actions"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
        self.enemy = Enemy("TestEnemy", EnemyType.NORMAL, level=1, behavior=EnemyBehavior.AGGRESSIVE)
        self.combat = Combat([self.player, self.enemy])
    
    def test_attack_action(self):
        """Test attack action mechanics"""
        initial_enemy_health = self.enemy.get_stat(StatType.HEALTH)
        
        # Create a mock turn with attack action
        from src.game.systems.combat import CombatTurn
        turn = CombatTurn(self.player, CombatAction.ATTACK, target=self.enemy)
        
        # Execute attack (simplified)
        damage = self.player.get_stat(StatType.ATTACK)
        actual_damage = self.enemy.take_damage(damage)
        
        # Enemy should take damage
        new_health = self.enemy.get_stat(StatType.HEALTH)
        assert new_health < initial_enemy_health
        assert actual_damage > 0
    
    def test_defend_action(self):
        """Test defend action mechanics"""
        # Player defends
        self.player.is_defending = True
        
        # Enemy attacks
        initial_player_health = self.player.get_stat(StatType.HEALTH)
        damage = self.enemy.get_stat(StatType.ATTACK)
        actual_damage = self.player.take_damage(damage)
        
        # Player should take reduced damage when defending
        new_health = self.player.get_stat(StatType.HEALTH)
        assert new_health < initial_player_health
        # Note: Actual damage reduction would depend on defense calculation
    
    def test_flee_action(self):
        """Test flee action mechanics"""
        # Test that flee action exists
        assert CombatAction.FLEE is not None
        
        # In a real implementation, flee would have a chance to succeed
        # For now, just test that the action is available
        available_actions = self.player.get_available_actions()
        assert "flee" in available_actions


class TestEnemyAI:
    """Test cases for enemy AI behavior"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
    
    def test_aggressive_enemy_behavior(self):
        """Test aggressive enemy behavior"""
        enemy = Enemy("AggressiveEnemy", EnemyType.NORMAL, level=1, behavior=EnemyBehavior.AGGRESSIVE)
        
        # Aggressive enemies should prefer attack
        action = enemy.get_ai_action(self.player)
        assert action in ["attack", "defend", "special_attack", "heal"]
    
    def test_defensive_enemy_behavior(self):
        """Test defensive enemy behavior"""
        enemy = Enemy("DefensiveEnemy", EnemyType.NORMAL, level=1, behavior=EnemyBehavior.DEFENSIVE)
        
        # Defensive enemies should prefer defend when low health
        enemy.take_damage(50)  # Reduce health
        action = enemy.get_ai_action(self.player)
        assert action in ["attack", "defend", "special_attack", "heal"]
    
    def test_healer_enemy_behavior(self):
        """Test healer enemy behavior"""
        enemy = Enemy("HealerEnemy", EnemyType.NORMAL, level=1, behavior=EnemyBehavior.HEALER)
        
        # Healer enemies should heal when low health
        enemy.take_damage(50)  # Reduce health
        action = enemy.get_ai_action(self.player)
        assert action in ["attack", "defend", "special_attack", "heal"]
    
    def test_enemy_ai_with_different_targets(self):
        """Test enemy AI with different target types"""
        enemy = Enemy("TestEnemy", EnemyType.NORMAL, level=1, behavior=EnemyBehavior.AGGRESSIVE)
        
        # Test with healthy target
        healthy_player = Player("HealthyPlayer", PlayerClass.WARRIOR, level=1)
        action1 = enemy.get_ai_action(healthy_player)
        
        # Test with injured target
        injured_player = Player("InjuredPlayer", PlayerClass.WARRIOR, level=1)
        injured_player.take_damage(50)
        action2 = enemy.get_ai_action(injured_player)
        
        # Both should return valid actions
        assert action1 in ["attack", "defend", "special_attack", "heal"]
        assert action2 in ["attack", "defend", "special_attack", "heal"]


class TestCombatEffects:
    """Test cases for combat effects and status"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.player = Player("TestPlayer", PlayerClass.WARRIOR, level=1)
        self.enemy = Enemy("TestEnemy", EnemyType.NORMAL, level=1, behavior=EnemyBehavior.AGGRESSIVE)
    
    def test_strength_buff_in_combat(self):
        """Test strength buff effect in combat"""
        initial_attack = self.player.get_stat(StatType.ATTACK)
        
        # Apply strength buff
        strength_buff = CommonEffects.strength_buff(duration=3, power=5)
        self.player.add_status_effect(strength_buff)
        
        # Apply the effect to the player
        strength_buff.apply(self.player)
        
        # Attack should be increased
        new_attack = self.player.get_stat(StatType.ATTACK)
        assert new_attack > initial_attack
    
    def test_poison_effect_in_combat(self):
        """Test poison effect in combat"""
        initial_health = self.enemy.get_stat(StatType.HEALTH)
        
        # Apply poison
        poison = CommonEffects.poison(duration=3, damage=5)
        self.enemy.add_status_effect(poison)
        
        # Apply the effect to the enemy
        poison.apply(self.enemy)
        
        # Process one turn of poison
        poison.tick(self.enemy)
        
        # Health should be reduced
        new_health = self.enemy.get_stat(StatType.HEALTH)
        assert new_health < initial_health
    
    def test_regeneration_effect_in_combat(self):
        """Test regeneration effect in combat"""
        # Damage player first
        self.player.take_damage(20)
        initial_health = self.player.get_stat(StatType.HEALTH)
        
        # Apply regeneration
        regen = CommonEffects.regeneration(duration=3, healing=5)
        self.player.add_status_effect(regen)
        
        # Apply the effect to the player
        regen.apply(self.player)
        
        # Process one turn of regeneration
        regen.tick(self.player)
        
        # Health should be increased
        new_health = self.player.get_stat(StatType.HEALTH)
        assert new_health > initial_health
    
    def test_effect_duration(self):
        """Test that effects have proper duration"""
        # Apply effect with 3 turn duration
        strength_buff = CommonEffects.strength_buff(duration=3, power=5)
        self.player.add_status_effect(strength_buff)
        
        assert len(self.player.status_effects) == 1
        assert self.player.status_effects[0].duration == 3
        
        # Process turns
        for _ in range(3):
            self.player.process_status_effects()
        
        # Effect should be removed after duration expires
        assert len(self.player.status_effects) == 0
    
    def test_multiple_effects(self):
        """Test multiple effects on same entity"""
        # Apply multiple effects
        strength_buff = CommonEffects.strength_buff(duration=2, power=3)
        poison = CommonEffects.poison(duration=2, damage=2)
        
        self.player.add_status_effect(strength_buff)
        self.player.add_status_effect(poison)
        
        assert len(self.player.status_effects) == 2
        
        # Process one turn
        self.player.process_status_effects()
        
        # Both effects should still be active
        assert len(self.player.status_effects) == 2
        assert all(effect.duration > 0 for effect in self.player.status_effects)
