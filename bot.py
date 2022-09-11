#!/usr/bin/env python3

import asyncio
import logging
import os
import platform
import sys
from logging import handlers

from config import botInformation as botInfo
from config import generalEventConfig as geConfig
from config import genericConfig as gxConfig
from config import verifyConfigJSON
from util.fileUtil import readJSON
from util.genUtil import blacklistCheck

PID = os.getpid()
print(f"\n***Starting*** {PID=}")


logging.addLevelName(logging.DEBUG, "DBUG")
log = logging.getLogger("discordGeneral")
logMess = logging.getLogger("discordMessages")

log.setLevel("DEBUG")

handleConsole = logging.StreamHandler(sys.stdout)
handleConsole.setFormatter(
    logging.Formatter("%(asctime)s |:| %(module)s | %(message)s", "%H:%M:%S")
)
log.addHandler(handleConsole)

curDir = os.path.dirname(os.path.realpath(__file__))
logDir = os.path.join(curDir, "logs")

if not os.path.exists(logDir):
    log.debug("mk logDir")
    os.mkdir(logDir)

# handleFile = logging.FileHandler(
#    filename=os.path.join(logDir, "discordGeneral.log"), encoding="utf-8", mode="a"
# )

handleFile = handlers.TimedRotatingFileHandler(
    os.path.join(logDir, "discordGeneral.log"), when="W6", utc=True)

handleFile.setFormatter(
    logging.Formatter(
        "%(asctime)s_%(created).2f | %(levelname).4s |:| %(module)s: %(funcName)s | %(message)s",
        "%Y-%m-%d_%H:%M:%S")
)
log.addHandler(handleFile)

messHandler = logging.FileHandler(
    filename=os.path.join(logDir, "discordMessages.log"), encoding="utf-8", mode="a"
)
messHandler.setFormatter(
    logging.Formatter(
        "%(asctime).19s_%(created).2f |:| %(message)s")
)
logMess.addHandler(messHandler)

log.critical(f"\n***Starting*** {PID=}")

critFiles = ["config.json", "config.py"]
configErr = False
for element in critFiles:
    if not os.path.exists(element):
        log.critical(f"{element} missing")
        configErr = True

if configErr:
    log.critical(f"Files missing!")
    sys.exit(78)

try:
    log.debug(f"Python {platform.python_version()} | TRY IMPORT MODULES")
    import nextcord
    from nextcord import ext
    from nextcord.ext import commands
    from nextcord.ext.commands import CommandNotFound
except Exception:
    log.exception("MAIN IMPORT MODULES")
    sys.exit()


if not verifyConfigJSON():
    log.critical("Bad Config")
else:
    log.info("Good Config")

configuration = readJSON(filename="config")

LOGLEVEL = (configuration["General"]["logLevel"]).upper()
log.debug(f"{LOGLEVEL=}")
log.setLevel(LOGLEVEL)
logMess.setLevel(LOGLEVEL)


log.info(f"{gxConfig.slashServers=}")


