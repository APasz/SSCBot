import asyncio
from collections import namedtuple
import logging
import time
from dataclasses import dataclass
import inspect

from config import genericConfig as gxConfig
from config import botInformation as botInfo

from util.fileUtil import readJSON

print("UtilGen")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY UTIL_GEN IMPORT MODUELS")
    import nextcord
    from nextcord import Guild as ncGuild
    from nextcord import Role, Emoji, PartialEmoji
    from nextcord.ext.commands import EmojiConverter, EmojiNotFound
except Exception:
    logSys.exception("UTIL_GEN IMPORT MODUELS")

configuration = readJSON(filename="config")
configGen = configuration["General"]


def getCol(col: str) -> nextcord.Color:
    """Gets the colour RGB list from config and returns colour object"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {col=}")

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


def getUserID(obj) -> int:
    """Gets the user id from either ctx or interaction types"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | type={type(obj)}")

    if hasattr(obj, "author_id"):
        return int(obj.author_id)
    if hasattr(obj, "user_id"):
        return int(obj.user_id)
    if hasattr(obj, "author"):
        return int(obj.author.id)
    if hasattr(obj, "user"):
        return int(obj.user.id)


def getChannelID(obj) -> int:
    """Gets the channel id from either ctx or interaction types"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | type={type(obj)}")

    if hasattr(obj, "channel_id"):
        return int(obj.channel_id)
    if hasattr(obj, "channel"):
        return int(obj.channel.id)


def getGuildID(obj) -> int:
    """Gets guild id from a guild object"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | type={type(obj)}")

    if hasattr(obj, "guild_id"):
        return int(obj.guild_id)
    if hasattr(obj, "guild"):
        return int(obj.guild.id)


def getChan(guild: int, chan: str, admin: bool = False, self=None):
    """Gets from config a channel id or object using the guild id."""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {guild=}, {chan=}, {admin=}, self={type(self)}")

    if admin is True:
        admin = "Channels_Admin"
    else:
        admin = "Channels"
    try:
        chanID = int(readJSON(filename="config")[str(guild)][admin][str(chan)])
    except KeyError:
        return None
    except Exception:
        logSys.exception("Get Chan")
    if self is not None:
        return self.bot.get_channel(chanID)
    else:
        return chanID


def getRole(guild: int | ncGuild, role: str):
    """Gets from config a channel id or object using the guild id."""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {type(guild)=} | {guild=} | {role=}")

    if isinstance(guild, str):
        guild = int(guild)
    role = str(role)

    def fromConfig(g: str, r: str):
        g = str(g)
        r = str(r)
        try:
            return readJSON(filename="config")[g]["Roles"][r]
        except KeyError:
            logSys.exception("getRole KeyErr")
        except Exception:
            logSys.exception("Get Role id")

    if isinstance(guild, int):
        roleRtn = fromConfig(g=guild, r=role)
    else:
        roleID = fromConfig(g=guild.id, r=role)
        try:
            roleRtn = guild.get_role(int(roleID))
        except Exception:
            logSys.exception(f"getRole obj")
            roleRtn = None
    logSys.debug(f"{type(roleRtn)=} | {roleRtn=}")
    return roleRtn


class formatTime:
    """Turn seconds into more human readable"""

    func = inspect.stack()[1][3]
    log.debug(f"{func=}")

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
    log.debug(f"{func=} | {blklstType=}")

    def check():
        if blklstType == "gen":
            filename = "GeneralBlacklist"
        elif blklstType == "ssc":
            filename = "SSCBlacklist"
        return readJSON(filename=filename, directory=["secrets"])

    userID = int(getUserID(obj=ctx))
    log.debug(f"{userID=}")
    if userID == int(gxConfig.ownerID):
        return True
    if userID == int(ctx.guild.owner.id):
        return True
    BL = check()
    if not bool(BL.get(userID)):
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
    log.info(f"BLCheck: {userID=} | {blklstType=}")
    return False


async def _ping(self, api: bool = False, testNum: int = 1) -> list[int]:
    """Get latency to Discord"""
    log.debug(f"_ping {api=} | {testNum=}")
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


def getLocale(locale: str) -> dict:
    "Returns dict associated with a lang code. Defaults to en"
    logSys.debug(f"{locale=}")
    if locale.startswith("en"):
        locale = "en"
    if locale not in gxConfig.langs:
        locale = "en"
    return readJSON(filename=locale, directory=["strings"])


def getLocaleText(
    locale: str = "en", category: str = "undefined", key: str = "undefined"
) -> str:
    "Returns localised text for the key provided. Defaults to en"
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {locale=} | {category=} | {key=}")
    if category == "undefined" or key == "undefined":
        return None
    try:
        return getLocale(locale)[category][key]
    except Exception as xcp:
        if "KeyError" not in str(xcp):
            logSys.exception("Locale Text")
        return getLocale("en")[category][key]


# MIT APasz
