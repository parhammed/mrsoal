from typing import TYPE_CHECKING, Optional
from enum import Enum, auto, unique

import discord
from discord.ext import commands

from classes.errors import MissingAccessError

if TYPE_CHECKING:
    from classes.collections.topic import Topic
    from classes.bot import Bot


@unique
class AccessEnum(Enum):
    head_master = auto()
    master = auto()
    pro = auto()
    newbie = auto()


def is_manager():
    """add check for the author of command is the manager or not"""
    async def predicate(ctx: commands.Context["Bot"]) -> bool:
        if getattr(ctx.guild, 'id', 0) != ctx.bot.settings['main_guild']:
            raise MissingAccessError()
        if ctx.permissions.administrator:
            return True

        raise MissingAccessError()

    return commands.check(predicate)


def is_admin():
    """add check for the author is admin or not"""
    async def predicate(ctx: commands.Context["Bot"]) -> bool:
        if getattr(ctx.guild, 'id', 0) != ctx.bot.settings['main_guild']:
            raise MissingAccessError()

        if (ctx.permissions.administrator or discord.utils.get(
                ctx.author.roles, id=ctx.bot.settings["admin"]
        ) is not None):
            return True

        raise MissingAccessError()

    return commands.check(predicate)


def check_role_access(
        level: AccessEnum,
        member: discord.Member,
        bot: "Bot",
        topic: Optional["Topic"]) -> None:
    """check the member has enough access to use command or not
    raise :class:`MissingAccessError` when access failed"""
    if getattr(member.guild, 'id', 0) != bot.settings['main_guild']:
        raise MissingAccessError()

    if member.guild_permissions.administrator:
        return

    roles = frozenset((role.id for role in member.roles[1:]))
    if topic is None:
        if (level in (AccessEnum.newbie, AccessEnum.pro)
                and bot.settings["admin"] in roles):
            return
        raise MissingAccessError()

    if topic.head_master in roles:
        return
    if level is AccessEnum.head_master:
        raise MissingAccessError()

    if topic.master in roles:
        return
    if level is AccessEnum.master:
        raise MissingAccessError()

    if topic.pro in roles:
        return
    if level is AccessEnum.pro:
        raise MissingAccessError()

    if topic.newbie in roles:
        return
    raise MissingAccessError()
