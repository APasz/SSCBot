#!/usr/bin/env python3
import asyncio
import logging
import os
import sys
import traceback
from logging import handlers
from time import perf_counter

perfTime = {}
perfTime["start"] = perf_counter()


try:
    from util.fileUtil import paths
except Exception:
    sys.exit(78)

PID = os.getpid()
print(f"\n***Starting*** {PID=}")


logging.addLevelName(logging.DEBUG, "DBUG")
log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
logMess = logging.getLogger("discordMessages")

log.setLevel("DEBUG")
logSys.setLevel("DEBUG")
logMess.setLevel("DEBUG")

# log for stdout
handleConsole = logging.StreamHandler(sys.stdout)
handleConsole.setFormatter(
    logging.Formatter(
        "%(asctime)s |:| %(module)s.%(funcName)s | %(message)s", "%H:%M:%S"
    )
)
log.addHandler(handleConsole)


if not paths.log.exists():
    log.debug("mk log")
    paths.log.mkdir()

logTxt = logging.Formatter(
    "%(asctime)s|%(created).3f || %(levelname).4s |:| %(module)s.%(funcName)s | %(message)s",
    "%Y-%m-%d:%H:%M:%S",
)

# log for general
handleFile = handlers.TimedRotatingFileHandler(
    filename=paths.log.joinpath("discordGeneral.log"),
    when="W6",
    utc=True,
    encoding="utf-8",
)
handleFile.setFormatter(logTxt)
log.addHandler(handleFile)

# log for sys
handleDisFile = handlers.TimedRotatingFileHandler(
    filename=paths.log.joinpath("discordSystem.log"),
    when="W6",
    utc=True,
    encoding="utf-8",
)
handleDisFile.setFormatter(logTxt)
logSys.addHandler(handleDisFile)


# log for deleted messages
messHandler = logging.FileHandler(
    filename=paths.log.joinpath("discordMessages.log"), encoding="utf-8", mode="a"
)
messHandler.setFormatter(
    logging.Formatter("%(asctime).19s|%(created).2f |:| %(message)s")
)
logMess.addHandler(messHandler)

log.critical(f"\n***Starting*** {PID=}")
logSys.critical(f"\n***Starting*** {PID=}")
logMess.critical(f"\n***Starting*** {PID=}")

perfTime["log"] = perf_counter()

critFiles = ["config.json", "config.py"]
configErr = False
for element in critFiles:
    file = paths.work.joinpath(element)
    print(file)
    if not file.exists():
        logSys.critical(f"{element} missing")
        configErr = True

if configErr:
    logSys.critical(f"Files missing!")
    sys.exit(78)

try:
    from config import verifyConfigJSON
except Exception:
    logSys.exception("IMPORT VERIFY")
    sys.exit(78)

if not verifyConfigJSON():
    logSys.critical("Bad Config")
else:
    logSys.info("Good Config")

try:
    logSys.debug("TRY MAIN IMPORT CONFIG")
    from config import botInformation as botInfo
    from config import generalEventConfig as geConfig
    from config import genericConfig as gxConfig
    from config import localeConfig as lcConfig
    from config import syncCommands
    from util.fileUtil import readJSON
    from util.genUtil import blacklistCheck, getServConf
    from util.startup import botSevers, getPrefix, sendReady, autoLoadCogs
except Exception:
    logSys.exception(f"MAIN IMPORT CONFIG")
    sys.exit(78)

_ = lcConfig.getLC

try:
    logSys.debug(f"Python {botInfo.hostPython} | TRY IMPORT MODULES")
    import nextcord
    from nextcord import ext
    from nextcord.ext import commands
except Exception:
    logSys.exception("MAIN IMPORT MODULES")
    sys.exit(77)


configuration = readJSON(file=paths.work.joinpath("config"))
LOGLEVEL = (configuration["logLevel"]).upper()
log.debug(f"{LOGLEVEL=}")
log.setLevel(LOGLEVEL)
logMess.setLevel(LOGLEVEL)

perfTime["import"] = perf_counter()

log.info(f"{gxConfig.slashServers=}")


