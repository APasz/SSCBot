import logging
import os

from config import botInformation as botInfo
from config import generalEventConfig as geConfig
from config import genericConfig as gxConfig
from config import screenShotCompConfig as sscConfig
from config import syncCommands
from util.fileUtil import cacheWrite, parentDir, writeJSON
from util.genUtil import blacklistCheck

print("CogBotManage")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY BOT_MANAGE IMPORT MODULES")
    import nextcord
    from discord import Permissions
    from nextcord import Interaction, SlashOption, slash_command
    from nextcord.ext import commands
except Exception:  # pylint: disable=broad-except
    logSys.exception("BOT_MANAGE IMPORT MODULES")


class botManage(commands.Cog, name="BotManagement"):
    """Class containing commands and functions related to the management of the bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logSys.debug(f"{self.__cog_name__} Ready")

    @commands.command(name="reload", aliases=["rl"], hidden=True)
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, extension):
        """Reloads a specific cog"""
        logSys.debug(ctx.author.id)
        try:
            self.bot.reload_extension(f"cogs.{extension}")
        except Exception:
            try:
                await ctx.send(f"**{extension}** can't be reloaded.")
            except Exception:
                logSys.exception(f"Cog Reload")
            logSys.exception(f"{extension} can't be reloaded")
        else:
            await ctx.send(f"**{extension}** successfully reloaded.")

    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def load(self, ctx: commands.Context, extension):
        """Loads a specific cog"""
        logSys.debug(ctx.author.id)
        if extension.lower() == "config":
            path = f"{extension}"
        else:
            path = f"cogs.{extension}"
        try:
            self.bot.load_extension(path)
        except Exception:
            try:
                await ctx.send(f"**{extension}** can't be loaded.")
            except Exception:
                logSys.exception(f"Cog Load")
            logSys.warning(f"{extension} can't be loaded")
        else:
            await ctx.send(f"**{extension}** successfully loaded.")

    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, extension):
        """Unloads a specific cog"""
        logSys.debug(ctx.author.id)
        try:
            self.bot.unload_extension(f"cogs.{extension}")
        except Exception:
            try:
                await ctx.send(f"**{extension}** can't be unloaded.")
            except Exception:
                logSys.exception(f"Unload Cog")
            logSys.exception(f"{extension} can't be unloaded")
        else:
            await ctx.send(f"**{extension}** successfully unloaded.")

    @commands.command(name="reloadAll", hidden=True)
    @commands.is_owner()
    async def reloadAll(self, ctx: commands.Context):
        """Reloads all cogs"""
        logSys.debug(ctx.author.id)
        cogsDir = os.path.join(parentDir(), "cogs")
        try:
            for filename in os.listdir(cogsDir):
                if filename.endswith(".py") and filename != "__init__.py":
                    self.bot.reload_extension(f"cogs.{filename[:-3]}")
            logSys.info("All cogs reloaded")
        except Exception:
            try:
                await ctx.send("Cogs can't be reloaded.")
            except Exception:
                logSys.exception(f"Cogs reload")
            logSys.exception("Cogs can't be reloaded")
        else:
            try:
                await ctx.send("All cogs successfully reloaded.")
            except Exception:
                logSys.exception(f"All Cogs Reloaded")

    @commands.command(name="toggle")
    @commands.has_permissions(administrator=True)
    async def toggle(self, ctx: commands.Context, comm=None):
        """Toggles a command. Must be Admin"""
        if not await blacklistCheck(ctx=ctx, blklstType="gen"):
            return
        logSys.debug(ctx.author.id)
        if comm is not None:
            command = self.bot.get_command(comm)
            logSys.info(f"{comm}: {command.enabled} | {ctx.author.id}")
            if command.enabled:
                command.enabled = False
                logSys.warning(command.enabled)
            elif not command.enabled:
                command.enabled = True
                logSys.warning(command.enabled)
            logSys.info(f"{comm}: {command.enabled}")
            await ctx.send(f"{comm.title()} command toggled")
        else:
            try:
                await ctx.send("Command not found")
            except Exception:
                # this should probably check the list of commands...
                logSys.exception(f"Toggle: Command Missing")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def _config(self, ctx: commands.Context, arg: str):
        logSys.debug(f"{arg=}")
        err = False
        if "-c" in arg:
            logSys.info("Writing JSON Cache")
            try:
                cacheWrite()
            except Exception:
                logSys.exception(f"_config dump cacheJSON")

        elif "-d" in arg:
            dumpPath = os.path.join(parentDir(), "dump")
            try:
                os.remove(dumpPath)
            except Exception:
                logSys.exception(f"Delete Dump Folder")
            try:
                os.mkdir(dumpPath)
            except Exception:
                logSys.exception(f"Make Dump Folder")
            logSys.info("Dumping genericConfig")
            try:
                dataGX = str(gxConfig.__dict__)
                writeJSON(data=dataGX, filename="GX", directory=["dump"])
            except Exception:
                logSys.exception(f"Dumping genericConfig")
                err = True
            logSys.info("Dumping screenShotCompConfig")
            try:
                dataSSC = str(sscConfig.__dict__)
                writeJSON(data=dataSSC, filename="SSC", directory=["dump"])
            except Exception:
                logSys.exception(f"Dumping screenShotCompConfig")
                err = True
            logSys.info("Dumping generalEventConfig")
            try:
                dataGE = str(geConfig.__dict__)
                writeJSON(data=dataGE, filename="GE", directory=["dump"])
            except Exception:
                logSys.exception(f"Dumping generalEventConfig")
                err = True
            logSys.info("Dumping botInformation")
            try:
                dataBI = str(botInfo.__dict__)
                writeJSON(data=dataBI, filename="BI", directory=["dump"])
            except Exception:
                logSys.exception(f"Dumping botInformation")
                err = True
            logSys.info("Dumping AutoReact")
            try:
                dataAR = (
                    str(geConfig.autoReacts) + "\n\n\n" + str(geConfig.autoReactsChans)
                )
                writeJSON(data=dataAR, filename="AR", directory=["dump"])
            except Exception:
                logSys.exception(f"Dumping AutoReact")
                err = True

        elif "-u" in arg:
            logSys.info("Reload genericConfig")
            try:
                gxConfig.update()
            except Exception:
                logSys.exception(f"Reload Configuration")
                err = True
            logSys.info("Reload screenShotCompConfig")
            try:
                sscConfig.update()
            except Exception:
                logSys.exception(f"Reload screenShotCompConfig")
                err = True
            logSys.info("Reload generalEventConfig")
            try:
                geConfig.update()
            except Exception:
                logSys.exception(f"Reload generalEventConfig")
                err = True
            logSys.info("Reload botInformation")
            try:
                botInfo.update()
            except Exception:
                logSys.exception(f"Reload botInformation")
                err = True

        elif "-s" in arg:
            if not await syncCommands(self.bot):
                err = False

        else:
            await ctx.send("Arg not recognised!")
            return
        logSys.debug(f"{err=}")
        if err:
            await ctx.send("Error!")
        else:
            await ctx.send("Success!")

    @slash_command(
        name="editbot",
        guild_ids=gxConfig.slashServers,
        default_member_permissions=Permissions(administrator=True),
    )
    async def editbot(
        self,
        interaction: Interaction,
        pfp: nextcord.Attachment = None,
        name: str = None,
    ):
        """Update pfp or name of the bot user. Owner Only"""
        if interaction.user.id != gxConfig.ownerID:
            try:
                interaction.send(
                    "This command is restricted to the bot owner.", ephemeral=True
                )
            except Exception:
                logSys.exception(f"/Command Restricted to Owner EditBot")
            return
        logSys.info(f"pfp {type(pfp)}, {name=}")
        if not pfp or not name:
            try:
                await interaction.send("Nah bro")
            except Exception:
                logSys.exception(f"EditBot")
            return
        if pfp:
            try:
                await self.bot.user.edit(avatar=pfp)
            except Exception:
                logSys.exception("Edit Bot Avatar")
            logSys.info("pfp updated")
        if name:
            try:
                await self.bot.user.edit(username=name)
            except Exception:
                logSys.exception("Edit Bot Name")
            logSys.info("name updated")
        try:
            await interaction.send("Done!", ephemeral=True)
        except Exception:
            logSys.exception(f"EditBot Done")


def setup(bot: commands.Bot):
    bot.add_cog(botManage(bot))


# MIT APasz
