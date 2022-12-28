import logging

logSys = logging.getLogger("discordSystem")

try:
    from config import botInformation as botInfo
    from config import genericConfig as gxConfig
    from config import localeConfig as lcConfig
    from util.fileUtil import paths, readJSON
except Exception:
    logSys.exception(f"STARTUP IMPORT MODULES")

_ = lcConfig.getLC


async def getPrefix(bot, message):
    if message.guild is None:
        logSys.debug("Guild is None")
        return gxConfig.BOT_PREFIX
    guildID = int(message.guild.id)
    prefixes = gxConfig.GUILD_BOT_PREFIX
    logSys.debug(f"prefix {guildID=} | {prefixes=}")
    return prefixes.get(guildID, gxConfig.BOT_PREFIX)


def _findReady(guildListID: list) -> dict[str, str]:
    """Finds the guilds that have been the readyMessage toggle enabled
    returns dict of str channel IDs and the configured lang"""

    sendReadies = {}
    for guildID in guildListID:
        guild = readJSON(file=paths.conf.joinpath(str(guildID)))
        try:
            event = bool(guild["Events"]["ReadyMessage"])
            lang = str(guild["MISC"]["Language"])
        except KeyError:
            logSys.warning(f"Ready KeyErr {guildID=}")
            continue
        except Exception:
            logSys.exception(f"ReadyMess: {guildID=}")
        logSys.debug(f"lang | {lang=}")
        if lang in lcConfig.sameyLangs:
            lang = lcConfig.sameyLangs[lang][0].value
            logSys.debug(f"sammyLangs | {lang=}")
        if event:
            sendReadies[(guild["Channels"]["ReadyMessage"])] = lang
    logSys.debug(f"{len(sendReadies)}:{sendReadies=}")
    return sendReadies


async def sendReady(bot, guildListID: list):
    """Formats and sends the bot ready message to guilds"""

    sendReadies = _findReady(guildListID)
    for chanID, lang in sendReadies.items():
        try:
            chan = bot.get_channel(int(chanID))
        except Exception:
            logSys.exception(f"ReadyGet {chanID=}")
            continue
        txtBase = f"**v{botInfo.version.base_version} | {botInfo.version.title}**\n"
        txtTrans = _("BOT_ONREADY", lang)
        txt = txtBase + txtTrans.format(
            boot=f"{botInfo.bootTime}s",
            ncVer=f"v{botInfo.nextcordVer}",
        )
        try:
            await chan.send(txt)
            logSys.info(f"Ready Sent: {chanID=}")
        except Exception:
            logSys.exception(f"ReadySend {chanID=}")


def botSevers(bot):
    """Get info about the servers the bot is in"""
    botGuilds = bot.guilds
    botInfo.guildCount = len(botGuilds)
    botInfo.botPerms = []
    gxConfig.permissions = {}
    for item in botGuilds:
        gxConfig.permissions[item.id] = []
        permObj = item.me.guild_permissions
        botInfo.botPerms.append(permObj)
        logSys.info(f"{item.name}  {item.id} | {permObj=}")
        for perm in permObj:
            gxConfig.permissions[item.id].append(perm)


def autoLoadCogs(bot):
    for file in paths.cog.iterdir():
        logSys.info(f"Autoloading: {file.name}")
        if file.name.startswith("__"):
            logSys.info(f"Autoloading: Invalid")
            continue
        if file.name.endswith(".py"):
            try:
                bot.load_extension(f"cogs.{file.stem}")
                logSys.info(f"Autoloading: Done!")
            except Exception:
                logSys.exception(f"Autoload Cog {file.stem}")
    logSys.info(f"Autoloaded: {', '.join(list(bot.extensions.keys()))}")
