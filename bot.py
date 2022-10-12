#!/usr/bin/env python3

import asyncio
import logging
import os
import platform
import sys
import traceback
from logging import handlers


PID = os.getpid()
print(f"\n***Starting*** {PID=}")


logging.addLevelName(logging.DEBUG, "DBUG")
log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
logMess = logging.getLogger("discordMessages")

log.setLevel("DEBUG")
logSys.setLevel("DEBUG")
logMess.setLevel("DEBUG")

handleConsole = logging.StreamHandler(sys.stdout)
handleConsole.setFormatter(
    logging.Formatter(
        "%(asctime)s |:| %(module)s: %(funcName)s | %(message)s", "%H:%M:%S")
)
log.addHandler(handleConsole)

curDir = os.path.dirname(os.path.realpath(__file__))
logDir = os.path.join(curDir, "logs")

if not os.path.exists(logDir):
    log.debug("mk logDir")
    os.mkdir(logDir)

# log for general
handleFile = handlers.TimedRotatingFileHandler(
    os.path.join(logDir, "discordGeneral.log"), when="W6", utc=True, encoding="utf-8")
handleFile.setFormatter(
    logging.Formatter(
        "%(asctime)s_%(created).2f | %(levelname).4s |:| %(module)s: %(funcName)s | %(message)s",
        "%Y-%m-%d_%H:%M:%S"))
log.addHandler(handleFile)

# log for sys
handleDisFile = logging.FileHandler(
    os.path.join(logDir, "discordSystem.log"), encoding="utf-8", mode="a")
handleDisFile.setFormatter(
    logging.Formatter(
        "%(asctime)s_%(created).2f |:| %(module)s: %(funcName)s | %(message)s",
        "%Y-%m-%d_%H:%M:%S"))
logSys.addHandler(handleDisFile)


# log for deleted messages
messHandler = logging.FileHandler(
    filename=os.path.join(logDir, "discordMessages.log"), encoding="utf-8", mode="a")
messHandler.setFormatter(
    logging.Formatter(
        "%(asctime).19s_%(created).2f |:| %(message)s"))
logMess.addHandler(messHandler)

log.critical(f"\n***Starting*** {PID=}")
logSys.critical(f"\n***Starting*** {PID=}")

critFiles = ["config.json", "config.py"]
configErr = False
for element in critFiles:
    if not os.path.exists(element):
        logSys.critical(f"{element} missing")
        configErr = True

if configErr:
    logSys.critical(f"Files missing!")
    sys.exit(78)

try:
    logSys.debug("TRY MAIN IMPORT CONFIG")
    from config import botInformation as botInfo
    from config import generalEventConfig as geConfig
    from config import genericConfig as gxConfig
    from config import verifyConfigJSON, syncCommands
    from util.fileUtil import readJSON
    from util.genUtil import blacklistCheck
except Exception:
    logSys.exception(f"MAIN IMPORT CONFIG")
    sys.exit()

try:
    logSys.debug(f"Python {platform.python_version()} | TRY IMPORT MODULES")
    import nextcord
    from nextcord import ext
    from nextcord.ext import commands
    from nextcord.ext.commands import CommandNotFound
except Exception:
    logSys.exception("MAIN IMPORT MODULES")
    sys.exit()


if not verifyConfigJSON():
    logSys.critical("Bad Config")