def main():
    intents = nextcord.Intents.default()
    intents.members = True
    intents.message_content = True
    intents.presences = False

    activity = nextcord.Activity(
        type=nextcord.ActivityType.listening,
        name=f"{gxConfig.BOT_PREFIX} and / | v{botInfo.version.major}.{botInfo.version.minor}",
    )

    bot = commands.Bot(
        # commands.when_mentioned_or(gxConfig.BOT_PREFIX),
        command_prefix=getPrefix,
        intents=intents,
        activity=activity,
        case_insensitive=True,
        max_messages=5_000,
    )

    @bot.event
    async def on_ready():
        await syncCommands(bot)
        log.critical("\n***Starting*** 'Hello World, or whatever'")
        logSys.critical("\n***Starting*** 'Hello World, or whatever'")
        perfTime["wait_ready"] = perf_counter()
        botSevers(bot)
        await bot.wait_until_ready()
        perfTime["ready"] = perf_counter()
        globalReady = configuration["Events"]["ReadyMessage"]
        botInfo.bootTime = round((perfTime["ready"] - perfTime["start"]), 2)
        botInfo.perfTime = perfTime
        log.info(f"Config {globalReady=}")
        if globalReady:
            await sendReady(bot, list(geConfig.guildListID.keys()))
        log.critical("Bot Ready")
        logSys.critical("Bot Ready")

    @bot.check
    async def prefixEnabled(ctx: nextcord.Message):
        "All prefix commands run this check"
        if ctx.guild is None:
            logSys.debug("Guild is None")
            return
        guildID = ctx.guild.id
        logSys.debug(f"prefEnb: {guildID}")
        print(ctx.channel.type, nextcord.ChannelType.private)
        if ctx.channel.type == nextcord.ChannelType.private:
            logSys.debug("privateChannel")
            return False
        cf = getServConf(guildID=guildID, option="PrefixCommands")
        print(cf)
        return cf

    @bot.check
    async def blacklistedUser(ctx: nextcord.Message):
        """All prefix commands run this check"""
        if ctx.command is None:
            return False
        if ctx.guild is None:
            return
        if ctx.channel.type == nextcord.ChannelType.private:
            logSys.debug("privateChannel")
            return False
        logSys.debug("blacklistedUserCheck")
        if await blacklistCheck(ctx=ctx, blklstType="gen") is True:
            return True
        else:
            raise ext.commands.MissingPermissions(["Blacklisted"])

    @bot.event
    async def on_application_command_error(interaction, exception):
        logSys.error(
            f"{interaction.user.name} | {interaction.guild.name}\n{exception=}"
        )

    @bot.event
    async def on_command_error(ctx, error):
        """When a command encounters and error on Discords side."""
        logSys.critical(f"on_command_error\n{error=}")
        auth = f"{ctx.author.id=}, {ctx.author.display_name=}"

        if isinstance(error, commands.MissingPermissions):
            try:
                await ctx.message.delete()
                await ctx.send(
                    f"You don't have the correct permissions.\n{error.missing_permissions=}",
                    delete_after=configuration["delTime"],
                )
            except Exception:
                logSys.exception(f"UserMissingPerm {error.missing_permissions=}")
            logSys.error(
                f"UserMissingPermission. {auth} | {error.missing_permissions=}"
            )
            return

        if isinstance(error, commands.MissingRole):
            try:
                await ctx.message.delete()
                await ctx.send(
                    f"You don't have the correct role.\n{error.missing_role=}",
                    delete_after=configuration["delTime"],
                )
            except Exception:
                logSys.exception(f"UserMissingRole {error.missing_role=}")
            logSys.error(f"MissingRole. {auth} | {error.missing_role=}")
            return

        if isinstance(error, commands.MissingRequiredArgument):
            try:
                await ctx.send("Missing Argument/s")
            except Exception:
                logSys.exception(f"Missing Argument {error.args=} | {error.param=}")
            logSys.error(f"MissingArgument. {auth} | {error.args=} | {error.param=}")
            return

        if isinstance(error, commands.CommandNotFound):
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

        if isinstance(error, commands.DisabledCommand):
            try:
                await ctx.send(f"Command currently **Disabled**")
            except Exception:
                logSys.exception(
                    f"Disabled Command {error.args=} | {error.with_traceback=}"
                )
            logSys.error(
                f"CommandDisabled. {auth} | {error.args=} | {error.with_traceback=}"
            )
            return

        if isinstance(error, commands.CommandOnCooldown):
            try:
                await ctx.send(
                    f"Command cooldown in effect: {round(error.retry_after, 3)}s"
                )
            except Exception:
                logSys.exception(f"Command Cooldown {round(error.retry_after, 3)}")
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
            logSys.error(f"asyncio 408 {auth}\n{error=}")
            return

        if isinstance(error, PermissionError):
            logSys.error(f"LowPermError\n{error=}")
            return

        if isinstance(error, commands.BotMissingRole):
            logSys.error(f"BotRoleError\n{error=}")
            return

        if isinstance(error, commands.BotMissingAnyRole):
            logSys.error(f"BotAnyRoleError\n{error=}")
            return

        if isinstance(error, commands.BotMissingPermissions):
            logSys.error(f"BotPermError\n{error=}")
            return

        if isinstance(error, commands.ArgumentParsingError):
            logSys.error(f"BotArgParseError\n{error=}")
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

    perfTime["error"] = perf_counter()

    autoLoadCogs(bot)

    perfTime["cogs"] = perf_counter()

    @bot.event
    async def on_connect():
        log.critical("Connected")
        logSys.critical("Connected")
        perfTime["connect"] = perf_counter()

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

        perfTime["run"] = perf_counter()

        bot.run(DISTOKEN)
    except Exception:
        log.exception(f"Bot Run")
        logSys.exception(f"Bot Run")


if __name__ == "__main__":
    main()

# MIT APasz
