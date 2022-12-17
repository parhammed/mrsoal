from discord.ext import commands
import discord

from classes import BaseCog

from utils.account import profile as _profile, level as _level


class AccountCog(BaseCog):
    def __init__(self, bot):
        super(AccountCog, self).__init__(bot)
        self._app_adder(
            discord.app_commands.ContextMenu(
                name="profile", callback=self.profile_menu)
        )
        bot.topic_manger.set_autocomplete("topic", self.level)

    @commands.hybrid_command(
        description="اطلاعات حساب",
        brief="اطلاعات حساب",
        extras={
            "member": "اطلاعات چه کسی را نیاز دارید؟ (روی ربات ها تاثیر ندارد)"
        }
    )
    @commands.guild_only()
    @commands.cooldown(1, 20, commands.BucketType.channel)
    async def profile(self, ctx: commands.Context,
                      member: discord.Member = None):
        if member and member.bot:
            await ctx.send("این شخص یه بات است", ephemeral=True)
            return

        await ctx.defer()
        await ctx.reply(
            embed=await _profile(self._bot, ctx.author, member or ctx.author))

    async def profile_menu(self, interaction: discord.Interaction,
                           member: discord.Member):
        if member.bot:
            await interaction.response.send_message(
                "این شخص یه بات است",
                ephemeral=True
            )
            return
        await interaction.response.defer()
        await interaction.followup.send(
            embed=await _profile(self._bot, interaction.user, member)
        )

    @commands.hybrid_command(description="سطح شخص در یک موضوع",
                             brief="سطح شخص در یک موضوع")
    @commands.guild_only()
    @commands.cooldown(1, 20, commands.BucketType.channel)
    async def level(self, ctx: commands.Context, topic: str,
                    member: discord.Member = None):
        if member and member.bot:
            await ctx.send("این شخص یه بات است", ephemeral=True)
            return

        await ctx.defer()
        file, embed = await _level(
            self._bot,
            topic,
            member or ctx.author,
            ctx.author)
        await ctx.send(embed=embed, file=file)
