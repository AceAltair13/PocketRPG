"""
Shared player validation utilities to reduce code duplication
"""

import discord
from typing import Optional, Tuple
from ...game.entities.player import Player


class PlayerUtils:
    """Utility class for common player validation patterns"""
    
    @staticmethod
    def get_player_or_error(bot, user_id: int) -> Tuple[Optional[Player], Optional[str]]:
        """
        Get player or return error message.
        Returns (player, error_message) tuple.
        If player exists, error_message is None.
        If player doesn't exist, player is None and error_message is the error.
        """
        player = bot.get_player(user_id)
        if not player:
            return None, "You don't have a character yet! Use `/create_character` to create one."
        return player, None
    
    @staticmethod
    def check_player_exists(bot, user_id: int) -> Tuple[Optional[Player], Optional[str]]:
        """
        Check if player exists or return error message.
        Returns (player, error_message) tuple.
        If player exists, error_message is None.
        If player doesn't exist, player is None and error_message is the error.
        """
        player = bot.get_player(user_id)
        if not player:
            return None, "You don't have a character yet! Use `/create_character` to create one."
        return player, None
    
    @staticmethod
    def check_player_not_exists(bot, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Check if player doesn't exist (for character creation).
        Returns (can_create, error_message) tuple.
        If can_create is True, error_message is None.
        If can_create is False, error_message is the error.
        """
        player = bot.get_player(user_id)
        if player:
            return False, "You already have a character! Use `/character` to view your stats."
        return True, None
    
    @staticmethod
    def validate_character_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate character name.
        Returns (is_valid, error_message) tuple.
        If is_valid is True, error_message is None.
        If is_valid is False, error_message is the error.
        """
        if not name or not name.strip():
            return False, "Character name cannot be empty."
        
        name = name.strip()
        
        if len(name) < 2:
            return False, "Character name must be at least 2 characters long."
        
        if len(name) > 20:
            return False, "Character name must be 20 characters or less."
        
        if not name.replace(' ', '').isalnum():
            return False, "Character name can only contain letters, numbers, and spaces."
        
        return True, None
