from typing import TYPE_CHECKING

import discord
from discord import ApplicationContext

if TYPE_CHECKING:
    from bot import UtonishBot


class TestCommands(discord.Cog):
    def __init__(self, bot: 'UtonishBot'):
        self.bot = bot

    @discord.slash_command(name='ping')
    async def ping(self, ctx: ApplicationContext):
        await ctx.respond('Pong!')
