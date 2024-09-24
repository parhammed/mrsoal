import discord


class Paginator(discord.ui.View):
    def __init__(
            self,
            embed: discord.Embed,
            items: list[tuple[str, str]],
            index: int = 0, inline=False
    ):
        super(Paginator, self).__init__(timeout=500)
        self._base_embed = embed.copy()
        self.embed = embed.copy()
        self._items = items
        self._index = index
        self._inline = inline
        self._last_page = (len(items) - 1) // 20

        self.update()

    def update(self):
        self.first.disabled = self.back.disabled = self._index <= 0
        self.last.disabled = self.forward.disabled = self._index >= self._last_page
        self.embed = self._base_embed.copy()
        for item in self._items[(self._index - 1) * 20:self._index * 20]:
            self.embed.add_field(name=item[0], value=item[1], inline=False)

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji='⏮')
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._index = 0
        self.update()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji='◀️')
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._index -= 1
        self.update()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji='▶️')
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._index += 1
        self.update()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji='⏭')
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._index = self._last_page
        self.update()
        await interaction.response.edit_message(embed=self.embed, view=self)
