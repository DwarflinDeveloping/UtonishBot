import random
from datetime import datetime
from typing import TYPE_CHECKING, List

import discord
from discord import ApplicationContext, option
from discord.ext import commands

from cogs import PersistentDeleteView
from cogs.censor import CensorCommands

if TYPE_CHECKING:
    from bot import UtonishBot


class QuoteInfoView(PersistentDeleteView):
    """A view containing a button to show extra quote metadata."""

    def __init__(self, quote: dict):
        super().__init__(timeout=None)
        self.quote = quote

        # Set button label to the author's nickname or name
        author_data = quote.get('author', {})
        author_name = author_data.get('nickname') or author_data.get('name', 'Unknown')

        # Create the button dynamically
        button = discord.ui.Button(
            label=f"Quote by {author_name}",
            style=discord.ButtonStyle.secondary
        )
        button.callback = self.show_details
        self.add_item(button)

    async def show_details(self, interaction: discord.Interaction):
        """Sends the ephemeral embed when the button is clicked."""
        quote = self.quote
        embed = discord.Embed(color=discord.Color.blue())

        # 1. Add Timestamp
        timestamp_str = quote.get('timestamp', None)
        if timestamp_str:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            embed.add_field(name="Date", value=discord.utils.format_dt(dt, style='F'))

        # 2. Add Message Link
        ref = quote.get('reference', {})
        guild_id = ref.get('guildId', '@me')
        channel_id = ref.get('channelId')
        message_id = quote.get('id')

        if channel_id and message_id:
            url = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
            embed.add_field(name="Context", value=f"[Jump to Message]({url})")

        # 3. Add Footer with Author Profile Picture and Tag
        author_data = quote.get('author', {})
        author_name = author_data.get('name', 'Unknown')
        discriminator = author_data.get('discriminator')

        # Combine name and discriminator for the full tag
        author_tag = f"{author_name}#{discriminator}" if discriminator and discriminator != "0000" else author_name
        avatar_url = author_data.get('avatarUrl')

        embed.set_footer(text=f"Sent by {author_tag}", icon_url=avatar_url)

        await interaction.response.send_message(embed=embed, ephemeral=True)


class QuoteGuessView(discord.ui.View):
    """A view that lets users guess the author of a quote via a dropdown."""

    def __init__(self, quote: dict, options: List[str]):
        super().__init__(timeout=60)
        self.quote = quote
        # Get the correct name for validation
        author_data = quote.get('author', {})
        self.correct_author = author_data.get('nickname') or author_data.get('name', 'Unknown')

        # Create the dropdown
        select = discord.ui.Select(
            placeholder="Who said this?",
            options=[discord.SelectOption(label=name) for name in options]
        )
        select.callback = self.check_guess
        self.add_item(select)

    async def check_guess(self, interaction: discord.Interaction):
        """Checks if the selected user is correct and reveals details if so."""
        guess = interaction.data['values'][0]

        if guess == self.correct_author:
            # If correct, edit original message to show the quote with the info button
            content = f"✅ **Correct!** It was indeed **{self.correct_author}**.\n\n{self.quote['content']}"
            await interaction.response.edit_message(content=content, view=QuoteInfoView(self.quote))
        else:
            # If wrong, send a private hint
            await interaction.response.send_message(f"❌ Not quite! That wasn't {guess}. Try again!", ephemeral=True)


