from typing import TYPE_CHECKING
import discord

if TYPE_CHECKING:
    from classes.collections import Question
    from .create_question_view import CreateQuestionView


class SetOptionsModal(discord.ui.Modal):
    """get initial information from user"""
    title = "لطفا گزینه های سوال را وارد کنید"

    correct = discord.ui.TextInput(
        label="لطفا گزینه صحیح را وارد کنید",
        placeholder="گزینه صحیح",
        max_length=2000
    )
    incorrect1 = discord.ui.TextInput(
        label="لطفا گزینه دوم را وارد کنید",
        placeholder="گزینه دوم",
        max_length=2000
    )
    incorrect2 = discord.ui.TextInput(
        label="لطفا گزینه سوم را وارد کنید",
        placeholder="گزینه سوم",
        max_length=2000
    )
    incorrect3 = discord.ui.TextInput(
        label="لطفا گزینه چهارم را وارد کنید",
        placeholder="گزینه چهارم سوال",
        max_length=2000
    )

    def __init__(self, question: "Question", view: "CreateQuestionView"):
        super(SetOptionsModal, self).__init__(timeout=300)

        self._question: "Question" = question
        self._view: "CreateQuestionView" = view

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        await interaction.response.defer()
        self._view.correct_option = self.correct.value
        self._view.options[0] = self.incorrect1.value
        self._view.options[1] = self.incorrect2.value
        self._view.options[2] = self.incorrect3.value
        self._view.set_options.style = discord.ButtonStyle.success
        self._view.set_options.disabled = True
        self._view.add_option.disabled = False
        self._view.change_option.disabled = False
        if self._view.set_values.style == discord.ButtonStyle.success:
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
