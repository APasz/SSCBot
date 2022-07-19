#!/usr/bin/env python3
import os
import sys

PID = os.getpid()
print(f"\n***Starting*** PID'{PID}'")


from util.fileUtil import newFile, readFile, readJSON, writeJSON

configuration = readJSON(filename="config")
configGen = configuration["General"]

import logging

log = logging.getLogger("discordGeneral")
logMess = logging.getLogger("discordMessages")

log.setLevel(configGen["logLevel"].upper())
logMess.setLevel(configGen["logLevel"].upper())

handleConsole = logging.StreamHandler(sys.stdout)
handleConsole.setFormatter(
    logging.Formatter("%(asctime)s |:| %(module)s | %(message)s", "%H:%M:%S")
)
log.addHandler(handleConsole)

handleFile = logging.FileHandler(
    filename=f"logs{os.sep}discordGeneral.log", encoding="utf-8", mode="a"
)
handleFile.setFormatter(
    logging.Formatter(
        "%(asctime)s:%(created)f |:| %(levelname)s:%(module)s; %(funcName)s | %(message)s",
    )
)
log.addHandler(handleFile)

messHandler = logging.FileHandler(
    filename=f"logs{os.sep}discordMessages.log", encoding="utf-8", mode="a"
)
messHandler.setFormatter(
    logging.Formatter("%(asctime)s:%(created)f |:| %(module)s; %(message)s")
)
logMess.addHandler(messHandler)

log.critical(f"\n***Starting*** PID'{PID}'")

critFiles = ["config.json", "config.py", "randomFact.txt", "missing.png"]
configErr = False
for element in critFiles:
    if not os.path.exists(element):
        log.critical(f"{element} missing")
        configErr = True

if configErr:
    log.critical(f"files missing!")
    sys.exit(78)

import asyncio

import nextcord
from nextcord import ext
from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound

from config import genericConfig
from util.genUtil import blacklistCheck, getGuilds

log.info(f"SlashComm Guilds: {genericConfig.slashServers}")


