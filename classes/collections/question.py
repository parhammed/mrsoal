import logging
from typing import TYPE_CHECKING, Union
from random import randrange
from jdatetime import date
from struct import unpack
from utils import numbers

from bson import ObjectId
import discord

from .base_collection import BaseCollection
from .tools import Field

if TYPE_CHECKING:
    from .topic import Topic
    from .option import Option
    from classes.bot import Bot

_log = logging.getLogger(__file__)
correct_index_type = int
topic_name_type = str


class Question(BaseCollection):
    __collection_name__ = "questions"

    content = Field(name="content", type_=str, required=True)
    complete_answer = Field(name="complete_answer", type_=str, required=False)
    is_maker_hidden = Field(name="is_maker_hidden", type_=bool, default=False)
    is_spoiler = Field(name="is_spoiler", type_=bool, default=False)
    is_active = Field(name="is_active", type_=bool, default=False)
    maker_id = Field(name="maker", type_=ObjectId, required=True)
    topic_id = Field(name="topic", type_=ObjectId, required=False)

    async def upload_all_question(self, data: list[dict[str, ...]]):
        pass

    @classmethod
    async def get_by_random(
            cls, bot: "Bot", topic_name: Union[str, "Topic", ObjectId, None]) \
            -> tuple[
                "Question",
                list["Option"],
                correct_index_type,
                topic_name_type,
                discord.User
            ]:
        from .topic import Topic
        from .option import Option
        from .account import Account

        topic: str | None = None
        pipeline = [
            {"$lookup": {
                "from": Topic.__collection_name__,
                "localField": cls.topic_id,
                "foreignField": Topic.id,
                "as": "topic_obj",
                "pipeline": [
                    {"$project": {Topic.name: True, Topic.id: False}}
                ]
            }},
            {"$unwind": {
                "path": "$topic_obj",
                "preserveNullAndEmptyArrays": True}}
        ]

        if isinstance(topic_name, str):
            topic = topic_name
            if topic_name != "general":
                pipeline.append(
                    {"$match": {f"topic_obj.{Topic.name}": topic_name}}
                )
        elif isinstance(topic_name, Topic):
            topic = topic_name.name
            pipeline.clear()
            pipeline.append(
                {"$match": {cls.topic_id: topic_name.id}}
            )
        elif isinstance(topic_name, ObjectId):
            pipeline.append(
                {"$match": {cls.topic_id: topic_name}}
            )

        elif topic_name is not None:
            _log.warning(
                f"topic_name is not valid type {topic_name}: {type(topic_name)}"
            )
        pipeline.extend([
            {"$match": {cls.is_active: True}},
            {"$sample": {"size": 1}},
            {"$lookup": {
                "from": Option.__collection_name__,
                "localField": cls.id,
                "foreignField": Option.question_id,
                "as": "incorrects",
                "pipeline": [
                    {"$match": {Option.is_correct: False}},
                    {"$sample": {"size": 3}}
                ]
            }},
            {"$lookup": {
                "from": Option.__collection_name__,
                "localField": cls.id,
                "foreignField": Option.question_id,
                "as": "correct",
                "pipeline": [
                    {"$match": {Option.is_correct: True}},
                    {"$sample": {"size": 1}}
                ]
            }},
            {"$unwind": {"path": "$correct"}},
            {"$lookup": {
                "from": Account.__collection_name__,
                "localField": cls.maker_id,
                "foreignField": Account.id,
                "as": "maker_acc",
                "pipeline": [
                    {"$project": {Account.id: False, Account.discord_id: True}},
                ]
            }},
            {"$unwind": {"path": "$maker_acc"}},
        ])
        data = await anext(
            bot.db[Question.__collection_name__].aggregate(pipeline)
        )
        if topic is None:
            topic: str = data.pop("topic_obj", {Topic.name: "general"})[
                Topic.name]
        else:
            data.pop("topic_obj", None)

        options = [
            Option.from_data(bot, option)
            for option in data.pop("incorrects")
        ]
        assert len(options) == 3
        correct_option = Option.from_data(bot, data.pop("correct"))
        correct_index = randrange(4)
        options.insert(correct_index, correct_option)
        maker = bot.get_user(data.pop("maker_acc")[Account.discord_id])
        question = cls.from_data(bot, data)
        return question, options, correct_index, topic, maker

    @property
    def creation_jdate(self) -> str:
        d = date.fromtimestamp(unpack(">I", self.id.binary[0:4])[0])
        return f"{numbers[d.day]} {date.j_months_fa[d.month - 1]} سال {d.year}"

    async def show(self, options: list["Option"], author: discord.User,
                   topic_name: str,
                   maker: discord.User) -> discord.Embed:
        embed = discord.Embed(
            title=f"کد سوال: {self.id}",
            description=(
                f"⚠ اخطار: این سوال حاویه اسپویل است\n||{self.content}||"
                if self.is_spoiler else
                self.content),
            color=0xffff00 if self.is_spoiler else 0x00ffff
        ).set_footer(
            text=f"موضوع سوال: {topic_name}"
                 f"\nتاریخ ایجاد این سوال: {self.creation_jdate}"
                 f"\nدرخواست شده توسط: {author.name}#{author.discriminator}"
        )
        if not self.is_maker_hidden:
            if isinstance(maker, int):
                embed.set_author(name=f"ساخته شده توسط: Unknown#0000 ({maker})")
            else:
                embed.set_author(
                    name=f"ساخته شده توسط: {maker.name}#{maker.discriminator}",
                    icon_url=maker.display_avatar.url)
        for index, option in enumerate(options):
            embed.add_field(
                name=f"گزینه {index + 1}:",
                value=f"||{option.content}||" if self.is_spoiler else option.content,
                inline=False
            )
        return embed

    def preview(self, options: list[str], topic_name: str,
                correct_option: str) -> discord.Embed:
        embed = (
            discord.Embed(
                title=f"**موضوع**: {topic_name}",
                description=f"**متن سوال**: {self.content or 'خالی'}\n",
                color=0xff8800
            ).add_field(
                name="جواب کامل",
                value=self.complete_answer or 'خالی',
                inline=False
            ).add_field(
                name="اسپویل بودن سوال",
                value='بله' if self.is_spoiler else 'خیر',
                inline=False
            ).add_field(
                name="نمایش اسم سازنده",
                value='خیر' if self.is_maker_hidden else 'بله',
                inline=False
            ).add_field(
                name="گزینه صحیح",
                value=correct_option or 'خالی',
                inline=False
            )
        )
        i = 2
        for option in options:
            embed.add_field(name=f"گزینه {numbers[i]}", value=option or 'خالی',
                            inline=False)
            i += 1
        return embed

    def full_data(self, topic: "Topic", maker: discord.Member,
                  options: list["Option"]):
        embed = (
            discord.Embed(
                title=f"**آیدی**: {self.id}",
                description=f"**متن سوال**: {self.content or 'خالی'}\n",
                color=0x00ffff
            ).add_field(
                name="موضوع",
                value=topic.name
            ).add_field(
                name="جواب کامل",
                value=self.complete_answer or 'خالی',
                inline=False
            ).add_field(
                name="اسپویل بودن سوال",
                value='بله' if self.is_spoiler else 'خیر',
                inline=False
            ).add_field(
                name="نمایش اسم سازنده",
                value='خیر' if self.is_maker_hidden else 'بله',
                inline=False
            ).set_author(
                name=f"{maker.name}#{maker.discriminator}",
                icon_url=(maker.avatar or maker.default_avatar).url)
        )

        for option in options:
            embed.add_field(
                name=option.content,
                value=f"صحت سوال: {option.is_correct}",
                inline=False)

        return embed
