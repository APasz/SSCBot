import logging

print("CogBotManage")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY BOT_MANAGE IMPORT MODULES")
    import nextcord
    from discord import Permissions
    from nextcord import Interaction, slash_command
    from nextcord.ext import commands
    from json import dumps as jdumps
    from shutil import rmtree

    from config import botInformation as botInfo
    from config import generalEventConfig as geConfig
    from config import genericConfig as gxConfig
    from config import localeConfig as lcConfig
    from config import screenShotCompConfig as sscConfig
    from config import syncCommands
    from util.fileUtil import cacheWrite, paths, writeJSON
    from util.genUtil import blacklistCheck
except Exception:
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
            logSys.exception("Cog Reload")
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
            logSys.exception("Cog Load")
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
            logSys.exception("Cog Unload")
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
        cogsDir = gxConfig.botDir.joinpath("cogs")
        try:
            for file in cogsDir.iterdir():
                if file.name.endswith(".py") and not file.name.startswith("__"):
                    try:
                        self.bot.reload_extension(f"cogs.{file.stem}")
                    except Exception:
                        log.exception(f"Cog Reload All")
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

            try:
                rmtree(paths.dump)
                paths.dump.mkdir()
            except Exception:
                logSys.exception(f"Dump Folder")

            def dicify(var):
                newVar = {}
                for key, val in var.items():
                    if not key.startswith("__") and "proxy" not in key:
                        newVar[str(key)] = str(val)
                return newVar

            logSys.info("Dumping genericConfig")
            try:
                dataGX = dicify(dict(gxConfig.__dict__))
                writeJSON(data=dataGX, file=paths.dump.joinpath("GX"), sort=True)
            except Exception:
                logSys.exception(f"Dumping genericConfig")
                err = True

            logSys.info("Dumping screenShotCompConfig")
            try:
                dataSSC = dicify(sscConfig.__dict__)
                writeJSON(data=dataSSC, file=paths.dump.joinpath("SSC"), sort=True)
            except Exception:
                logSys.exception(f"Dumping screenShotCompConfig")
                err = True

            logSys.info("Dumping generalEventConfig")
            try:
                dataGE = dicify(geConfig.__dict__)
                writeJSON(data=dataGE, file=paths.dump.joinpath("GE"), sort=True)
            except Exception:
                logSys.exception(f"Dumping generalEventConfig")
                err = True

            logSys.info("Dumping botInformation")
            try:
                dataBI = dicify(botInfo.__dict__)
                writeJSON(data=dataBI, file=paths.dump.joinpath("BI"), sort=True)
            except Exception:
                logSys.exception(f"Dumping botInformation")
                err = True

            logSys.info("Dumping AutoReact")
            try:
                dataAR = "\n\n\n".join(
                    [jdumps(geConfig.autoReacts), jdumps(geConfig.autoReactsChans)]
                )
                writeJSON(
                    data=dicify(dataAR),
                    file=paths.dump.joinpath("AR"),
                    sort=True,
                )
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
            logSys.info("Reload localeConfig")
            try:
                lcConfig.update()
            except Exception:
                logSys.exception(f"Reload localeConfig")
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