else:
    logSys.info("Good Config")

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

    def botSevers(bot: commands.Bot):
        """Get info about the servers the bot is in"""
        botGuilds = bot.guilds
        botInfo.guildCount = len(botGuilds)
        botInfo.botPerms = []
        for item in botGuilds:
            permList = item.me.guild_permissions
            botInfo.botPerms.append(permList)
            logSys.info(f"{item.name}  {item.id} | {permList=}")
            for perm in permList:
                logSys.info(f"{perm=}")

    @bot.event
    async def on_ready():
        await syncCommands(bot)
        log.critical("\n***Started*** 'Hello World, or whatever'")
        logSys.critical("\n***Started*** 'Hello World, or whatever'")
        #log.debug("on_ready wait_ready")
        botSevers(bot)
        # await bot.wait_until_ready()
        stringsBot = readJSON(filename="strings")["en"]["Bot"]
        txt = (stringsBot["Ready"]).format(base=botInfo.base, name=botInfo.name,
                                           ncVer=botInfo.nextcordVer)
        configuration = readJSON(filename="config")
        globalReady = configuration["General"]["Events"]["ReadyMessage"]
        log.info(f"Config {globalReady=} | {txt=}")
        if globalReady:
            guilds = list((geConfig.guildListID).keys())
            sendReady = []
            for item in guilds:
                item = str(item)
                try:
                    event = configuration[item]["Events"]["ReadyMessage"]
                except KeyError:
                    log.warning(f"Ready KeyErr {item=}")
                    continue
                except Exception:
                    log.exception(f"ReadyMess: {item=}")
                if event:
                    sendReady.append(
                        configuration[item]["Channels"]["ReadyMessage"])
            log.debug(f"{sendReady=}")
            for element in sendReady:
                try:
                    chan = await bot.fetch_channel(int(element))
                except Exception:
                    log.exception(f"ReadyGet {element=}")
                try:
                    await chan.send(txt)
                    log.info(f"Ready Sent: {element=}")
                except Exception:
                    log.exception(f"ReadySend {element=}")
        log.critical("Bot Ready")
        logSys.critical("Bot Ready")

    @bot.check
    async def blacklistedUser(ctx):
        """All prefix commands run this check"""
        if ctx.command is None:
            logSys.debug("ctxCommand")
            return False
        if "private" in str(ctx.channel.type).lower():
            logSys.debug("ctxChannelType")
            return False
        logSys.debug("blacklistedUserCheck")
        if await blacklistCheck(ctx=ctx, blklstType="gen") is True:
            return True
        else:
            raise ext.commands.MissingPermissions([""])

    @bot.event
    async def on_application_command_error(interaction, exception):
        logSys.error(f"{interaction.user.name} | {exception=}")

    @bot.event
    async def on_command_error(ctx, error):
        """When a command encounters and error on Discords side."""
        logSys.critical(f"on_command_error\n{error=}")
        auth = f"{ctx.author.id=}, {ctx.author.display_name=}"

        if isinstance(error, (commands.MissingPermissions)):
            try:
                await ctx.message.delete()
                await ctx.send(
                    f"You don't have the correct permissions.\n{error.missing_permissions=}",
                    delete_after=configuration["General"]["delTime"],
                )
            except Exception:
                logSys.exception(
                    f"UserMissingPerm {error.missing_permissions=}")
            logSys.error(
                f"UserMissingPermission. {auth} | {error.missing_permissions=}")
            return

        if isinstance(error, (commands.MissingRole)):
            try:
                await ctx.message.delete()
                await ctx.send(
                    f"You don't have the correct role.\n{error.missing_role=}",
                    delete_after=configuration["General"]["delTime"],
                )
            except Exception:
                logSys.exception(f"UserMissingRole {error.missing_role=}")
            logSys.error(f"MissingRole. {auth} | {error.missing_role=}")
            return

        if isinstance(error, (commands.MissingRequiredArgument)):
            try:
                await ctx.send("Missing Argument/s")
            except Exception:
                logSys.exception(
                    f"Missing Argument {error.args=} | {error.param=}")
            logSys.error(
                f"MissingArgument. {auth} | {error.args=} | {error.param=}")
            return

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
                logSys.exception(f"Command not Found {error.command_name=}")
            logSys.error(f"CommandNotFound. {auth} | {error.command_name=}")
            return

        if isinstance(error, (commands.DisabledCommand)):
            try:
                await ctx.send(f"Command currently **Disabled**")
            except Exception:
                logSys.exception(
                    f"Disabled Command {error.args=} | {error.with_traceback=}")
            logSys.error(
                f"CommandDisabled. {auth} | {error.args=} | {error.with_traceback=}")
            return

        if isinstance(error, commands.CommandOnCooldown):
            try:
                await ctx.send(
                    f"Command cooldown in effect: {round(error.retry_after, 3)}s"
                )
            except Exception:
                logSys.exception(
                    f"Command Cooldown {round(error.retry_after, 3)}")
            logSys.error(f"CommandCooldown. {auth}")
            return

        if isinstance(error, commands.ExtensionNotFound):
            try:
                await ctx.send(f"Cog not found.")
            except Exception:
                logSys.exception(f"")
            logSys.error(f"ExtensionNotFound. {auth}")
            return

        if isinstance(error, asyncio.TimeoutError):
            try:
                await ctx.send(f"asyncio 408. Response not received in time.")
            except Exception:
                logSys.exception("asyncio 408")
            logSys.error(f"asyncio 408 {auth}")
            return

        if isinstance(error, (PermissionError)):
            logSys.error(f"LowPermError")
            return

        if isinstance(error, (commands.BotMissingRole)):
            logSys.error(f"BotRoleError")
            return

        if isinstance(error, (commands.BotMissingAnyRole)):
            logSys.error(f"BotAnyRoleError")
            return

        if isinstance(error, (commands.BotMissingPermissions)):
            logSys.error(f"BotPermError")
            return

        logSys.critical(f"Unhandled on_command_error")

    @bot.event
    async def on_error(event, *args, **kwargs):
        try:
            err = sys.exc_info()
        except Exception:
            err = "*undefined*"
        try:
            erro = traceback.format_exception()
        except Exception:
            erro = "*undefined*"
        log.error(f"Error! {event=}\n{err=}\n{erro=}\n{args=}\n{kwargs=}")
        logSys.error(traceback.format_exc())
        raise

    for filename in os.listdir(cogsDir):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
            except Exception:
                logSys.exception(f"Autoload Cog {filename=}")

    @bot.event
    async def on_connect():
        log.critical("Connected")
        logSys.critical("Connected")

    @bot.event
    async def on_resumed():
        log.critical("Resumed")
        logSys.critical("Resumed")

    @bot.event
    async def on_close():
        log.critical("Closing")
        logSys.critical("Closing")

    log.critical("Conecting to Discord")
    logSys.critical("Conecting to Discord")

    try:
        from config import DISTOKEN
        bot.run(DISTOKEN)  # , log_handler=handleDisFile
    except Exception:
        log.exception(f"Bot Run")
        logSys.exception(f"Bot Run")


if __name__ == "__main__":
    main()

# MIT APasz
