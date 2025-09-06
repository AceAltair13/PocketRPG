"""
Tests for Discord bot functionality
"""

import pytest
from unittest.mock import Mock, AsyncMock
from src.bot.bot import PocketRPG, create_bot


class TestPocketRPG:
    """Test cases for PocketRPG bot class"""
    
    def test_bot_creation(self):
        """Test bot creation"""
        bot = create_bot()
        
        assert isinstance(bot, PocketRPG)
        assert bot.command_prefix == "!"
        assert bot.region_manager is not None
        assert bot.active_players == {}
        assert bot.active_combats == {}
    
    def test_player_management(self):
        """Test player management methods"""
        bot = create_bot()
        
        # Mock player
        mock_player = Mock()
        mock_player.name = "TestPlayer"
        
        user_id = 12345
        
        # Test setting player
        bot.set_player(user_id, mock_player)
        assert bot.get_player(user_id) == mock_player
        
        # Test removing player
        bot.remove_player(user_id)
        assert bot.get_player(user_id) is None
    
    def test_combat_management(self):
        """Test combat management methods"""
        bot = create_bot()
        
        # Mock combat
        mock_combat = Mock()
        channel_id = 67890
        
        # Test setting combat
        bot.set_combat(channel_id, mock_combat)
        assert bot.get_combat(channel_id) == mock_combat
        
        # Test removing combat
        bot.remove_combat(channel_id)
        assert bot.get_combat(channel_id) is None
    
    def test_bot_intents(self):
        """Test bot intents configuration"""
        bot = create_bot()
        
        # Check that required intents are enabled
        assert bot.intents.message_content is True
        assert bot.intents.members is True


class TestBotIntegration:
    """Test bot integration with game systems"""
    
    def test_region_manager_integration(self):
        """Test that bot has region manager"""
        bot = create_bot()
        
        assert bot.region_manager is not None
        assert hasattr(bot.region_manager, 'get_available_regions')
        assert hasattr(bot.region_manager, 'set_current_region')
    
    def test_data_loader_integration(self):
        """Test that bot can access data loader"""
        bot = create_bot()
        
        # Bot should be able to access data loader through region manager
        data_loader = bot.region_manager.data_loader
        assert data_loader is not None
        assert hasattr(data_loader, 'list_regions')
        assert hasattr(data_loader, 'load_region')
