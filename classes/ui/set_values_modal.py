from typing import TYPE_CHECKING

import discord

from classes.collections import Question, Topic

if TYPE_CHECKING:
    from classes.bot import Bot
    from .create_question_view import CreateQuestionView


class SetValueModal(discord.ui.Modal):
    title = "لطفا موارد زیر را تکمیل کنید"
    topic = discord.ui.TextInput(
        label="لطفا موضوع سوال را وارد کنید",
        placeholder="موضوع سوال شما",
        default="general",
        required=False,
        min_length=3,
        max_length=35,
    )
    content = discord.ui.TextInput(
        label="متن سوال",
        style=discord.TextStyle.paragraph,
        placeholder="محتوای سوال شما",
        min_length=10,
        max_length=4000,
    )
    complete_answer = discord.ui.TextInput(
        label="لطفا جواب کامل سوال را وارد کنید",
        style=discord.TextStyle.long,
        placeholder="جواب کامل سوال شما",
        required=False,
        min_length=10,
        max_length=4000,
    )

    def __init__(self, question: Question, view: "CreateQuestionView",
                 bot: "Bot"):
        super(SetValueModal, self).__init__(timeout=300)

        self._question: Question = question
        self._view: "CreateQuestionView" = view
        self._bot: "Bot" = bot
        self.content.default = question.content
        self.complete_answer.default = question.complete_answer
        if self._view.topic:
            self.topic.default = self._view.topic.name

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        await interaction.response.defer()

        self._question.content = self.content.value
        self._question.complete_answer = self.complete_answer.value or None

        topic: Topic | None = await Topic.get_by_name(
            self._bot, self.topic.value)
        if topic is None and not (
                not self.topic.value or self.topic.value == "general"):
            await interaction.followup.send(
                "موضوع مورد نظر شما در سیستم ثبت نشده است"
                "\nشما میتوانید با استفاده از کامند `get_all_topics` به تمامیه موضوعات داخل سیستم دسترسی داشته باشید",
                ephemeral=True
            )
        else:
            self._view.topic = topic
        self._view.set_values.label = "تغییر مقدایر"
        self._view.set_values.style = discord.ButtonStyle.success
        if self._view.set_options.disabled:
            self._view.submit.disabled = False
        await interaction.followup.edit_message(
            interaction.message.id,
            view=self._view,
            embed=self._question.preview(
                self._view.options,
                getattr(self._view.topic, "name", "general"),
                self._view.correct_option
            ),
        )