def main():
    intents = nextcord.Intents.default()
    intents.members = True
    intents.message_content = True
    intents.presences = False

    activity = nextcord.Activity(
        type=nextcord.ActivityType.listening,
        name=f"{gxConfig.BOT_PREFIX} and / | v{botInfo.major}.{botInfo.minor}",
    )

    bot = commands.Bot(
        commands.when_mentioned_or(gxConfig.BOT_PREFIX),
        intents=intents,
        activity=activity,
        case_insensitive=True,
    )
    cogsDir = os.path.join(curDir, "cogs")

    def botSevers(bot):
        """Get info about the servers the bot is in"""

        botGuilds = bot.guilds
        botInfo.guildCount = len(botGuilds)

    @bot.event
    async def on_ready():
        log.critical("\n***Started*** 'Hello World, or whatever'")
        #log.debug("on_ready wait_ready")
        botSevers(bot)
        # await bot.wait_until_ready()
        stringsBot = readJSON(filename="strings")["en"]["Bot"]
        txt = (stringsBot["Ready"]).format(base=botInfo.base, name=botInfo.name,
                                           ncVer=botInfo.nextcordVer)
        configuration = readJSON(filename="config")
        globalReady = configuration["General"]["Events"]["ReadyMessage"]
        log.info(f"Config {globalReady=} | {txt=}")
        if globalReady == True:
            guilds = list((geConfig.guildListID).keys())
            sendReady = []
            for item in guilds:
                item = str(item)
                try:
                    event = configuration[item]["Events"]["ReadyMessage"]
                except KeyError:
                    log.exception(f"KeyErr {item=}")
                    continue
                except Exception:
                    log.exception(f"ReadyMess: {item=}")
                if event == True:
                    sendReady.append(
                        configuration[item]["Channels"]["ReadyMessage"])
            log.debug(f"{sendReady=}")
            for element in sendReady:
                try:
                    chan = await bot.fetch_channel(element)
                except Exception:
                    log.exception(f"ReadyGet {element=}")
                try:
                    await chan.send(txt)
                    log.info(f"Ready Sent: {element=}")
                except Exception:
                    log.exception(f"ReadySend {element=}")
        log.critical("Bot Ready")

    @bot.check
    async def blacklistedUser(ctx):
        """All prefix commands run this check"""
        if ctx.command is None:
            log.debug("ctxCommand")
            return False
        if "private" in str(ctx.channel.type).lower():
            log.debug("ctxChannelType")
            return False
        log.debug("blacklistedUserCheck")
        if await blacklistCheck(ctx=ctx, blklstType="gen") is True:
            return True
        else:
            raise ext.commands.MissingPermissions([""])

    @bot.event
    async def on_command_error(ctx, error):
        """When a command encounters and error on Discords side."""
        auth = f"{ctx.author.id=}, {ctx.author.display_name=}"
        if isinstance(error, (commands.MissingPermissions)):
            try:
                await ctx.message.delete()
                await ctx.send(
                    f"You don't have the correct permissions.\n{error.missing_permissions=}",
                    delete_after=configuration["General"]["delTime"],
                )
            except Exception:
                log.exception(f"UserMissingPerm {error.missing_permissions=}")
            log.error(
                f"UserMissingPermission. {auth} | {error.missing_permissions=}")

        if isinstance(error, (commands.MissingRole)):
            try:
                await ctx.message.delete()
                await ctx.send(
                    f"You don't have the correct role.\n{error.missing_role=}",
                    delete_after=configuration["General"]["delTime"],
                )
            except Exception:
                log.exception(f"UserMissingRole {error.missing_role=}")
            log.error(f"MissingRole. {auth} | {error.missing_role=}")

        if isinstance(error, (commands.MissingRequiredArgument)):
            try:
                await ctx.send("Missing Argument/s")
            except Exception:
                log.exception(
                    f"Missing Argument {error.args=} | {error.param=}")
            log.error(
                f"MissingArgument. {auth} | {error.args=} | {error.param=}")

        if isinstance(error, (commands.CommandNotFound)):
            if ctx.message.content.startswith(
                f"{gxConfig.BOT_PREFIX}{gxConfig.BOT_PREFIX}"
            ):
                return
            try:
                await ctx.send(
                    f"Command not found.\nPlease check with {gxConfig.BOT_PREFIX}help"
                )
            except Exception:
                log.exception(f"Command not Found {error.command_name=}")
            log.error(f"CommandNotFound. {auth} | {error.command_name=}")

        if isinstance(error, (commands.DisabledCommand)):
            try:
                await ctx.send(f"Command currently **Disabled**")
            except Exception:
                log.exception(
                    f"Disabled Command {error.args=} | {error.with_traceback=}")
            log.error(
                f"CommandDisabled. {auth} | {error.args=} | {error.with_traceback=}")

        if isinstance(error, commands.CommandOnCooldown):
            try:
                await ctx.send(
                    f"Command cooldown in effect: {round(error.retry_after, 3)}s"
                )
            except Exception:
                log.exception(
                    f"Command Cooldown {round(error.retry_after, 3)}")
            log.error(f"CommandCooldown. {auth}")

        if isinstance(error, commands.ExtensionNotFound):
            try:
                await ctx.send(f"Cog not found.")
            except Exception:
                log.exception(f"")
            log.error(f"ExtensionNotFound. {auth}")

        if isinstance(error, asyncio.TimeoutError):
            try:
                await ctx.send(f"asyncio 408. Response not received in time.")
            except Exception:
                log.exception("asyncio 408")
            log.error(f"asyncio 408 {auth}")

    for filename in os.listdir(cogsDir):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
            except Exception:
                log.exception(f"Autoload Cog {filename=}")

    log.critical("Conecting to Discord")
    try:
        from config import DISTOKEN
        bot.run(DISTOKEN)
    except Exception:
        log.exception(f"Bot Run")


if __name__ == "__main__":
    main()

# MIT APasz
