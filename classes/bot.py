import json

from motor.motor_asyncio import AsyncIOMotorClient
from discord.ext import commands
from discord import app_commands
import discord

from classes import error_handler, TopicManager
from classes.collections import Guild
from cogs import setup

supported_app_commands = (
        app_commands.Command
        | app_commands.ContextMenu
        | app_commands.Group
)


class Bot(commands.Bot):
    def __init__(self, settings_path: str):
        with open(settings_path, 'r') as file:
            self._settings = json.load(file)
        self._db = AsyncIOMotorClient(self._settings.pop("engine_url"))[
            "mrsoal"]
        self._settings["test_guilds"] = [
            discord.Object(guild)
            for guild in self._settings["test_guilds"]
        ]
        # cached prefixes by guild id
        self.prefixes: dict[int, str] = {}
        self._topic_manager = TopicManager(self)
        super(Bot, self).__init__(self._settings['default_prefix'], intents=discord.Intents.all())

    async def setup_hook(self) -> None:
        self._topic_manager.start()
        await setup(self)
        for guild in self._settings["test_guilds"]:
            self.tree.copy_global_to(guild=guild)
        await self.tree.sync()

    async def get_prefix(
            self, message: discord.Message | discord.Guild | None) \
            -> list[str]:
        if isinstance(message, discord.Message):
            guild = message.guild
        else:
            guild = message
        prefix = default_prefix = self._settings["default_prefix"]
        if guild is not None:
            prefix = self.prefixes.get(guild.id, None)
            if prefix is None:
                self.prefixes[guild.id] = prefix = await Guild.get_prefix(
                    self._db,
                    guild.id,
                    default_prefix,
                )
        return [
            prefix + " ", prefix,
            f'<@{self.user.id}> ',
            f'<@!{self.user.id}> ',
            f'<@{self.user.id}>',
            f'<@!{self.user.id}>',
        ]

    async def on_command_error(
            self,
            context: commands.Context,
            exception: commands.CommandError, /) -> None:
        data = error_handler(exception, self._settings["debug"])
        if data is None:
            return
        time, embed = data
        await context.reply(embed=embed, delete_after=time)

    async def on_app_command_error(
            self,
            inter: discord.Interaction,
            exc: app_commands.AppCommandError):

        data = error_handler(exc, self._settings["debug"])
        if data is None:
            return
        time, embed = data
        if inter.response.is_done():
            await inter.followup.send(embed=embed, delete_after=time)
        else:
            await inter.response.send_message(embed=embed, delete_after=time)

    def add_hidden_app_command(self, command: supported_app_commands):
        self.tree.add_command(command, guild=self._settings["main_guild"])

    def add_app_command(self, command: supported_app_commands):
        self.tree.add_command(command)

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{self._settings['default_prefix']} help"))
        print("ready")

    @staticmethod
    async def on_connect():
        print("connected")

    @staticmethod
    async def on_disconnect():
        print("disconnected")

    @staticmethod
    async def on_resumed():
        print("resumed")

    @property
    def settings(self) -> dict[str, ...]:
        return self._settings

    @property
    def db(self):
        return self._db

    @property
    def topic_manger(self) -> TopicManager:
        return self._topic_manager
