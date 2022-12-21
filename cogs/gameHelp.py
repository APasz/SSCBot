import logging

from config import genericConfig as gxConfig
from util.fileUtil import readJSON, paths
from util.genUtil import blacklistCheck

print("CogGameHelp")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY GAME_HELP IMPORT MODULES")
    from nextcord.ext import commands
except Exception:
    logSys.exception("GAME_HELP IMPORT MODULES")


class gameHelp(commands.Cog, name="GameHelp"):
    """Class containing commands and whatnot meant to help with the game."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logSys.debug(f"{self.__cog_name__} Ready")

    @commands.command(name="wiki", aliases=["w", "wik", "gameinfo"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def wiki(self, ctx, game="2"):
        """Provides links to Wikis *WIP*"""
        if not await blacklistCheck(ctx=ctx):
            return
        try:
            if "2" in game:
                await ctx.send(
                    f"Here's the Wiki for Transport Fever 2.\n{gxConfig.Wiki2}"
                )
            elif "1" in game:
                await ctx.send(
                    f"Here's the Wiki for Transport Fever 1.\n{gxConfig.Wiki1}"
                )
            elif "tf" in game:
                await ctx.send(f"Here's the Wiki for Train Fever.\n{gxConfig.Wiki0}")
            else:
                await ctx.send(
                    f"Unable to find which Wiki you want. Defaulting to TpF2\n{gxConfig.Wiki2}"
                )
        except Exception:
            log.exception(f"Wiki Base")

    @commands.command(name="modding", aliases=["m", "mod"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def modding(self, ctx, entry=None):
        """Provides link TpF mod wiki *WIP*"""
        if not await blacklistCheck(ctx=ctx):
            return
        if entry is None:
            try:
                await ctx.send(gxConfig.Wiki2modInstall)
            except Exception:
                log.exception(f"Wiki mod install")

    @commands.command(name="log", aliases=["c", "crash", "stdout", "gamefiles"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def log(self, ctx, entry="gameFiles", game="2"):
        """Provides link TpF wiki*WIP*"""
        if not await blacklistCheck(ctx=ctx):
            return
        if "2" in game and "gameFiles" in entry:
            try:
                txt = gxConfig.Wiki2gameFiles
                strData = readJSON(file=paths.work.joinpath("strings"))
                udb = strData["en"]["GameHelp"]["UserDataButton"]
                if "stdout" in ctx.message.content:
                    await ctx.send(txt + "#game_log_files" + "\n" + udb)
                else:
                    await ctx.send(txt + "#folder_locations")
            except Exception:
                log.exception(f"Wiki stdou|folder")


def setup(bot: commands.Bot):
    bot.add_cog(gameHelp(bot))


# MIT APasz
