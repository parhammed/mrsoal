import discord
from discord.ext import commands
from classes.base_cog import BaseCog


class HelperCog(BaseCog):
    @commands.hybrid_command(
        name="help",
        description="نمایش یک کامند با جزئیات کامل یا کل کامندها با توضیحات مختصر",
        brief="نمایش یک کامند با جزئیات کامل یا کل کامندها با توضیحات مختصر",
        extras={
            "command": "کامند مورد نظر درصورت خالی بودن کل کامند هارا نمایش میدهد"
        },
        aliases=("h",))
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def _help(self, ctx: commands.Context, command: str = None):
        prefix = (await self._bot.get_prefix(ctx.guild))[0]
        if command is None:
            embed = discord.Embed(
                title="لیست کامند های بات",
                description=f"پرفیکس فعلی:\n {prefix}",
                color=0x00ffff
            )
            for com in self._bot.commands:
                if com.hidden:
                    continue
                embed.add_field(
                    name=f"<a:dar_hale_anjam:1002897734652670053>{com.name}",
                    value=com.brief, inline=False
                )
            await ctx.send(embed=embed)
        else:
            com = self._bot.get_command(command)
            if com is None or com.hidden:
                await ctx.send(embed=discord.Embed(
                    title="کامند مورد نظر یافت نشد",
                    color=0xff0000
                ))
                return
            short_name = com.name
            params = "".join(
                (f"[{key}]" if value.required else f"<{key}>" for key, value in
                 com.clean_params.items()))

            embed = discord.Embed(
                title=f"{prefix} {com.name}",
                description=com.brief,
                color=0x00ffff)
            if com.aliases:
                embed.add_field(
                    name="نام های دیگر",
                    value='\n'.join(com.aliases),
                    inline=False
                )
                short_name = min(com.aliases, key=len)
            embed.add_field(
                name="نحوه استفاده",
                value=f"{prefix}{short_name} {params}",
                inline=False
            )
            if com.extras:
                embed.add_field(
                    name="ورودی های کامند",
                    inline=False,
                    value='\n'.join((
                        f"{k}: {v}"
                        for k, v in com.extras.items()
                    )),
                )
            await ctx.send(embed=embed)

    @_help.autocomplete("command")
    async def command_autocomplete(self, inter: discord.Interaction,
                                   string: str):
        return [
            discord.app_commands.Choice(name=command.name, value=command.name)
            for command in self._bot.commands
            if string.lower() in command.name.lower()
        ]
