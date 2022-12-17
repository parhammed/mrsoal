from typing import TYPE_CHECKING
from discord.ext import commands
import discord

from classes.collections import Guild
from classes import BaseCog
from utils import safe_text, get_or_create

if TYPE_CHECKING:
    from classes.bot import Bot


class GuildCog(BaseCog):
    def __init__(self, bot: "Bot"):
        super(GuildCog, self).__init__(bot)
        self._reset_prefix_embed = discord.Embed(
            title="پرفیکس با موفقیت ریست شد",
            description=f"پرفیکس فعلی:\n{bot.settings['default_prefix']}",
            color=0xffff00)

    @commands.hybrid_command(
        description="تغییر پرفیکس بات برای سرور",
        brief="تغییر پرفیکس بات برای سرور",
        extras={
            "prefix": "پرفیکس جدید بات در صورت خالی بودن پرفیکس ریست میشود"
        },
        aliases=("cp",))
    @discord.app_commands.describe(
        prefix="پرفیکس جدید بات در صورت خالی بودن پرفیکس ریست میشود"
    )
    @discord.app_commands.default_permissions(administrator=True)
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    @commands.cooldown(3, 60, commands.BucketType.guild)
    async def change_prefix(self, ctx: commands.Context, *, prefix: str = None):
        await ctx.defer()
        new_prefix = prefix or self._bot.settings["default_prefix"]

        await self._bot.db[Guild.__collection_name__].update_one(
            {Guild.discord_id: ctx.guild.id},
            {"$setOnInsert": {Guild.discord_id: ctx.guild.id},
             "$set": {"prefix": new_prefix}}, upsert=True)
        self._bot.prefixes[ctx.guild.id] = new_prefix
        if prefix is None:
            await ctx.reply(embed=self._reset_prefix_embed)
        else:
            embed = discord.Embed(
                title="عملیات با موفقیت انجام شد",
                description=f"پرفیکس جدید:\n{safe_text(new_prefix)}",
                color=0x00ff00)
            await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return

        if message.content.strip() == self._bot.user.mention:
            await message.reply(
                f"پرفیکس فعلی بات در اینجا:"
                f"\n{safe_text((await self._bot.get_prefix(message))[0])}"
            )

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await get_or_create(self._bot.db, Guild, {"discord_id": guild.id},
                            {"prefix": self._bot.settings["default_prefix"]})
