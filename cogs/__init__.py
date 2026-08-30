import os

import discord
from discord.ext import commands


class ReactionListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        raw_trusted_id = os.getenv('TRUSTED_USER', False)
        if raw_trusted_id:
            self.trusted_id = int(raw_trusted_id) if str(raw_trusted_id).isnumeric() else raw_trusted_id
        else:
            self.trusted_id = None

    @commands.Cog.listener()
    async def on_ready(self):
        # Register the view here AFTER the asyncio event loop is running
        self.bot.add_view(PersistentDeleteView())
        print("Registered persistent views.")

class PersistentDeleteView(discord.ui.View):
    def __init__(self, timeout: int = None):
        trusted_id = os.getenv('TRUSTED_USER', False)
        self.trusted_id = int(trusted_id) if trusted_id.isnumeric() else trusted_id
        super().__init__(timeout=timeout)  # Infinite timeout

    """@discord.ui.button(
        label="Delete",
        style=discord.ButtonStyle.danger,
            emoji="🇽",
        custom_id="persistent_trusted_delete_button"  # REQUIRED for persistence
    )
    async def delete_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Verify trusted user
        print(button, interaction)
        if self.trusted_id and interaction.user.id == self.trusted_id:
            try:
                await interaction.message.delete()
            except discord.errors.Forbidden:
                # Fallback: Edit the content if hard deletion is blocked by Discord
                await interaction.message.edit(content="*[This message was removed by moderation]*", view=None)
        else:
            await interaction.response.send_message(
                "You do not have permission to delete this message.",
                ephemeral=True
            )"""
