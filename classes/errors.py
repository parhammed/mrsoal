import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from classes.collections.base_collection import BaseCollection

_no_private_embed = discord.Embed(
    title="کامند مورد نظر شما در پی وی کار نمیکند❌",
    description="لطفا در سرور مورد نظر خود امتحان کنید",
    color=0xffff00
)
_missing_access_embed = discord.Embed(
    title="شما حق استفاده از این کامند را ندارید",
    description="اگر مشکلی در بات مشاهده میکنید لطفا تیکت دهید",
    color=0xff0000
)

_log = logging.getLogger(__name__)
__all__ = ("TopicNotFoundError", "MissingAccessError", "error_handler",
           "FieldNotFoundError")


class TopicNotFoundError(Exception):
    """raise when topic didn't find"""

    def __init__(self, topic, *args):
        self.topic = topic
        super(TopicNotFoundError, self).__init__(*args)


class FieldNotFoundError(Exception):
    """raise when a field in collections didn't found"""

    def __init__(self, field_name: str, collection: "BaseCollection"):
        self.field_name = field_name
        self.collection = collection
        super(FieldNotFoundError, self).__init__(
            f"the {field_name} field didn't found in {collection}")


class MissingAccessError(Exception):
    """raise when Permission denied"""
    pass


def error_handler(base_error: Exception, debug=False) \
        -> tuple[float | None, discord.Embed] | None:
    if debug:
        _log.error("error", exc_info=base_error)
    error = base_error
    if isinstance(error, commands.HybridCommandError):
        error = error.original
    if isinstance(error, (
            commands.CommandInvokeError,
            discord.app_commands.CommandInvokeError)):
        error = error.original

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="کامند مورد نظر در حالت استراحت است😴",
            description=f"لطفا بعد از {round(error.retry_after, 2)} مجددا تلاش کنید",
            color=0x00ffff)
        return min(error.retry_after, 20), embed

    if isinstance(error, TopicNotFoundError):
        return 30, discord.Embed(
            title=f"موضوع {error.topic} یافت نشد",
            description=f"لطفا با دستور gat لیست موضوعات بات را چک کنید"
        )

    if isinstance(error, commands.NoPrivateMessage):
        return None, _no_private_embed

    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="شما دسترسی های لازم را ندارید",
            description="نیازمندی ها:\n{}".format(
                '\n'.join(error.missing_permissions)),
            color=0xffff00)
        return None, embed

    if isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            title="بات دسترسی های لازم را ندارد درصورتی که شما نمیتوانید به بات دسترسی های خواسته شده را بدهید به اونر سرور اطلاع دهید",
            description="نیازمندی ها:\n{}".format(
                '\n'.join(error.missing_permissions)),
            color=0xff0000)
        return None, embed

    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title=f"شما پارامتر {error.param.name} را وارد نکرده اید",
            description=str(error.param.annotation),
            color=0xffff00
        )
        return 20, embed

    if isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title=f"ممبر `{error.argument}` یافت نشد",
            description="لطفا آیدی شخص مورد نظر را بنویسید یا آن را منشن کنید",
            color=0xffff00
        )
        return 30, embed

    if isinstance(error, MissingAccessError):
        return None, _missing_access_embed
    if not debug:
        _log.error("Warning: The Unknown Error", exc_info=base_error)
