import os
from typing import TYPE_CHECKING

import discord
from discord import ApplicationContext, Forbidden

if TYPE_CHECKING:
    from bot import UtonishBot


class RenameCommands(discord.Cog):
    def __init__(self, bot: 'UtonishBot'):
        self.bot = bot
        trusted_id = os.getenv('TRUSTED_USER', False)
        self.trusted_id = int(trusted_id) if trusted_id.isnumeric() else trusted_id

    async def edit_nick(self, ctx: ApplicationContext, member: discord.Member, nick: str | None) -> bool:
        changes_self = ctx.user.guild_permissions.change_nickname
        change_others = ctx.user.guild_permissions.manage_nicknames or ctx.user.id == self.trusted_id
        if not change_others and not (changes_self and ctx.author == member):
            await ctx.respond(f':x: You don\'t have permissions to manage nicknames on this server!', ephemeral=True)
            return False

        try:
            await member.edit(nick=nick)
        except Forbidden:
            await ctx.respond(f':x: I cannot change this person\'s nickname.', ephemeral=True)
            return False

        return True

    @staticmethod
    def reverse_name(name: str) -> str:
        reversed_name = name[::-1].replace('(', '\u9990').replace(')', '\u9991')
        reversed_name = reversed_name.replace('\u9990', ')').replace('\u9991', '(')
        return reversed_name

    name_cmds = discord.SlashCommandGroup('name', 'Do fun and annoying stuff with user names')
    @name_cmds.command()
    async def reverse(self, ctx: ApplicationContext, member: discord.Member):
        original_name, reversed_name = member.display_name, self.reverse_name(member.display_name)
        if not await self.edit_nick(ctx, member, reversed_name):
            return

        await ctx.respond(f':white_check_mark: Reversed {original_name}\'s name to {reversed_name}!', ephemeral=True)

    @name_cmds.command()
    async def reset(self, ctx: ApplicationContext, member: discord.Member = None):
        if member is None:
            member = ctx.author
        if not await self.edit_nick(ctx, member, None):
            return

        await ctx.respond(f':white_check_mark: {member.display_name}\'s was reset!', ephemeral=True)
