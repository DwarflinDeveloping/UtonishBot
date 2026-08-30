import random
import textwrap
from typing import TYPE_CHECKING, List, Optional

import discord
from discord import ApplicationContext, option
from discord.ext import commands

from cogs.censor import CensorCommands

if TYPE_CHECKING:
    from bot import UtonishBot


class CopypastaCommands(discord.Cog):
    """Cog handling commands related to Utonish copypastas."""

    def __init__(self, bot: 'UtonishBot'):
        self.bot = bot
        self.censor_interface = CensorCommands(self.bot)

    async def get_copypasta_suggestions(self, ctx: discord.AutocompleteContext):
        """Autocomplete function to search copypastas by content[cite: 1]."""
        query = ctx.value.lower()
        copypastas = getattr(self.bot, 'copypastas', [])

        if not query:
            return [c['content'][:100] for c in copypastas[:25]]

        matches = [c['content'] for c in copypastas if query in c['content'].lower()]
        matches.sort(key=len)  # Prioritize shorter/closer matches[cite: 1]

        return [m[:100] for m in matches][:25]

    copypasta_group = discord.SlashCommandGroup(
        name='copypasta',
        description='Search and display community copypastas',
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

    @staticmethod
    async def send_long_content(ctx: ApplicationContext, content: str):
        chunks = textwrap.wrap(content, width=2000, replace_whitespace=False, drop_whitespace=False)
        await ctx.respond(chunks[0])
        for chunk in chunks[1:]:
            await ctx.followup.send(chunk)

    # Usage inside your slash command:
    @copypasta_group.command(name="random", description="Get a random copypasta")
    async def random_copypasta(self, ctx: ApplicationContext):
        copypastas = getattr(self.bot, 'copypastas', [])
        if not copypastas:
            await ctx.respond("No copypastas found...", ephemeral=True)
            return

        selected = random.choice(copypastas)
        content = self.censor_interface.censor_text(selected['content'].replace('@', '＠'))

        if len(content) > 2000:
            await self.send_long_content(ctx, content)
        else:
            await ctx.respond(content)

    @copypasta_group.command(name="search", description="Search for a specific copypasta")
    @option("query", description="Type content to search...", autocomplete=get_copypasta_suggestions)
    async def search(self, ctx: ApplicationContext, query: str):
        """Searches for a specific copypasta and displays it with metadata."""
        copypastas = getattr(self.bot, 'copypastas', [])

        found = next((c for c in copypastas if c['content'].startswith(query)), None)
        if not found:
            # Fallback search if exact prefix match fails
            found = next((c for c in copypastas if query.lower() in c['content'].lower()), None)

        if found:
            content = self.censor_interface.censor_text(found['content'].replace('@', '＠'))
            if len(content) > 2000:
                await self.send_long_content(ctx, content)
            else:
                await ctx.respond(content)
        else:
            await ctx.respond("Copypasta no longer exists.", ephemeral=True)


def setup(bot: 'UtonishBot'):
    bot.add_cog(CopypastaCommands(bot))