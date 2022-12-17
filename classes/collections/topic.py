from typing import Optional, TYPE_CHECKING

from .base_collection import BaseCollection
from .tools import Field
from classes.errors import TopicNotFoundError

if TYPE_CHECKING:
    from classes.bot import Bot


class Topic(BaseCollection):
    __collection_name__ = "topics"
    ranks = ("newbie", "pro", "master", "head_master")

    name = Field("name", type_=str, required=True)
    head_master = Field("head_master", type_=int, required=False)
    master = Field("master", type_=int, required=False)
    pro = Field("pro", type_=int, required=False)
    newbie = Field("newbie", type_=int, required=False)

    @classmethod
    async def get_by_name(cls, bot: "Bot", name: str) -> Optional["Topic"]:
        if not name or name == "general":
            return None
        data = await bot.db[cls.__collection_name__].find_one({cls.name: name})
        if data is None:
            raise TopicNotFoundError(name)
        return cls.from_data(bot, data)