class QuoteCommands(discord.Cog):
    def __init__(self, bot: 'UtonishBot'):
        self.bot = bot
        self.censor_interface = CensorCommands(self.bot)

    async def _quote(self, ctx: ApplicationContext, quotes: list):
        if not quotes:
            await ctx.respond('No quotes found...', ephemeral=True)
            return

        quote = random.choice(quotes)
        content = self.censor_interface.censor_text(quote['content'].replace('@', '＠'))
        view = QuoteInfoView(quote)
        await ctx.respond(content, view=view)

    def get_askutonish(self) -> str:
        if random.random() < 0.001:
            return '👹 YOU HAVE BEEN SENT TO THE T̵̲̰̈́R̵̘̝͒̏I̵̦̝̓̅A̵̡̞̅̈L̵̺̞̈́S̵̙̝̈́. PREPARE TO DIE.'
        if random.random() < 0.03:
            return '**😠 Utonish is extremely angered by this ridiculous remark…\nHe has ordered a flock of killer drones to take you out. Better go hide!**'
        if random.random() < 0.40:
            return '*Utonish does not respond to your request. You have been ghosted.*'

        return random.choice(self.bot.askutonish_quotes)

    # Allowed integration types & contexts for user installation
    quote_cmds = discord.SlashCommandGroup(
        name='quote',
        description='Generate or search for quotes',
        integration_types={discord.IntegrationType.guild_install, discord.IntegrationType.user_install},
        contexts={discord.InteractionContextType.guild, discord.InteractionContextType.bot_dm, discord.InteractionContextType.private_channel}
    )

    @quote_cmds.command()
    async def benyi(self, ctx: ApplicationContext):
        await self._quote(ctx, self.bot.benyi_quotes)

    @quote_cmds.command()
    async def potential(self, ctx: ApplicationContext):
        await self._quote(ctx, self.bot.potential_quotes)

    @quote_cmds.command()
    async def dtm(self, ctx: ApplicationContext):
        await self._quote(ctx, self.bot.dtm_quotes)

    @quote_cmds.command()
    async def bilip(self, ctx: ApplicationContext):
        await self._quote(ctx, self.bot.bilip_quotes)

    @quote_cmds.command()
    async def utonish(self, ctx: ApplicationContext):
        await self._quote(ctx, self.bot.utonish_quotes)

    @quote_cmds.command()
    async def random(self, ctx: ApplicationContext):
        await self._quote(ctx, self.bot.quotes)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages sent by bots (including itself)
        if message.author.bot:
            return

        # Check if the bot was pinged in the message
        if self.bot.user in message.mentions:
            if not self.bot.utonish_quotes:
                await message.channel.send("No utonish quotes found...")
                return

            await message.reply(self.get_askutonish())

    async def get_quote_suggestions(self, ctx: discord.AutocompleteContext):
        """Logic for weighted search results."""
        query = ctx.value.lower()
        if not query:
            return [q['content'][:100] for q in self.bot.quotes[:25]]

        # Filter quotes that contain the query
        matches = [q['content'] for q in self.bot.quotes if query in q['content'].lower()]

        # Sort matches: shorter total length (closer to exact match) comes first
        matches.sort(key=len)

        return [m[:100] for m in matches][:25]

    @quote_cmds.command(name="search", description="Search for a specific quote")
    @option("query", description="Type to search...", autocomplete=get_quote_suggestions)
    async def search(self, ctx: ApplicationContext, query: str):
        found_quote = next((q for q in self.bot.quotes if q['content'].startswith(query)), None)
        if found_quote:
            content = self.censor_interface.censor_text(found_quote['content'].replace('@', '＠'))
            await ctx.respond(content, view=QuoteInfoView(found_quote))
        else:
            await ctx.respond("Quote no longer exists.", ephemeral=True)

    @discord.slash_command(
        integration_types={discord.IntegrationType.guild_install, discord.IntegrationType.user_install},
        contexts={discord.InteractionContextType.guild, discord.InteractionContextType.bot_dm, discord.InteractionContextType.private_channel}
    )
    @discord.ext.commands.cooldown(1, 600, discord.ext.commands.BucketType.user)
    async def askutonish(self, ctx: ApplicationContext):
        await ctx.respond(self.get_askutonish())

    @askutonish.error
    async def askutonish_error(self, ctx: ApplicationContext, error):
        """Error handler specifically for the askutonish command."""
        if isinstance(error, commands.CommandOnCooldown):
            # Formats the remaining time (e.g., 45.2s) into a readable string
            retry_after = round(error.retry_after)
            await ctx.respond(
                f"⏳ Utonish will not respond to your spam. Please wait **{retry_after} seconds** before asking again.",
                ephemeral=True
            )
        else:
            # Raise other errors so they aren't silently swallowed
            raise error