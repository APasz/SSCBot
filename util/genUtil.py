import asyncio
import inspect
import logging
import time
from dataclasses import dataclass
from pathlib import Path as Pathy

print("UtilGen")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY UTIL_GEN IMPORT MODUELS")
    import nextcord
    from nextcord import Emoji
    from nextcord import Guild as ncGuild
    from nextcord import Interaction, Message, PartialEmoji, Role
    from nextcord.ext.commands import Context

    from config import botInformation as botInfo
    from config import genericConfig as gxConfig
    from config import localeConfig as lcConfig
    from util.fileUtil import paths, readJSON, writeJSON
except Exception:
    logSys.exception("UTIL_GEN IMPORT MODUELS")

configuration = readJSON(file=paths.work.joinpath("config"))
configGen = configuration


def getCol(col: str) -> nextcord.Color:
    """Gets the colour RGB list from config and returns colour object"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {col=}")
    if col == "nexus":
        col = "nexusmods"

    red, green, blue = configGen["EmbedColours"][col]
    colour = nextcord.Colour.from_rgb(red, green, blue)
    return colour


def hasRole(role: Role, userRoles) -> bool:
    """Checks if user has role object
    role = Discord role object
    :param arg2: roles object of a user"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {role=} | {userRoles=}")

    return role in userRoles


def getChan(guild: int, chan: str, admin: bool = False, self=None):
    """Gets from config a channel id or object using the guild id."""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {guild=}, {chan=}, {admin=}, self={type(self)}")

    if admin is True:
        admin = "Channels_Admin"
    else:
        admin = "Channels"

    chanID = getServConf(guildID=guild, group=admin, option=chan)

    if self:
        return self.bot.get_channel(chanID)
    else:
        return chanID


def getRole(guild: int | ncGuild, role: str):
    """Gets from config a channel id using the guild id.
    If guild object is pass, role object is returned"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {type(guild)=} | {guild=} | {role=}")

    if isinstance(guild, str):
        guild = int(guild)
    role = str(role)

    def fromConfig(g: str, r: str):
        g = str(g)
        r = str(r)
        return getServConf(guildID=g, group="Roles", option=r)

    if isinstance(guild, int):
        roleReturn = fromConfig(g=guild, r=role)
    else:
        roleID = fromConfig(g=guild.id, r=role)
        try:
            roleReturn = guild.get_role(int(roleID))
        except Exception:
            logSys.exception(f"getRole obj")
            roleReturn = None
    logSys.debug(f"{type(roleReturn)=} | {roleReturn=}")
    return roleReturn


class formatTime:
    """Turn seconds into more human readable"""

    func = inspect.stack()[1][3]
    logSys.debug(f"{func=}")

    def _strPluralise(num: int, word: str) -> str:
        num = int(num)
        x = f"{num} {word}"
        if num > 1:
            x = x + "s"
        return x

    def _breakdown(num: int):
        @dataclass(slots=True)
        class _totals:
            total_second: int
            seconds: int
            total_minute: int
            minutes: int
            total_hour: int
            hours: int
            total_day: int
            days: int
            weeks: int

        _totals.t_minute, _totals.seconds = divmod(num, 60)
        _totals.t_hour, _totals.minutes = divmod(_totals.t_minute, 60)
        _totals.t_day, _totals.hours = divmod(_totals.t_hour, 24)
        _totals.weeks, _totals.days = divmod(_totals.t_day, 7)

        return _totals

    def time_format(total):
        log.debug(total)
        k = formatTime._breakdown(total)
        strTime = []

        if k.seconds > 0:
            i = formatTime._strPluralise(k.seconds, "Sec")
            strTime.append(i)
        if k.minutes > 0:
            i = formatTime._strPluralise(k.minutes, "Min")
            strTime.append(i)
        if k.hours > 0:
            i = formatTime._strPluralise(k.hours, "Hour")
            strTime.append(i)
        if k.days > 0:
            i = formatTime._strPluralise(k.days, "Day")
            strTime.append(i)
        if k.weeks > 0:
            i = formatTime._strPluralise(k.weeks, "Week")
            strTime.append(i)

        strTime.reverse()
        log.debug(strTime)
        return ", ".join(strTime)


async def blacklistCheck(ctx, blklstType: str = "gen") -> bool:
    """Checks if user in the blacklist"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {blklstType=}")
    cd = commonData(ctx)

    def check():
        if blklstType == "gen":
            filename = "GeneralBlacklist"
        elif blklstType == "ssc":
            filename = "SSCBlacklist"
        return readJSON(file=paths.secret.joinpath(filename))

    log.debug(f"{cd.intUser=}")
    if cd.intUser == int(gxConfig.ownerID):
        return True
    if cd.intUser == int(ctx.guild.owner.id):
        return True
    BL = check()
    if not bool(BL.get(cd.intUser)):
        return True
    txt = f"""You're blacklisted from using **{botInfo.botName}**.
If you believe this to be error, please contact a server Admin/Moderator."""
    try:
        if "inter" in str(type(ctx)):
            await ctx.response.send_message(txt, ephemeral=True)
        elif "user" in str(type(ctx)):
            await ctx.send(txt)
        elif "member" in str(type(ctx)):
            await ctx.send(txt)
    except Exception:
        log.exception(f"/Blacklist Check")
    log.info(f"BLCheck: {cd.intUser=} | {blklstType=}")
    return False


