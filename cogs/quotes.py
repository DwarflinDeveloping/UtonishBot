import random
from typing import TYPE_CHECKING

import discord
from discord import ApplicationContext

from quotes import QuoteGenerator

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

    @discord.slash_command(name='gen_quotes')
    async def generate(self, ctx: ApplicationContext):
        await ctx.defer()
        generator = QuoteGenerator()
        generator.save()
        self.bot.quotes = generator.quotes

        await ctx.respond(f'Fetched {len(self.bot.quotes)} Benyi quotes!',
                          file=discord.File(generator.save_path, 'benyi_quotes.txt'))
