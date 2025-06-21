import discord
from discord.ext import commands
from discord import Message
import os

# from analyzer import MessageAnalyzer
from cogs.quotes import QuoteCommands
from cogs.rename import RenameCommands
from cogs.testing import TestCommands
from quotes import QuoteGenerator


class UtonishBot(commands.Bot):
    """
    Main class for the bot. Initialize and call `.run()`
    """

    def __init__(
        self,
        token: str = None,
        message_checking: bool = False,
        **kwargs
    ):
        intents = discord.Intents.all()
        super().__init__(intents=intents, **kwargs)

        self._token = token
        # self.analyzer = MessageAnalyzer() if message_checking else None
        self.message_checking = message_checking
        self.quotes = list(QuoteGenerator.load())

    @property
    def token(self) -> str:
        return self._token or os.getenv('DISCORD_TOKEN')

    def setup(self) -> None:
        # self.add_cog(TestCommands(self))
        self.add_cog(RenameCommands(self))
        self.add_cog(QuoteCommands(self))

    async def on_message(self, message: Message):
        return
        if any((
            self.analyzer is None,
            not self.message_checking,
            message.author.bot,
            message.author.id == self.user.id
        )):
            return

        print(self.analyzer.analyse_message(message.content))

    async def start(self, *_) -> None:
        await super().start(self.token)
