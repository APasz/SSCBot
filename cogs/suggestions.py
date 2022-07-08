print("CogSuggestions")
import logging

from discord import SlashOption

from config import genericConfig
import nextcord
from nextcord.ext import commands

log = logging.getLogger("discordGeneral")


class suggModal(nextcord.ui.Modal):
    def __init__(self, suggTitle, nameLabel, descLabel):
        super().__init__(
            title=suggTitle,
            timeout=5 * 60,
        )
        self.name = nextcord.ui.TextInput(
            label=nameLabel,
            min_length=3,
            max_length=75,
        )
        self.add_item(self.name)

        self.description = nextcord.ui.TextInput(
            label="Description",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Describe with as much detail as possible.",
            required=False,
            max_length=1000,
        )
        self.add_item(self.description)

    async def callback(self, interaction: nextcord.Interaction):
        txt = f"User suggestion: {self.name.value}\n{self.description.value}\n\n{interaction.user.id}"
        log.info(txt)
        owner = interaction.guild.get_member(genericConfig.ownerID)
        await owner.send(txt)


class suggCOMM(commands.Cog, description="Trigger Modal"):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="suggest",
        description="Trigger a form modal where you can explain your suggestion. Currently sent to APasz",
        guild_ids=genericConfig.slashServers,
    )
    async def send(
        self,
        interaction: nextcord.Interaction,
        modalTitle: str = SlashOption(
            name="type",
            required=True,
            description="What sort of suggestion do you want to make?",
            choices={
                "Bot Suggestion": "Bot Suggestion",
                "Server Suggestion": "Server Suggestion",
            },
        ),
    ):
        """Makes suggestion modal"""
        if "Bot Suggestion" == modalTitle:
            nameLabel = "Your Suggestion?"
            descLabel = "What sort of suggestion do you want to make?"
        elif "Server Suggestion" == modalTitle:
            nameLabel = "Your Suggestion?"
            descLabel = "What sort of suggestion do you want to make?"

        data = await interaction.response.send_modal(
            modal=suggModal(
                suggTitle=modalTitle, nameLabel=nameLabel, descLabel=descLabel
            )
        )


def setup(bot: commands.Bot):
    bot.add_cog(suggCOMM(bot))


# "Mod Request": "Mod Request",
# "Game Request **Not in Use**": "Game Request",

# elif "Mod Request" == modalTitle:
# 	nameLabel = "What"
# elif "Game Request" == modalTitle:
# 	nameLabel = None

# MIT APasz
