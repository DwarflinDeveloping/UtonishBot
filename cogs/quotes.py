import random
from typing import TYPE_CHECKING

import discord
from discord import ApplicationContext

if TYPE_CHECKING:
    from bot import UtonishBot


class QuoteCommands(discord.Cog):
    def __init__(self, bot: 'UtonishBot'):
        self.bot = bot

    @discord.slash_command(name='quote')
    async def random(self, ctx: ApplicationContext):
        if not self.bot.quotes:
            await ctx.respond('No quotes found...', ephemeral=True)
            return

        quote = random.choice(self.bot.quotes)
        await ctx.respond(quote)
