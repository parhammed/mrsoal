from typing import TYPE_CHECKING
import discord
from utils import numbers, get

if TYPE_CHECKING:
    from classes.collections import Question
    from .create_question_view import CreateQuestionView


class GetOptionModal(discord.ui.Modal):
    """get text of option from user"""
    option = discord.ui.TextInput(label="", max_length=2000)

    def __init__(self, index, question: "Question", view: "CreateQuestionView"):
        number = "صحیح" if index == -1 else numbers[index + 2]
        super(GetOptionModal, self).__init__(
            title=f"لطفا گزینه {number} سوال را وارد کنید",
            timeout=300
        )

        self.option.label = f"لطفا گزینه {number} سوال را وارد کنید"
        self.option.placeholder = f"گزینه {number}"
        self.option.default = get(view.options, index, "")

        self._index = index
        self._question: "Question" = question
        self._view: "CreateQuestionView" = view

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        await interaction.response.defer()
        if self._index == -1:
            self._view.correct_option = self.option.value

        elif self._index < len(self._view.options):
            self._view.options[self._index] = self.option.value

        else:
            self._view.options.append(self.option.value)
            self._view.change_option.options.append(
                discord.SelectOption(label=f"گزینه {numbers[self._index + 2]}",
                                     value=str(self._index)))
            if self._view.remove_option.disabled:
                self._view.remove_option.disabled = False
            if len(self._view.options) >= 10:
                self._view.add_option.disabled = True

        await interaction.followup.edit_message(
            interaction.message.id,
            view=self._view,
            embed=self._question.preview(
                self._view.options,
                getattr(self._view.topic,
                        "name", "general"),
                self._view.correct_option)
        )
