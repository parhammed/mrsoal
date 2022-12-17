from dataclasses import dataclass
from typing import TYPE_CHECKING
import struct

from jdatetime import datetime
from pytz import timezone
import discord

from classes.collections import Account, Topic, Answer, Question
from ._base import get_or_create, Point
from .image import make_bars

if TYPE_CHECKING:
    from classes.bot import Bot

_tehran = timezone('Asia/Tehran')
_fmt = '%S:%M:%H %d-%m-%Y'
__all__ = ("profile", "level")


@dataclass
class _TopicInfo:
    point: Point = None
    question_count: int = 0


async def profile(
        bot: "Bot", author: discord.Member,
        member: discord.Member) -> discord.Embed:
    account = await get_or_create(bot, Account, {Account.discord_id: member.id})
    question_counts = await account.get_all_question_counts()
    points = await Answer.get_all_points(bot.db, account.id)
    infos: dict[str, _TopicInfo] = {}
    for topic, point in points.items():
        info = infos[topic] = _TopicInfo()
        info.point = point

    for topic, question_count in question_counts.items():
        info = infos.setdefault(topic, _TopicInfo())
        info.question_count = question_count

    birth = datetime.fromgregorian(
        datetime=member.created_at.astimezone(_tehran))
    join = datetime.fromgregorian(datetime=member.joined_at.astimezone(_tehran))
    creation = datetime.fromtimestamp(
        struct.unpack(">I", account.id.binary[0:4])[0], _tehran)
    embed = discord.Embed(
        title=f"{member.name}#{member.discriminator}",
        description=f"لقب: {member.nick}\n"
                    f"تاریخ ساخت اکانت: {birth.strftime(_fmt)}\n"
                    f"تاریخ عضویت: {join.strftime(_fmt)}\n"
                    f"تاریخ ایجاد حساب در بات: {creation.strftime(_fmt)}",
        color=0x07c3ff
    )
    embed.set_thumbnail(url=(member.avatar or member.default_avatar).url)
    embed.set_footer(
        text=f"درخواست شده توسط: {author.name}#{author.discriminator}")

    for topic, info in infos.items():
        point = info.point or Point()
        embed.add_field(
            name=f"موضوع {topic}",
            value=f"تعداد سوال ها: {info.question_count}\n"
                  f"تعداد جواب ها: {point.count}\n"
                  f"تعداد جواب های درست: {point.correct}\n"
                  f"تعداد جواب های نادرست: {point.incorrect}")
    return embed


async def level(bot: "Bot", topic_name: str, member: discord.Member,
                author: discord.Member) -> tuple[discord.File, discord.Embed]:
    topic_id = getattr(await Topic.get_by_name(bot, topic_name), "id", None)
    account = await get_or_create(bot, Account, {Account.discord_id: member.id})
    question_count = await bot.db[Question.__collection_name__].count_documents({
        Question.maker_id: account.id,
        Question.topic_id: topic_id, Question.is_active: True,
        Question.is_maker_hidden: False
    })
    point = await Answer.get_point(bot.db, account.id, topic_id)

    test_point = point.correct - (point.incorrect / 3)
    correct_percent = point.correct / (point.count or 1)
    incorrect_percent = point.incorrect / (point.count or 1)
    idk_percent = 1 - correct_percent - incorrect_percent

    return (
        discord.File(
            make_bars(correct_percent, incorrect_percent, idk_percent),
            filename="bars.png"),
        discord.Embed(
            title=f"موضوع {topic_name or 'general'}",
            color=0x00ff00
        ).add_field(
            name="تعداد سوالات ایجاد شده",
            value=str(question_count)
        ).add_field(
            name="تعداد کل جواب ها",
            value=str(point.count)
        ).add_field(
            name="تعداد جواب های درست",
            value=str(point.correct)
        ).add_field(
            name="تعداد جواب های نادرست",
            value=str(point.incorrect)
        ).add_field(
            name="امیتاز",
            value=str(round(test_point, 1))
        ).add_field(
            name="درصد جواب های درست",
            value=f"%{round(correct_percent * 100, 2)}"
        ).add_field(
            name="درصد جواب های نادرست",
            value=f"%{round(incorrect_percent * 100, 2)}"
        ).add_field(
            name="درصد جواب های نزده",
            value=f"%{round(idk_percent * 100, 2)}"
        ).set_author(
            name=f"{member.name}#{member.discriminator}",
            icon_url=(member.avatar or member.default_avatar).url
        ).set_image(
            url="attachment://bars.png"
        ).set_footer(
            text=f"درخواست شده توسط: {author.name}#{author.discriminator}")
    )
