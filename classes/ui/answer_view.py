from typing import TYPE_CHECKING
import discord

if TYPE_CHECKING:
    from classes.collections import Account, Option

    from classes.bot import Bot
    from bson import ObjectId


class AnswerView(discord.ui.View):
    def __init__(
            self,
            participant: "Account",
            bot: "Bot",
            channel: discord.abc.Messageable,
            correct_index: int,
            complete_answer: str,
            options: list["Option"],
            *,
            timeout: float | None = 30.):
        self._channel: discord.abc.Messageable = channel
        self._participant: "Account" = participant
        self._bot: "Bot" = bot
        self._correct_index: int = correct_index
        self._complete_answer: str = complete_answer
        self._options: list["Option"] = options
        self.fallback: ObjectId | None = None
        super(AnswerView, self).__init__(timeout=timeout)

    async def _check_option(
            self,
            interaction: discord.Interaction,
            selected: int):
        if interaction.user.id != self._participant.discord_id:
            await interaction.response.send_message(
                "شما نمیتوانید به سوال شخص دیگری پاسخ دهید\nلطفا با استفاده از اسلش کامند ask از خودتان سوال بپرسید",
                ephemeral=True)
            return
        await interaction.response.defer()
        self.fallback = self._options[selected].id
        if selected == self._correct_index:
            await interaction.followup.send(embed=discord.Embed(
                title="جواب شما درست است ✅",
                description=f"گزینه صحیح: {self._correct_index + 1}"
                            f"\n{self._complete_answer}",
                color=0x00ff00))
        else:
            await interaction.followup.send(embed=discord.Embed(
                title="جواب شما نادرست است ❌",
                description=f"گزینه صحیح: {self._correct_index + 1}"
                            f"\n{self._complete_answer}",
                color=0xff0000))
        self.stop()

    @discord.ui.button(label="گزینه", style=discord.ButtonStyle.primary,
                       emoji='1️⃣')
    async def option1(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        await self._check_option(interaction, 0)

    @discord.ui.button(label="گزینه", style=discord.ButtonStyle.primary,
                       emoji="2️⃣")
    async def option2(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        await self._check_option(interaction, 1)

    @discord.ui.button(label="گزینه", style=discord.ButtonStyle.primary,
                       emoji="3️⃣")
    async def option3(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        await self._check_option(interaction, 2)

    @discord.ui.button(label="گزینه", style=discord.ButtonStyle.primary,
                       emoji="4️⃣")
    async def option4(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        await self._check_option(interaction, 3)

    @discord.ui.button(label="بلد نیستم", style=discord.ButtonStyle.secondary,
                       emoji='😵')
    async def idk(self, interaction: discord.Interaction,
                  button: discord.ui.Button):
        if interaction.user.id != self._participant.discord_id:
            await interaction.response.send_message(
                "شما نمیتوانید به سوال شخص دیگری پاسخ دهید"
                "\nلطفا با استفاده از کامند ask از خودتان سوال بپرسید",
                ephemeral=True)
            return
        await interaction.response.send_message(embed=discord.Embed(
            title="سوال با موفقیت کنسل شد 🤓",
            description=f"گزینه صحیح: {self._correct_index + 1}"
                        f"\n{self._complete_answer}",
            color=0x888888
        ))
        self.stop()

    async def on_timeout(self):
        await self._channel.send(embed=discord.Embed(
            title="زمان شما به اتمام رسیده است ⏰",
            description=f"گزینه صحیح: {self._correct_index + 1}"
                        f"\n{self._complete_answer}",
            color=0x0000ff))
