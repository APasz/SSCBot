import logging

print("CogSuggestions")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY SUGGESTIONS IMPORT MODUELS")
    import nextcord
    from discord import SlashOption
    from nextcord.ext import commands

    from config import genericConfig as gxConfig
except Exception:
    logSys.exception("SUGGESTIONS IMPORT MODUELS")


class suggModal(nextcord.ui.Modal):
    """Suggestion modal"""

    def __init__(self, suggTitle, nameLabel, descLabel):
        super().__init__(
            title=suggTitle,
            timeout=30 * 60,
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
        owner = interaction.guild.get_member(gxConfig.ownerID)
        try:
            await owner.send(txt)
        except Exception:
            log.exception(f"Sugg")


class suggCOMM(commands.Cog, description="Trigger Modal"):
    """Suggestion command to trigger the suggestion modal."""

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="suggest",
        description="Trigger a form modal where you can explain your suggestion. Currently sent to APasz",
        guild_ids=gxConfig.slashServers,
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

        await interaction.response.send_modal(
            modal=suggModal(
                suggTitle=modalTitle, nameLabel=nameLabel, descLabel=descLabel
            )
        )


def setup(bot: commands.Bot):
    bot.add_cog(suggCOMM(bot))


# MIT APasz
