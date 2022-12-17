from typing import TYPE_CHECKING, Callable, TypeVar
from asyncio import Task

from discord.ext import tasks, commands
from discord import app_commands
import discord

from classes.collections import Topic

if TYPE_CHECKING:
    from .bot import Bot
_command = TypeVar("_command", discord.app_commands.AppCommand,
                   commands.HybridCommand)


class TopicManager:
    def __init__(self, bot: "Bot"):
        self._topics = []
        self._bot: "Bot" = bot

    async def _autocomplete(self, inter: discord.Interaction, value: str):
        return [
            app_commands.Choice(name=topic, value=topic)
            for topic in self.str_topics if value.lower() in topic]

    def set_autocomplete(self, name: str, cmd: _command) -> _command:
        return cmd.autocomplete(name)(self._autocomplete)

    def __call__(self, name: str) -> Callable[[_command], _command]:
        def inner(
                cmd: discord.app_commands.AppCommand | commands.HybridCommand):
            return cmd.autocomplete(name)(self._autocomplete)

        return inner

    def start(self) -> Task[None]:
        return self._set_all_topic.start()

    @tasks.loop(hours=1)
    async def _set_all_topic(self):
        self._topics = [
            Topic.from_data(self._bot, item)
            async for item in
            self._bot.db[Topic.__collection_name__].find().sort(Topic.name)]

    @property
    def topics(self) -> list[Topic]:
        return self._topics.copy()

    @property
    def str_topics(self) -> list[str]:
        return [
            *(topic.name for topic in self._topics)
        ]
