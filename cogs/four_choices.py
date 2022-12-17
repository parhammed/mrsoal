from discord.ext import commands, tasks
import discord

from typing import TYPE_CHECKING

from classes import BaseCog
from classes.ui import CreateQuestionView, AnswerView
from classes.collections import Question, Account, Answer
from utils import get_or_create

if TYPE_CHECKING:
    from classes.bot import Bot

__all__ = ("FourChoiceQuestion",)

_choice_emojis = ("1️⃣", "2️⃣", "3️⃣", "4️⃣")


class FourChoiceQuestion(BaseCog):
    def __init__(self, bot: "Bot"):
        super(FourChoiceQuestion, self).__init__(bot)
        bot.topic_manger.set_autocomplete("topic", self.ask)

    @commands.hybrid_command(
        description="ساخت سوال چهارگزینه ای توسط کاربر",
        brief="ساخت سوال چهارگزینه ای توسط کاربر")
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def add(self, ctx: commands.Context):
        await ctx.defer(ephemeral=True)
        user = await get_or_create(
            self._bot, Account, {Account.discord_id: ctx.author.id}
        )
        cqv = CreateQuestionView(user, self._bot)
        msg = await ctx.reply(
            "loading...",
            view=cqv,
            ephemeral=True)
        await cqv.set_message(msg)

    @commands.hybrid_command(
        description="پرسش سوال توسط بات از کاربر",
        brief="پرسش سوال توسط بات از کاربر",
        extras={
            "topic": "از چه موضوع سوال بپرسم؟ در صورت خالی بودن از یه موضوع رندوم سوال میپرسم"
        })
    @discord.app_commands.describe(
        topic="از چه موضوع سوال بپرسم؟ در صورت خالی بودن از یه موضوع رندوم سوال میپرسم"
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ask(self, ctx: commands.Context, topic: str = None):
        await ctx.defer()
        (question, options, correct_index, topic, maker
         ) = await Question.get_by_random(self._bot, topic)

        complete_answer = question.complete_answer or ''
        account = await get_or_create(
            self._bot, Account, {Account.discord_id: ctx.author.id})

        if complete_answer and question.is_spoiler:
            complete_answer = f"||{complete_answer}||"

        av = AnswerView(account, self._bot, ctx.channel, correct_index,
                        complete_answer, options)

        msg = await ctx.send(
            embed=await question.show(options, ctx.author, topic, maker),
            view=av)
        await av.wait()
        await msg.edit(view=None)
        await Answer.create_complete_object(
            self._bot,
            user_id=account.id,
            option_id=av.fallback,
            question_id=question.id
        )

    @commands.hybrid_command(
        description="گرفتن تمامیه موضوعات بات",
        brief="گرفتن تمامیه موضوعات بات",
        aliases=("gat",))
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def get_all_topics(self, ctx: commands.Context):
        await ctx.send(embed=discord.Embed(
            title="لیست مضوعات بات",
            description=', '.join(self._bot.topic_manger.str_topics),
            color=0x00ffff))
