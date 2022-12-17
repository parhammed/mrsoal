from .base_collection import BaseCollection
from .tools import Field


class Guild(BaseCollection):
    __collection_name__ = "guilds"

    prefix = Field(name="prefix", type_=str, required=False)
    discord_id = Field(name="discord_id", type_=int, required=False)

    @classmethod
    async def get_prefix(cls, db, discord_id: int, default_prefix: str) -> str:
        return (await db[cls.__collection_name__].find_one(
            {cls.discord_id: discord_id},
            {cls.id: False, cls.prefix: True}
        )).get(cls.prefix, default_prefix)
