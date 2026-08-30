import os
import re
from typing import TYPE_CHECKING

import discord
from discord import ApplicationContext, Forbidden, option

if TYPE_CHECKING:
    from bot import UtonishBot


class CensorCommands(discord.Cog):
    def __init__(self, bot: 'UtonishBot'):
        self.bot = bot
        # Single-character replacements for str.maketrans
        self.homoglyph_map = {
            'a': 'а',
            'c': 'с',
            'e': 'е',
            'i': 'і',
            'j': 'ј',
            'o': 'о',
            'p': 'р',
            's': 'ѕ',
            'u': 'ᴜ',
            'x': 'х',
            'y': 'у',
            'A': 'А',
            'B': 'В',
            'C': 'С',
            'E': 'Е',
            'H': 'Н',
            'I': 'І',
            'J': 'Ј',
            'K': 'К',
            'M': 'М',
            'O': 'О',
            'P': 'Р',
            'S': 'Ѕ',
            'T': 'Т',
            'X': 'Х',
            'Y': 'Ү',
        }
        # Pre-build translation table for performance
        self.trans_table = str.maketrans(self.homoglyph_map)

        # Multi-character replacements
        self.string_map = {
            ":middle_finger:": "🖕",
        }

    def replace_homoglyphs(self, text: str) -> str:
        # First, apply single-character translation
        text = text.translate(self.trans_table)

        # Next, handle multi-character substring replacements
        for key, value in self.string_map.items():
            text = text.replace(key, value)

        return text

    def censor_text(self, text: str) -> str:
        text = self.replace_homoglyphs(text)
        return text

    @discord.slash_command(
        name='censor',
        description='Converts text into a version that will not get censored',
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install
        },
        contexts={
            discord.InteractionContextType.guild,
            discord.InteractionContextType.bot_dm,
            discord.InteractionContextType.private_channel
        }
    )
    @option("text", description="The text you want to uncensor", required=True)
    async def censor(self, ctx: ApplicationContext, text: str):
        """Processes the text and returns it ephemerally to the user."""
        censored_output = self.censor_text(text)

        embed = discord.Embed(
            title="ゆ Utonish Uncensored",
            description=censored_output,
            color=discord.Color.blue()
        )
        embed = None
        # embed.set_footer(text=f"Words modified: {modification_count}")

        await ctx.respond(censored_output, embed=embed, ephemeral=True)