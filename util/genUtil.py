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
    from nextcord import Role
except Exception:
    logSys.exception("UTIL_GEN IMPORT MODUELS")

configuration = readJSON(filename="config")
configGen = configuration["General"]


def getCol(col: str) -> nextcord.Color:
    """Gets the colour RGB list from config and returns colour object"""
    func = inspect.stack()[1][3]
    log.debug(f"{func=} | {col=}")

    red, green, blue = configGen["EmbedColours"][col]
    colour = nextcord.Colour.from_rgb(red, green, blue)
    return colour


def hasRole(role: Role, userRoles) -> bool:
    """Checks if user has role object
    role = Discord role object
    :param arg2: roles object of a user"""
    func = inspect.stack()[1][3]
    log.debug(f"{func=} | {role=} | {userRoles=}")

    return role in userRoles


def getUserID(obj) -> str | int:
    """Gets the user id from either ctx or interaction types"""
    func = inspect.stack()[1][3]
    log.debug(f"{func=} | type={type(obj)}")

    if hasattr(obj, "author"):
        return obj.author.id
    if hasattr(obj, "user"):
        return obj.user.id


def getChannelID(obj) -> str | int:
    """Gets the channel id from either ctx or interaction types"""
    func = inspect.stack()[1][3]
    log.debug(f"{func=} | type={type(obj)}")

    if hasattr(obj, "channel"):
        return obj.channel.id
    if hasattr(obj, "channel_id"):
        return obj.channel_id


def getGuildID(obj) -> str | None:
    """Gets guild id from a guild object"""
    func = inspect.stack()[1][3]
    log.debug(f"{func=} | type={type(obj)}")

    if hasattr(obj, "guild_id"):
        return str(obj.guild_id)
    elif hasattr(obj, "guild"):
        if hasattr(obj.guild, "id"):
            return str(obj.guild.id)
    else:
        return None


def getChan(guild: str | int, chan: str, admin: bool = False, self=None):
    """Gets from config a channel id or object using the guild id."""
    func = inspect.stack()[1][3]
    guild = str(guild)
    chan = str(chan)
    log.debug(f"{func=} | {guild=}, {chan=}, {admin=}, self={type(self)}")

    if admin is True:
        admin = "Channels_Admin"
    else:
        admin = "Channels"
    try:
        chanID = int(readJSON(filename="config")[guild][admin][chan])
    except KeyError:
        return None
    except Exception:
        log.exception("Get Chan")
    if self is not None:
        return self.bot.get_channel(chanID)
    else:
        return chanID


def getRole(guild: str | int | ncGuild, role: str):
    """Gets from config a channel id or object using the guild id."""
    func = inspect.stack()[1][3]
    role = str(role)
    log.debug(f"{func=} | {type(guild)=} | {guild=} | {role=}")

    def fromConfig(g: str, r: str):
        try:
            return readJSON(filename="config")[g]["Roles"][r]
        except KeyError:
            log.exception("getRole KeyErr")
        except Exception:
            log.exception("Get Role id")

    if isinstance(guild, int | str):
        roleRtn = fromConfig(g=str(guild), r=str(role))
    else:
        roleID = fromConfig(g=str(guild.id), r=str(role))
        try:
            roleRtn = guild.get_role(int(roleID))
        except Exception:
            log.exception(f"getRole obj")
            roleRtn = None
    log.debug(f"{type(roleRtn)=} | {roleRtn=}")
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
        class _totals():
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
        return ', '.join(strTime)


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


def isEmojiCustom(emoji: str, guildEmos: tuple = None) -> str | list:
    """If a emoji is custom, a tuple of it's name and id is returned
    if only a name is given, a guild emoji tuple must also be provided, in order to get the id
    else the emoji is returned"""
    func = inspect.stack()[1][3]
    log.debug(f"{func=} | {type(emoji)} | {emoji=} | {guildEmos=})")

    if isinstance(emoji, str):
        if emoji.startswith('<'):
            log.debug("Is special")
            name, ID = (emoji[2:-1]).split(':')
            return [name, ID]
        elif emoji.startswith(':'):
            log.debug("Is name")
            if guildEmos:
                emoName = emoji[1:-1]
                for item in guildEmos:
                    log.debug(f"{type(item)} | {item}")
                    if emoName in str(item):
                        return [item.name, item.id]
            else:
                log.error("guildEmos not provided")
                return False

        else:
            log.debug("Likely normal")
            return emoji
    else:
        log.debug(f"Not str {type(emoji)=}")
        return False


def toStr(k: list, sep: str = ' '):
    "Converts a list to string"
    func = inspect.stack()[1][3]
    log.debug(f"{func=} | {k=} | {type(k)}")
    if isinstance(k, list):
        return sep.join(k)
    else:
        return k


def emoToStr(e: list, sep: str = ' '):
    func = inspect.stack()[1][3]
    log.debug(f"{func=} | {e=} | {type(e)}")
    if isinstance(e, list):
        emoList = []
        for item in e:
            if isinstance(item, str):
                emoList.append(item)
            elif isinstance(item, list):
                print(item[0], type(item[0]))
                emoList.append(item[0])
        return sep.join(emoList)
    else:
        return e


def toList(k: str | int, sep: str = ' '):
    func = inspect.stack()[1][3]
    log.debug(f"{func=} | {k=} | {type(k)} | {sep=}")
    if isinstance(k, str | int):
        k = str(k)
        return k.split(str(sep))
    else:
        return k


def emoToList(e: str, guildEmos: tuple, sep: str = ' '):
    func = inspect.stack()[1][3]
    log.debug(f"{func=} | {e=} | {type(e)} | {sep=} | {guildEmos=}")
    if isinstance(e, str):
        eList = e.split(str(sep))
    else:
        return e
    emoList = []
    for item in eList:
        if len(item) > 0:
            emoList.append(isEmojiCustom(
                emoji=item, guildEmos=guildEmos))
    return emoList

# MIT APasz
