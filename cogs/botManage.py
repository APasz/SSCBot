print("CogBotManage")
import logging

from nextcord.ext import commands

log = logging.getLogger("discordGeneral")

from config import genericConfig
import os
from util.genUtil import blacklistCheck
from discord import Permissions, SlashApplicationSubcommand
from nextcord import Embed, Interaction, SlashOption, slash_command
from nextcord.ext import application_checks, commands
from config import genericConfig, dataObject
from util.genUtil import parentDir


class botManage(commands.Cog, name="BotManagement"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="reload", aliases=["rl"], hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension):
        """Reloads a specific cog"""
        log.debug(ctx.author.id)
        try:
            self.bot.reload_extension(f"cogs.{extension}")
        except Exception as xcp:
            await ctx.send(f"**{extension}** can't be reloaded.")
            log.error(f"{extension} can't be reloaded: {xcp}")
        else:
            await ctx.send(f"**{extension}** successfully reloaded.")

    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension):
        """Loads a specific cog"""
        log.debug(ctx.author.id)
        try:
            self.bot.load_extension(f"cogs.{extension}")
        except:
            await ctx.send(f"**{extension}** can't be loaded.")
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
        except:
            await ctx.send(f"**{extension}** can't be unloaded.")
            log.warning(f"{extension} can't be unloaded")
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
        except:
            await ctx.send("Cogs can't be reloaded.")
            log.error("Cogs can't be reloaded")
        else:
            await ctx.send("All cogs successfully reloaded.")


def setup(bot: commands.Bot):
    bot.add_cog(botManage(bot))


# MIT APasz