def main():
    intents = nextcord.Intents.default()
    intents.members = True
    intents.message_content = True

    data = readJSON(filename="changelog")
    ver = list(data.keys())[-1]
    verMajor, verMinor, verPoint = ver.split(".")
    verName, verDate = list(data[f"{ver}"])[0].split("::")

    activity = nextcord.Activity(
        type=nextcord.ActivityType.listening,
        name=f"{genericConfig.BOT_PREFIX} and / | v{verMajor}.{verMinor}",
    )

    bot = commands.Bot(
        commands.when_mentioned_or(genericConfig.BOT_PREFIX),
        intents=intents,
        activity=activity,
        case_insensitive=True,
    )
    curDir = os.path.dirname(os.path.realpath(__file__))
    cogsDir = os.path.join(curDir, "cogs")

    @bot.event
    async def on_ready():
        log.critical("\n***Started*** 'Hello World, or whatever'")
        txt = f"""**v{verMajor}.{verMinor}.{verPoint} | {verName}**
Nextcord v{nextcord.__version__} **Ready**\nUse /changelog to see changes"""
        configuration = readJSON(filename="config")
        configGen = configuration["General"]
        oldVerMajor = configGen["verMajor"]
        oldVerMinor = configGen["VerMinor"]
        oldVerPoint = configGen["verPoint"]
        if (
            oldVerMajor != verMajor
            or oldVerMinor != verMinor
            or oldVerPoint != verPoint
        ):
            configGen["verMajor"] = verMajor
            configGen["VerMinor"] = verMinor
            configGen["verPoint"] = verPoint
            configGen["verName"] = verName
            writeJSON(data=configuration, filename="config")
        globalReady = configGen["Events"]["ReadyMessage"]
        log.debug(f"globalReady: {globalReady}")
        if globalReady is True:
            guilds = getGuilds().keys()
            sendReady = []
            for item in guilds:
                try:
                    event = configuration[item]["Events"]["ReadyMessage"]
                    if event is True:
                        sendReady.append(
                            configuration[item]["Channels"]["ReadyMessage"]
                        )
                except KeyError:
                    pass
            for element in sendReady:
                try:
                    chan = await bot.fetch_channel(element)
                    await chan.send(txt)
                except Exception as xcp:
                    if "Missing Access" in str(xcp):
                        log.error(f"Missing Access: {element}")
                        pass
        messFile = os.path.join(curDir, "messID.txt")
        if os.path.exists(messFile):
            messIDs = readFile(directory=curDir, filename="messID")
            os.remove(os.path.join(curDir, "messID.txt"))
            log.debug(messIDs)
            if len(messIDs) <= 2:
                return
            messID, chanID = messIDs.split("|")
            chan = await bot.fetch_channel(int(chanID))
            mess = await chan.fetch_message(int(messID))
            await mess.edit(content="Reboot Successful!")

    @bot.check
    async def blacklistedUser(ctx):
        if ctx.command is None:
            print("ctxCommand")
            return False
        if "private" in str(ctx.channel.type).lower():
            print("ctxChannelType")
            return False
        log.debug("blacklistedUserCheck")
        if await blacklistCheck(ctx=ctx, blklstType="gen") is True:
            return True
        else:
            raise ext.commands.MissingPermissions([""])

    @bot.event
    async def on_command_error(ctx, error):
        auth = f"{ctx.author.id}, {ctx.author.display_name}"
        if isinstance(error, (commands.MissingPermissions)):
            await ctx.message.delete()
            await ctx.send(
                "You don't have the correct permissions.",
                delete_after=configuration["General"]["delTime"],
            )
            log.error(f"MissingPermission. {auth}")
        if isinstance(error, (commands.MissingRole)):
            await ctx.message.delete()
            await ctx.send(
                "You don't have the correct role.",
                delete_after=configuration["General"]["delTime"],
            )
            log.error(f"MissingRole. {auth}")
        if isinstance(error, (commands.MissingRequiredArgument)):
            await ctx.send("Missing Argument/s")
            log.error(f"MissingRole. {auth}")
        if isinstance(error, (commands.CommandNotFound)):
            if ctx.message.content.startswith(
                f"{genericConfig.BOT_PREFIX}{genericConfig.BOT_PREFIX}"
            ):
                return
            await ctx.send(
                f"Command not found.\nPlease check with {genericConfig.BOT_PREFIX}help"
            )
            log.error(f"CommandNotFound. {auth}")
        if isinstance(error, (commands.DisabledCommand)):
            await ctx.send(f"Command currently **Disabled**")
            log.error(f"CommandDisabled. {auth}")
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"Command cooldown in effect: {round(error.retry_after, 3)}s"
            )
            log.error(f"CommandCooldown. {auth}")
        if isinstance(error, commands.ExtensionNotFound):
            await ctx.send(f"Cog not found.")
            log.error(f"ExtensionNotFound. {auth}")
        if isinstance(error, asyncio.TimeoutError):
            await ctx.send(f"asyncio 408. Response not received in time.")
            log.error(f"asyncio 408 {auth}")

    @bot.command(name="toggle")
    @commands.has_permissions(administrator=True)
    async def toggle(ctx, comm=None):
        """Toggles a command. Must be Admin"""
        log.debug(ctx.author.id)
        if comm != None:
            command = bot.get_command(comm)
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
            await ctx.send(
                "Command not found"
            )  # this should probably check the list of commands...

    @bot.command(name="memory", hidden=True)
    @commands.is_owner()
    async def memory(ctx):
        """Fetches the current amount of memory used by the bot process"""
        log.debug(ctx.author.id)
        import platform
        import resource

        memKB = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        memMB = int(memKB) / 10**3
        totalMemoryMB, usedMemoryMB, freeMemoryMB = map(
            int, os.popen("free -t -m").readlines()[-1].split()[1:]
        )
        percent = round((usedMemoryMB / totalMemoryMB) * 100, 2)
        if usedMemoryMB > 4096:
            usedMemory = f"{int(usedMemoryMB) / 10**3}GB"
        else:
            usedMemory = f"{usedMemoryMB}MB"
        await ctx.send(
            f"{platform.node()}\nProcess: {memMB}MB\nSystem: {usedMemory} {percent}%"
        )

    async def botRestartCheck(ctx, currentDirectory: str):
        log.critical(ctx.author)
        mess = await ctx.send("Commencing restart squence...")

        def check(m):
            if m.author == ctx.author and m.channel == ctx.channel:
                return True

        try:
            reply = await bot.wait_for("message", check=check, timeout=15.0)
        except asyncio.TimeoutError as xcp:
            await mess.edit(content="Timeout. Restart Aborted")
            log.error(f"timeout, {xcp}")
            return False
        except Exception as xcp:
            await mess.edit(content=f"xcp: {xcp}")
        await reply.delete()
        await mess.edit(content="Confirmed. Restartig momentarily")
        IDs = f"{mess.id}|{mess.channel.id}"
        file = os.path.join(currentDirectory, "messID.txt")
        if os.path.exists(file):
            log.debug("File found")
            os.remove(file)
        if not newFile(IDs, directory=currentDirectory, filename="messID"):
            ctx.send("Restart Halted: Error noting message ID\nContinue anyway?")
            if not await bot.wait_for("message", check=check, timeout=10.0):
                return False
        return True

    def systemRestart(system: bool):
        log.critical(f"Rebooting | System: {system}")
        if system is True:
            sys.exit(194)
        else:
            sys.exit(0)

    @bot.command(name="botRestart", hidden=True)
    @commands.is_owner()
    async def botRestart(ctx, system=True):
        """Exits the Discord Bot script. By default it's automatically restarted by the trigger script"""
        if await botRestartCheck(ctx, currentDirectory=curDir) is False:
            return
        systemRestart(system)

    for filename in os.listdir(cogsDir):
        if filename.endswith(".py") and filename != "__init__.py":
            bot.load_extension(f"cogs.{filename[:-3]}")

    log.critical("Conecting to Discord")
    from config import DISTOKEN

    bot.run(DISTOKEN)


if __name__ == "__main__":
    main()

# MIT APasz
