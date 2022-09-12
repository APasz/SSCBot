import asyncio
import logging
import time

from config import genericConfig as gxConfig

from util.fileUtil import readJSON

print("UtilGen")

log = logging.getLogger("discordGeneral")
try:
    log.debug("TRY UTIL_GEN IMPORT MODUELS")
    import nextcord
    from nextcord import Role, Guild as ncGuild
except Exception:
    log.exception("UTIL_GEN IMPORT MODUELS")

configuration = readJSON(filename="config")
configGen = configuration["General"]


def getCol(col: str) -> nextcord.Color:
    """Gets the colour RGB list from config and returns colour object"""
    log.debug(f"{col=}")
    red, green, blue = configGen["EmbedColours"][col]
    colour = nextcord.Colour.from_rgb(red, green, blue)
    return colour


def hasRole(role: Role, userRoles) -> bool:
    """Checks if user has role object
    role = Discord role object
    :param arg2: roles object of a user"""
    log.debug(f"{role=} | {userRoles=}")
    if role in userRoles:
        return True
    else:
        return False


def getUserID(obj) -> str:
    """Gets the user id from either ctx or interaction types"""
    # log.debug(obj)
    if hasattr(obj, "author"):
        return str(obj.author.id)
    if hasattr(obj, "user"):
        return str(obj.user.id)


def getChan(guild: str | int, chan: str, admin: bool = False, self=None):
    """Gets from config a channel id or object using the guild id."""
    log.debug(f"{guild=}, {chan=}, {admin=}, self={type(self)}")
    guild = str(guild)
    chan = str(chan)
    if admin is True:
        admin = "Channels_Admin"
    else:
        admin = "Channels"
    try:
        chanID = readJSON(filename="config")[guild][admin][chan]
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
    log.debug(f"{type(guild)=} | {guild=} | {role=}")
    role = str(role)

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


def hoursFromSeconds(
        seconds: int | str,
        asStr: bool = False,
        strSeconds: bool = True,
        strMinutes: bool = True,
        strHours: bool = True,
        strDays: bool = False,
        strWeeks: bool = False
):
    """Returns (weeks, days,) hours, minutes, and seconds as tuple or string from an int/str of seconds."""
    log.debug(f"{seconds=}, {asStr=}")
    seconds = int(seconds)
    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)
    week, day = divmod(day, 7)
    if not asStr:
        return (week, day, hour, minute, second)
    timeList = []
    if strWeeks:
        if week != 0:
            timeList.append(f"{week} Week")
            if week > 1:
                timeList[-1] = timeList[-1] + "s"
    if strDays:
        if day != 0:
            timeList.append(f"{day} Day")
            if day > 1:
                timeList[-1] = timeList[-1] + "s"
    if strHours:
        if hour != 0:
            timeList.append(f"{hour} Hour")
            if hour > 1:
                timeList[-1] = timeList[-1] + "s"
    if strMinutes:
        if minute != 0:
            timeList.append(f"{minute} Min")
            if minute > 1:
                timeList[-1] = timeList[-1] + "s"
    if strSeconds:
        if second != 0:
            timeList.append(f"{second} Sec")
            if second > 1:
                timeList[-1] = timeList[-1] + "s"
    retrn = ", ".join(timeList)
    log.debug(f"{retrn=}")
    return retrn


def getGuildID(obj) -> str | None:
    """Gets guild id from a guild object"""
    log.debug("run")
    if hasattr(obj, "guild_id"):
        return str(obj.guild_id)
    elif hasattr(obj, "guild"):
        if hasattr(obj.guild, "id"):
            return str(obj.guild.id)
    else:
        return None


async def blacklistCheck(ctx, blklstType: str = "gen") -> bool:
    """Checks if user in the blacklist"""
    log.debug(f"{blklstType=}")

    def check():
        if blklstType == "gen":
            filename = "GeneralBlacklist"
        elif blklstType == "ssc":
            filename = "SSCBlacklist"
        return readJSON(filename=filename, directory=["secrets"])

    userID = getUserID(obj=ctx)
    log.debug(f"{userID=}")
    if userID == gxConfig.ownerID:
        return True
    if userID == ctx.guild.owner.id:
        return True
    BL = check()
    if not bool(BL.get(userID)):
        return True
    txt = f"""You're blacklisted from using **{gxConfig.botName}**.
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
            chan = await self.bot.fetch_channel(gxConfig.pingingChan)
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

# MIT APasz
