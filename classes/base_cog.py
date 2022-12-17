from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from bot import Bot


class BaseCog(commands.Cog):
    __hidden__ = False

    def __init__(self, bot: "Bot"):
        self._bot: "bot" = bot

        app_adder = getattr(bot, (
            "add_hidden_app_command"
            if self.__hidden__ else
            "add_app_command"
        ))
        # for command in self.__cog_commands__:
        #     app_command = getattr(command, "app_command", None)
        #     if app_command:
        #         app_adder(app_command)
        # for app_command in self.__cog_app_commands__:
        #     app_adder(app_command)
        self._app_adder = app_adder