async def _ping(self, api: bool = False, testNum: int = 1) -> list[int]:
    """Get latency to Discord"""
    logSys.debug(f"_ping {api=} | {testNum=}")
    testNumGate = testNumAPI = testNum

    async def apiPing(chan) -> int:
        se = time.perf_counter()
        try:
            await chan.send("Ponging...")
        except Exception:
            log.exception(f"Pong")
        en = time.perf_counter()
        ping = int(round((en - se) * 1000))
        log.debug(ping)
        return ping

    def gatePing() -> int:
        try:
            test = self.bot.latency
            ping = int(round(test * 1000))
        except Exception:
            log.exception(f"bot Latency")
        else:
            log.debug(ping)
            return ping
        return False

    testsGate = []
    while testNumGate > 0:
        log.debug(f"While {testNumGate=}")
        testNumGate = testNumGate - 1
        try:
            test = gatePing()
            testsGate.append(test)
            await asyncio.sleep(0.05)
        except Exception:
            log.exception(f"Ping Gate")
    testsGate = int(sum(testsGate) / len(testsGate))

    testsAPI = None
    if api:
        try:
            chan = await self.bot.fetch_channel(int(gxConfig.pingingChan))
        except Exception:
            chan = False
            log.exception(f"pinging Chan")
        else:
            testsAPI = []
            while testNumAPI > 0:
                log.debug(f"While {testNumAPI=}")
                testNumAPI = testNumAPI - 1
                try:
                    test = await apiPing(chan=chan)
                    testsAPI.append(test)
                    await asyncio.sleep(0.05)
                except Exception:
                    log.exception(f"Ping API")
        testsAPI = int(sum(testsAPI) / len(testsAPI))
    testsBoth = [testsGate, testsAPI]
    log.debug(f"{testsBoth=}")
    return testsBoth


def sortReactions(reactions: list):
    "Sorts the reactions list of a message into lists[(name, id) | str] of Emoji, Partial, String, and Unknown"
    reactsObj = []
    reactsStr = []
    reactsBad = []
    reactsUnk = []
    for react in reactions:
        if isinstance(react.emoji, str):
            logSys.debug(f"StrEmoji | {react.emoji}")
            reactsStr.append(react.emoji)
        elif isinstance(react.emoji, Emoji):
            logSys.debug(f"ObjEmoji | {react.emoji}")
            reactsObj.append((react.emoji.name, react.emoji.id))
        elif isinstance(react.emoji, PartialEmoji):
            logSys.debug(f"ParEmoji | {react.emoji}")
            reactsBad.append((react.emoji.name, react.emoji.id))
        else:
            logSys.debug(f"UnkEmoji | {type(react)}, {react}")
            reactsUnk.append(react)

    class reacts:
        Obj = reactsObj
        Str = reactsStr
        Bad = reactsBad
        Unk = reactsUnk

    return reacts


def getNameID(k: list | tuple | set, name: bool = True) -> str | int:
    "Returns the first str or first int"
    if name:
        typ = str
    else:
        typ = int
    for e in k:
        print(type(e), e)
        if isinstance(e, typ):
            return e
    return False


