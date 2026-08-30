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
        # Ported from index.html
        self.censor_dict = {
            "gay": "gɑy",
            "ass": "ɑss",
            "hate": "hɑte",
            "ha te": "hɑte",
            "fuck": "fᴜck",
            "suck": "sᴜck",
            "porn": "pᴏrn",
            "cock": "cᴏck",
            "zionist": "ziᴏnist",
            "femboy": "fembᴏy",
            "fem boy": "fembᴏy",
            "kill": "kıll",
            "racist": "racıst",
            ":middle_finger:": "🖕",
        }

    def preserve_casing(self, original: str, replacement: str) -> str:
        """Ported logic from preserveCasing in index.html"""
        if original.isupper():
            return replacement.upper()
        if original[0].isupper():
            return replacement[0].upper() + replacement[1:].lower()
        return replacement.lower()

    def censor_text(self, text: str) -> tuple[str, int]:
        """Ported logic from censorText in index.html using Python regex"""
        count = 0

        for key, value in self.censor_dict.items():
            # 'gi' equivalent in Python is re.IGNORECASE
            pattern = re.compile(re.escape(key), re.IGNORECASE)

            def replace_match(match):
                nonlocal count
                count += 1
                return self.preserve_casing(match.group(0), value)

            text = pattern.sub(replace_match, text)

        return text, count

    @discord.slash_command(
        name='censor',
        description='Converts text into a version that will not get censored'
    )
    @option("text", description="The text you want to uncensor", required=True)
    async def censor(self, ctx: ApplicationContext, text: str):
        """Processes the text and returns it ephemerally to the user."""
        censored_output, modification_count = self.censor_text(text)

        # Using an Embed for a cleaner look similar to the website UI
        embed = discord.Embed(
            title="ゆ Utonish Uncensored",
            description=censored_output,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Words modified: {modification_count}")

        # ephemeral=True ensures only the user who ran the command sees the output
        await ctx.respond(embed=embed, ephemeral=True)
