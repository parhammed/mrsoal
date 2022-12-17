from typing import TYPE_CHECKING
import discord
from classes.collections import Question, Account, Topic, Option
from .set_values_modal import SetValueModal
from .set_options_modal import SetOptionsModal
from .get_option_modal import GetOptionModal

if TYPE_CHECKING:
    from classes.bot import Bot


class CreateQuestionView(discord.ui.View):
    def __init__(self, maker: Account, bot: "Bot", *,
                 timeout=900):
        self._question = Question(bot, maker_id=maker.id, is_active=False)
        self.options = ["", "", ""]
        self.topic: Topic | None = None
        self.correct_option = ""
        self._bot: "Bot" = bot
        self._maker = maker
        self._message: discord.Message | None = None
        super(CreateQuestionView, self).__init__(timeout=timeout)

    async def set_message(self, message: discord.Message):
        self._message = message
        await message.edit(
            content="",
            embed=self._question.preview(
                self.options,
                getattr(self.topic, "name", "general"),
                self.correct_option), view=self)

    @discord.ui.button(
        label="ارسال",
        style=discord.ButtonStyle.success,
        disabled=True,
        row=3
    )
    async def submit(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        if self._maker.discord_id != interaction.user.id:
            await interaction.response.send_message(
                "این عملیات برای شخص دیگری فعال شده است",
                ephemeral=True
            )
            return
        await interaction.response.defer()
        self._question.topic_id = getattr(self.topic, "id", None)
        await self._question.save()
        await self._bot.db[Option.__collection_name__].insert_many((
            Option(
                self._bot,
                content=self.correct_option,
                is_correct=True,
                question_id=self._question.id
            ).to_data(),
            *(
                Option(
                    self._bot,
                    content=option,
                    is_correct=False,
                    question_id=self._question.id
                ).to_data() for option in self.options)
        ))
        channel = self._bot.get_channel(
            self._bot.settings['question_query_channel'])
        await channel.send(
            f"کد سوال: {self._question.id}",
            embed=self._question.preview(
                self.options,
                getattr(self.topic, "name", "general"),
                self.correct_option)
        )
        await interaction.followup.send(
            f"سوال شما با موفقیت در لیست انتطار تائید قرار گرفت (کد سوال جهت پیگیری: {self._question.id}) ",
            ephemeral=True)
        await self.stop()

    @discord.ui.button(
        label="مقدار دهی گزینه ها",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def set_options(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if self._maker.discord_id != interaction.user.id:
            await interaction.response.send_message(
                "این عملیات برای شخص دیگری فعال شده است", ephemeral=True)
            return
        await interaction.response.send_modal(
            SetOptionsModal(self._question, self))

    @discord.ui.button(
        label="اضافه کردن گزینه",
        style=discord.ButtonStyle.primary,
        disabled=True,
        row=1
    )
    async def add_option(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        if self._maker.discord_id != interaction.user.id:
            await interaction.response.send_message(
                "این عملیات برای شخص دیگری فعال شده است", ephemeral=True)
            return
        await interaction.response.send_modal(
            GetOptionModal(len(self.options), self._question, self))

    @discord.ui.button(
        label="حذف آخرین گزینه",
        style=discord.ButtonStyle.primary,
        disabled=True,
        row=1
    )
    async def remove_option(self, interaction: discord.Interaction,
                            button: discord.ui.Button):
        if self._maker.discord_id != interaction.user.id:
            await interaction.response.send_message(
                "این عملیات برای شخص دیگری فعال شده است", ephemeral=True)
            return
        await interaction.response.defer()
        self.options.pop()
        self.change_option.options.pop()
        if self.add_option.disabled:
            self.add_option.disabled = False
        if len(self.options) <= 3:
            button.disabled = True
        await interaction.message.edit(
            embed=self._question.preview(
                self.options,
                getattr(self.topic, "name", "general"),
                self.correct_option), view=self)

    @discord.ui.select(
        placeholder="یک گزینه را برای تغییر انتخاب کنید",
        min_values=1,
        max_values=1,
        row=2,
        options=[
            discord.SelectOption(label="گزینه صحیح", value="correct"),
            discord.SelectOption(label="گزینه دوم", value="0"),
            discord.SelectOption(label="گزینه سوم", value="1"),
            discord.SelectOption(label="گزینه چهارم", value="2"),
        ],
        disabled=True)
    async def change_option(self, interaction: discord.Interaction,
                            select: discord.ui.Select):
        if self._maker.discord_id != interaction.user.id:
            await interaction.response.send_message(
                "این عملیات برای شخص دیگری فعال شده است",
                ephemeral=True
            )
            return
        await interaction.response.send_modal(
            GetOptionModal(int(select.values[0]), self._question, self))

    @discord.ui.button(label="مقدار دهی", style=discord.ButtonStyle.danger)
    async def set_values(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        if self._maker.discord_id != interaction.user.id:
            await interaction.response.send_message(
                "این عملیات برای شخص دیگری فعال شده است",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            SetValueModal(self._question, self, self._bot))

    @discord.ui.button(
        label="تغییر حالت اسپویل",
        style=discord.ButtonStyle.primary)
    async def change_is_spoiler(self, interaction: discord.Interaction,
                                button: discord.ui.Button):
        if self._maker.discord_id != interaction.user.id:
            await interaction.response.send_message(
                "این عملیات برای شخص دیگری فعال شده است", ephemeral=True)
            return
        self._question.is_spoiler = not self._question.is_spoiler
        await interaction.response.edit_message(
            embed=self._question.preview(self.options,
                                         getattr(self.topic, "name", "general"),
                                         self.correct_option), view=self)

    @discord.ui.button(label="تغییر حالت نمایش اسم",
                       style=discord.ButtonStyle.primary)
    async def change_is_maker_hidden(self, interaction: discord.Interaction,
                                     button: discord.ui.Button):
        if self._maker.discord_id != interaction.user.id:
            await interaction.response.send_message(
                "این عملیات برای شخص دیگری فعال شده است", ephemeral=True)
            return
        self._question.is_maker_hidden = not self._question.is_maker_hidden
        await interaction.response.edit_message(
            embed=self._question.preview(
                self.options,
                getattr(self.topic, "name", "general"),
                self.correct_option),
            view=self
        )

    @discord.ui.button(label="لغو", style=discord.ButtonStyle.danger, row=3)
    async def cancel(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        if self._maker.discord_id != interaction.user.id:
            await interaction.response.send_message(
                "این عملیات برای شخص دیگری فعال شده است", ephemeral=True)
            return

        if interaction.message.flags.ephemeral:
            await interaction.response.edit_message(
                content="عملیات با موفقیت لغو شد",
                view=None,
                embed=None
            )
        else:
            await interaction.response.send_message("عملیات با موفقیت لغو شد",
                                                    ephemeral=True)
        await self.stop()

    @discord.ui.button(label="راهنما", style=discord.ButtonStyle.secondary,
                       row=3)
    async def help(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
        await interaction.response.send_message(
            "لطفا قبل تنظیم کردن موضوع از وجود داشتن آن موضوع در سیستم با دستور `get_all_topics` مطمئن شوید"
            "\nسازنده سوال آیدی شماست برای نمایش و پیگیری سوال"
            "\nمنظور از جواب کامل سوال متنی است که بعد از جواب دادن به سوال برای اینکه کاربر متوجه اشتباه خودش شود نمایش داده میشود"
            "\nگزینه ها به اینصورت انتخاب میشود که ابتدا 3 گزینه غلط از بین تمامی گزینه های غلط بصورت رندوم انتخاب میشود سپس گزینه صحیح بصورت رندوم در کنار یا بین سوال های غلط قرار میگیرد"
            "\n"
            "\nنکته: در سوال خود به هیچ عنوان از '|' برای اسپویلر زدن به سوال خود استفاده نکنید بجاش از دکمه 'تغییر حالت اسپویل' استفاده کنید"
            "\n"
            "\nتمامی سوال های ثبت شده توسط کاربر ابتدا توسط ادمین ها اصلاح میشوند سپس در سیستم بصورت کامل ثبت میشود",
            ephemeral=True)

    async def stop(self):
        if not self._message.flags.ephemeral:
            await self._message.delete()
        super(CreateQuestionView, self).stop()

    async def on_timeout(self) -> None:
        await self.stop()
