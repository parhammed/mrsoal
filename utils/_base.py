__all__ = ("root", "numbers", "get", "safe_text", "get_or_create", "Point")

import re
from os.path import dirname, abspath
from typing import TypeVar, Mapping, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from classes.collections.base_collection import BaseCollection
    from classes.bot import Bot

    _object = TypeVar("_object", bound=BaseCollection)

# mrsoal folder
root = abspath(dirname(dirname(__file__)))
# persian numbers from 0 to 35
numbers = [
    "صفرم", "اول", "دوم", "سوم", "چهارم", "پنجم",
    "ششم", "هفتم", "هشتم", "نهم", "دهم",
    "یازدهم", "دوازدهم", "سیزدهم", "چهاردهم", "پانزدهم",
    "شانزدهم", "هفدهم", "هجدهم", "نوزدهم", "بیستم",
    "بیست و یکم", "بیست و دوم", "بیست و سوم", "بیست و چهارم", "بیست و پنجم",
    "بیست و ششم", "بیست و هفتم", "بیست و هشتم", "بیست و نهم", "سی‌ام",
    "سی و یکم", "سی و دوم", "سی و سوم", "سی و چهارم", "سی و پنجم"
]

_key = TypeVar("_key")
_item = TypeVar("_item")
_default = TypeVar("_default")
# letters that change style of text in discord
_safe_re = re.compile(r"[\\_|*`>~]")


class Point:
    count: int = 0
    correct: int = 0
    incorrect: int = 0


def get(items: Mapping[_key, _item], key: _key,
        default: _default = None) -> _default | _item:
    """return the value with index or key

    when item not found, we return :parm:`default`

    like  :parm:`items`[:parm:`key`] but without raising error when
    item not found

    :param items: Mapping
        the mapping like :class:`list` or :class:`tuple` that you want
        to get item

    :param key:
        the index or key in :class:`list` or :class:`tuple` (or maybe
        :class:`dict`)

    :param default:
        when item not found we return this parameter

    :return: the item that stored in :parm:`items`[:parm:`key`]
    or :parm:`default`

    """
    try:
        return items[key]
    except IndexError or KeyError:
        return default


def _add_backslash(match: re.Match) -> str:
    """add backslash to first of match"""
    return "\\" + match.group(0)


def safe_text(text: str) -> str:
    """safe the text from changing style (and removing chars) in
    discord

    :param text: :class:`str`
        dangerous text

    :return: :class:`str`
        safe text
    """
    return _safe_re.sub(_add_backslash, text)


async def get_or_create(bot: "Bot", model: Type["_object"],
                        kwargs: dict[str, ...], default: dict[str, ...] = None) \
        -> "_object":
    """get a object or create it

    :param bot:
        the database that we want to get or insert object

    :param model: Type[_object]
        the collection that we want to get or insert object

    :param kwargs: dict[:class:`str`, ...]
        a MATCH filter to get or insert object

    :param default:
        to insert defaults in inserted object

    :return: _object
        the object that got or inserted

    """
    default = default or {}
    return model.from_data(
        bot,
        await bot.db[model.__collection_name__].find_one_and_update(
            kwargs, {"$setOnInsert": default | kwargs}, upsert=True,
            return_document=True))
