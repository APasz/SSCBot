import logging
import os

from config import botInformation as botInfo
from config import generalEventConfig as geConfig
from config import genericConfig as gxConfig
from config import screenShotCompConfig as sscConfig
from util.fileUtil import cacheWrite, parentDir, writeJSON
from util.genUtil import blacklistCheck

print("CogBotManage")

log = logging.getLogger("discordGeneral")
try:
    log.debug("TRY BOT_MANAGE IMPORT MODULES")
    import nextcord
    from discord import Permissions
    from nextcord import Interaction, SlashOption, slash_command
    from nextcord.ext import commands
except Exception:
    log.exception("BOT_MANAGE IMPORT MODULES")


class botManage(commands.Cog, name="BotManagement"):
    """Class containing commands and functions related to the management of the bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.debug(f"{self.__cog_name__} Ready")

    @commands.command(name="reload", aliases=["rl"], hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension):
        """Reloads a specific cog"""
        log.debug(ctx.author.id)
        try:
            self.bot.reload_extension(f"cogs.{extension}")
        except Exception:
            try:
                await ctx.send(f"**{extension}** can't be reloaded.")
            except Exception:
                log.exception(f"Cog Reload")
            log.exception(f"{extension} can't be reloaded")
        else:
            await ctx.send(f"**{extension}** successfully reloaded.")

    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension):
        """Loads a specific cog"""
        log.debug(ctx.author.id)
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
                log.exception(f"Cog Load")
            log.warning(f"{extension} can't be loaded")
        else:
            await ctx.send(f"**{extension}** successfully loaded.")

    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension):
        """Unloads a specific cog"""
        log.debug(ctx.author.id)
        try:
            self.bot.unload_extension(f"cogs.{extension}")
        except Exception:
            try:
                await ctx.send(f"**{extension}** can't be unloaded.")
            except Exception:
                log.exception(f"Unload Cog")
            log.exception(f"{extension} can't be unloaded")
        else:
            await ctx.send(f"**{extension}** successfully unloaded.")

    @commands.command(name="reloadAll", hidden=True)
    @commands.is_owner()
    async def reloadAll(self, ctx):
        """Reloads all cogs"""
        log.debug(ctx.author.id)
        cogsDir = os.path.join(parentDir(), "cogs")
        try:
            for filename in os.listdir(cogsDir):
                if filename.endswith(".py") and filename != "__init__.py":
                    self.bot.reload_extension(f"cogs.{filename[:-3]}")
            log.info("All cogs reloaded")
        except Exception:
            try:
                await ctx.send("Cogs can't be reloaded.")
            except Exception:
                log.exception(f"Cogs reload")
            log.exception("Cogs can't be reloaded")
        else:
            try:
                await ctx.send("All cogs successfully reloaded.")
            except Exception:
                log.exception(f"All Cogs Reloaded")

    @commands.command(name="toggle")
    @commands.has_permissions(administrator=True)
    async def toggle(self, ctx, comm=None):
        """Toggles a command. Must be Admin"""
        if not await blacklistCheck(ctx=ctx, blklstType="gen"):
            return
        log.debug(ctx.author.id)
        if comm != None:
            command = self.bot.get_command(comm)
            log.info(f"{comm}: {command.enabled} | {ctx.author.id}")
            if command.enabled == True:
                command.enabled = False
                log.warning(command.enabled)
            elif command.enabled == False:
                command.enabled = True
                log.warning(command.enabled)
            log.info(f"{comm}: {command.enabled}")
            await ctx.send(f"{comm.title()} command toggled")
        else:
            try:
                await ctx.send("Command not found")
            except Exception:
                # this should probably check the list of commands...
                log.exception(f"Toggle Command Missing")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def _config(self, ctx, dump: str = None):
        log.debug(f"{dump=}")
        err = False
        if "-c" in dump:
            log.info("Writing JSON Cache")
            try:
                cacheWrite()
            except Exception:
                log.exception(f"_config dump cacheJSON")
        elif "-d" in dump:
            dumpPath = os.path.join(parentDir(), "dump")
            try:
                os.mkdir(dumpPath)
            except FileExistsError:
                pass
            except Exception:
                log.exception(f"Make Dump Folder")
            log.info("Dumping genericConfig")
            try:
                dataGX = str(gxConfig.__dict__)
                writeJSON(data=dataGX, filename="GX", directory=["dump"])
            except Exception:
                log.exception(f"Dumping genericConfig")
                err = True
            log.info("Dumping screenShotCompConfig")
            try:
                dataSSC = str(sscConfig.__dict__)
                writeJSON(data=dataSSC, filename="SSC", directory=["dump"])
            except Exception:
                log.exception(f"Dumping screenShotCompConfig")
                err = True
            log.info("Dumping generalEventConfig")
            try:
                dataGE = str(geConfig.__dict__)
                writeJSON(data=dataGE, filename="GE", directory=["dump"])
            except Exception:
                log.exception(f"Dumping generalEventConfig")
                err = True
            log.info("Dumping botInformation")
            try:
                dataBI = str(botInfo.__dict__)
                writeJSON(data=dataBI, filename="BI", directory=["dump"])
            except Exception:
                log.exception(f"Dumping botInformation")
                err = True
        elif "-u" in dump:
            log.info("Reload genericConfig")
            try:
                gxConfig.update()
            except Exception:
                log.exception(f"Reload Configuration")
                err = True
            log.info("Reload screenShotCompConfig")
            try:
                sscConfig.update()
            except Exception:
                log.exception(f"Reload screenShotCompConfig")
                err = True
            log.info("Reload generalEventConfig")
            try:
                geConfig.update()
            except Exception:
                log.exception(f"Reload generalEventConfig")
                err = True
            log.info("Reload botInformation")
            try:
                botInfo.update()
            except Exception:
                log.exception(f"Reload botInformation")
                err = True
        else:
            await ctx.send("Arg not recognised!")
            return
        log.debug(f"{err=}")
        if err:
            await ctx.send("Error!")
        else:
            await ctx.send("Success!")

    @slash_command(name="editbot", guild_ids=gxConfig.slashServers,
                   default_member_permissions=Permissions(administrator=True))
    async def editbot(self, interaction: Interaction,
                      pfp: nextcord.Attachment = None, name: str = None,):
        """Update pfp or name of the bot user. Owner Only"""
        if interaction.user.id != gxConfig.ownerID:
            try:
                interaction.send(
                    "This command is restricted to the bot owner.", ephemeral=True)
            except Exception:
                log.exception(f"/Command Restricted to Owner EditBot")
            return
        log.info(f"pfp {type(pfp)}, {name=}")
        if pfp or name:
            if pfp:
                try:
                    await self.bot.user.edit(avatar=pfp)
                except Exception:
                    log.exception("Edit Bot Avatar")
                log.info("pfp updated")
            elif name:
                try:
                    await self.bot.user.edit(username=name)
                except Exception:
                    log.exception("Edit Bot Name")
                log.info("name updated")
        else:
            try:
                await interaction.send("Nah bro")
            except Exception:
                log.exception(f"EditBot")
            return
        try:
            await interaction.send("Done!", ephemeral=True)
        except Exception:
            log.exception(f"EditBot Done")


def setup(bot: commands.Bot):
    bot.add_cog(botManage(bot))


# MIT APasz
