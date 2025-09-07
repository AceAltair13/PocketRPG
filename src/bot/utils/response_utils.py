"""
Shared response utilities to reduce code duplication
"""

import discord
from typing import Optional
from .embed_utils import EmbedUtils


class ResponseUtils:
    """Utility class for common Discord response patterns"""
    
    @staticmethod
    async def send_error(interaction: discord.Interaction, message: str, title: str = "Error", ephemeral: bool = True):
        """Send a standardized error response"""
        embed = EmbedUtils.create_error_embed(message, title)
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
    
    @staticmethod
    async def send_success(interaction: discord.Interaction, message: str, title: str = "Success", ephemeral: bool = False):
        """Send a standardized success response"""
        embed = EmbedUtils.create_success_embed(message, title)
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
    
    @staticmethod
    async def send_info(interaction: discord.Interaction, message: str, title: str = "Info", ephemeral: bool = False):
        """Send a standardized info response"""
        embed = EmbedUtils.create_info_embed(message, title)
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
    
    @staticmethod
    async def send_embed(interaction: discord.Interaction, embed: discord.Embed, ephemeral: bool = False):
        """Send an embed response"""
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
    
    @staticmethod
    async def send_embed_with_view(interaction: discord.Interaction, embed: discord.Embed, view: discord.ui.View, ephemeral: bool = False):
        """Send an embed with a view"""
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, view=view, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(embed=embed, view=view, ephemeral=ephemeral)
