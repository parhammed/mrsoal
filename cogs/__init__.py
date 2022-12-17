from typing import TYPE_CHECKING, Type
from .guild_cog import GuildCog
from .four_choices import FourChoiceQuestion
from .helper import HelperCog
from .account_cog import AccountCog
from .manager import Manager

if TYPE_CHECKING:
    from classes.bot import Bot
    from classes.base_cog import BaseCog

cogs: list[Type["BaseCog"]] = [
    GuildCog,
    FourChoiceQuestion,
    HelperCog,
    AccountCog,
    Manager
]


async def setup(bot: "Bot") -> None:
    bot.remove_command("help")
    for cog in cogs:
        if cog.__hidden__ or bot.settings["debug"]:
            await bot.add_cog(cog(bot), guilds=bot.settings["test_guilds"])
        else:
            await bot.add_cog(cog(bot))