def getUserConf(userID: int | str, option: str):
    """Retrieves the value of a userConf option
    returns None if user doesn't have a value set"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {userID=} | {option=}")
    userID = str(userID)
    userConf = readJSON(file=paths.conf.joinpath("user"))
    try:
        return userConf[userID][option]
    except Exception:
        return None


def setUserConf(userID: int | str, option: str, value):
    """Sets the value of an option of a user"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {userID=} | {option=} | {value=}")
    userID = str(userID)
    userConf = readJSON(file=paths.conf.joinpath("user"))
    oldValue = None
    if userID not in userConf:
        userConf[userID] = {}
    if option in userConf[userID]:
        oldValue = userConf[userID][option]
    userConf[userID][option] = value
    logSys.debug(f"userConf updated! {userID=} | {option=} | {oldValue} -> {value}")
    return writeJSON(userConf, file=paths.conf.joinpath("user"))


def getServConf(guildID: int | str, option: str, group: str = None):
    """Retrieves the value of a servConf option
    returns None if server doesn't have a value set"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {guildID=} | {group=} |  {option=}")
    guildID = str(guildID)
    option = str(option)
    servConf = readJSON(paths.conf.joinpath(guildID))
    if group is None:
        try:
            return servConf[option]
        except Exception:
            return None
    else:
        group = str(group)
        try:
            return servConf[group][option]
        except Exception:
            return None


def setServConf(guildID: int | str, option: str, value, group: str = None):
    """Sets the value of an option of a user"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {guildID=} | {option=} | {value=}")
    servConf = readJSON(file=paths.conf.joinpath(str(guildID)))
    oldValue = None
    if group:
        if group not in servConf:
            servConf[group] = {}
        oldValue = servConf[group][option]
        servConf[group][option] = value
    else:
        oldValue = servConf[option]
        servConf[option] = value
    logSys.debug(f"userConf updated! {guildID=} | {option=} | {oldValue} -> {value}")
    return writeJSON(servConf, file=paths.conf.joinpath(str(guildID)))


def commonData(obj: Context | Interaction):
    """Takes either a command Context or application Interaction
    returns object with"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {type(obj)}")

    class data:
        print(obj.guild)
        intGuild = int(obj.guild.id)
        "int of the guild id"
        strGuild = str(obj.guild.id)
        "str of the guild id"
        guildID_Name = f"GuildID: {obj.guild.id} | GuildName: {obj.guild.name}"
        "For log convince, Guild ID | Guild name"
        intChan = int(obj.channel.id)
        "int of the channel id"
        strChan = str(obj.channel.id)
        "str of the channel id"
        chanID_Name = f"ChanID: {obj.channel.id} | ChanName: {obj.channel.name}"
        "For log convince, channel ID | channel name"
        intUser: int
        "int of the member id"
        strUser: str
        "str of the member id"
        userID_Name: str
        "For log convince, member ID | member display_name"
        locale: str

    if isinstance(obj, Context | Message):  # Context type
        data.intUser = int(obj.author.id)
        data.strUser = str(obj.author.id)
        data.userID_Name = (
            f"UserID: {obj.author.id} | UserName: {obj.author.display_name}"
        )
        data.locale = lcConfig.getGuildLC(data.intGuild)
        if data.locale in lcConfig.sameyLangs:
            data.locale = lcConfig.sameyLangs[data.locale][0]

    elif isinstance(obj, Interaction):  # Interacton type
        data.intUser = int(obj.user.id)
        data.strUser = str(obj.user.id)
        data.userID_Name = f"UserID: {obj.user.id} | UserName: {obj.user.display_name}"
        data.locale = obj.locale

    if data.intGuild in gxConfig.GUILD_BOT_PREFIX:
        data.prefix = gxConfig.GUILD_BOT_PREFIX[data.intGuild]
    else:
        data.prefix = gxConfig.BOT_PREFIX

    return data


def onMessageCheck(ctx):
    func = inspect.stack()[1][3]
    log.debug(f"{func=}")
    if ctx.guild is None:
        return False
    if ctx.author.id == gxConfig.botID:
        return False
    if (ctx.guild.id == gxConfig.ownerGuild) and gxConfig.Prod:
        return False
    return True


# MIT APasz
