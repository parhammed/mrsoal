from typing import Literal

import discord
from discord.ext import commands
from bson import ObjectId

from classes import BaseCog
from classes.collections import Topic, Question, Account, Option
from utils.access import AccessEnum, check_role_access


class Manager(BaseCog):
    __hidden__ = True

    def __init__(self, bot):
        super(Manager, self).__init__(bot)
        bot.topic_manger.set_autocomplete("topic", self.set_role)

    @commands.hybrid_command(hidden=True)
    @commands.is_owner()
    async def set_role(
            self,
            ctx: commands.Context,
            topic: str,
            rank: Literal['newbie', 'pro', 'master', 'head_master'],
            role: discord.Role
    ):
        await ctx.defer(ephemeral=True)
        if rank not in Topic.ranks:
            await ctx.send("rank not found", ephemeral=True)
            return
        topic = await Topic.get_by_name(self._bot.db, topic)
        if topic is None:
            await ctx.send("topic can not be general", ephemeral=True)
            return
        await self._bot.db[Topic.__collection_name__].update_one(
            {Topic.id: topic.id}, {'$set': {rank: role.id}})
        await ctx.send("done", ephemeral=True)

    @commands.hybrid_command(hidden=True)
    async def get_question(self, ctx: commands.Context, id: str):
        await ctx.defer()
        question_data = await anext(
            self._bot.db[Question.__collection_name__].aggregate([
                {"$match": {Question.id: ObjectId(id)}},
                {"$lookup": {
                    "from": Topic.__collection_name__,
                    "localField": Question.topic_id,
                    "foreignField": Topic.id,
                    "as": "topic"
                }},
                {"$unwind": {"path": "$topic",
                             "preserveNullAndEmptyArrays": True}},
                {"$lookup": {
                    "from": Account.__collection_name__,
                    "localField": Question.maker_id,
                    "foreignField": Account.id,
                    "as": "maker"}},
                {"$unwind": {"path": "$maker"}},
                {"$lookup": {
                    "from": Option.__collection_name__,
                    "localField": Question.id,
                    "foreignField": Option.question_id,
                    "as": "options"}},
            ]))
        topic = question_data.get("topic", None)
        if topic is not None:
            topic = Topic.from_data(self._bot, topic)
        check_role_access(AccessEnum.pro, ctx.author, self._bot, topic)

        options = [Option.from_data(self._bot, option) for option in
                   question_data["options"]]
        question = Question.from_data(self._bot, question_data)

        # TODO: finish this part
