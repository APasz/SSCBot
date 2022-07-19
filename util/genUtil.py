print("UtilGen")
import os
import time
import nextcord
from nextcord import Role

from util.fileUtil import readJSON, writeJSON, parentDir
from config import genericConfig

configuration = readJSON(filename="config")
configGen = configuration["General"]
import logging

log = logging.getLogger("discordGeneral")


def getCol(col: str):
    """Gets the colour RGB list from config and returns colour object"""
    log.debug(col)
    red, green, blue = configGen["EmbedColours"][col]
    colour = nextcord.Colour.from_rgb(red, green, blue)
    return colour


def hasRole(role: Role, userRoles):
    """Checks if user has role object"""
    log.debug(role)
    if role in userRoles:
        return True
    else:
        return False


def getUserID(obj):
    """Gets the user id from either ctx or interaction types"""
    # log.debug(obj)
    if hasattr(obj, "author"):
        return str(obj.author.id)
    if hasattr(obj, "user"):
        return str(obj.user.id)


def getChan(guild: str | int, chan: str, admin: bool = False, self=None):
    """Gets from config a channel id using the guild id."""
    guild = str(guild)
    if admin is True:
        admin = "Channels_Admin"
    else:
        admin = "Channels"
    try:
        chanID = readJSON(filename="config")[guild][admin][chan]
    except KeyError:
        return None
    if self is not None:
        return self.bot.get_channel(chanID)
    else:
        return chanID


def hoursFromSeconds(
    seconds: int | str,
    asStr: bool = False,
) -> tuple | str:
    """Returns hours, minutes, and seconds as tuple or string(# H, ) from an int/str of seconds."""
    seconds = int(seconds)
    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)

    if not asStr:
        return (hour, minute, second)
    timeList = []
    if hour != 0:
        timeList.append(f"{hour} Hour")
        if hour > 1:
            timeList[-1] = timeList[-1] + "s"
    if minute != 0:
        timeList.append(f"{minute} Min")
        if minute > 1:
            timeList[-1] = timeList[-1] + "s"
    if second != 0:
        timeList.append(f"{second} Sec")
        if second > 1:
            timeList[-1] = timeList[-1] + "s"
    return ", ".join(timeList)


def getGuildID(obj) -> str | None:
    """Gets guild id from a guild object"""
    if hasattr(obj, "guild_id"):
        return str(obj.guild_id)
    elif hasattr(obj, "guild"):
        if hasattr(obj.guild, "id"):
            return str(obj.guild.id)
    else:
        return None


async def blacklistCheck(ctx, blklstType: str = "gen"):
    """Checks if user in the blacklist"""
    # log.debug(ctx)

    def check():
        if blklstType == "gen":
            filename = "GeneralBlacklist"
        elif blklstType == "ssc":
            filename = "SSCBlacklist"
        return readJSON(filename=filename, directory=["secrets"])

    userID = None
    userID = getUserID(obj=ctx)
    log.debug(userID)
    if userID == genericConfig.ownerID:
        return True
    if userID == ctx.guild.owner.id:
        return True
    BL = check()
    if not bool(BL.get(userID)):
        return True
    txt = f"""You're blacklisted from using **{genericConfig.botName}**.
If you believe this to be error, please contact a server Admin/Moderator."""
    if "inter" in str(type(ctx)):
        await ctx.response.send_message(txt, ephemeral=True)
    elif "user" in str(type(ctx)):
        await ctx.send(txt)
    elif "member" in str(type(ctx)):
        await ctx.send(txt)
    log.info(f"BLCheck: {userID} | {blklstType}")
    return False


def getGlobalEventConfig(listAll: bool = False):
    """Gets list of either all or only globally disabled events"""
    globalEvents = set()
    configuration = readJSON(filename="config")
    for itemKey, itemVal in configuration["General"]["Events"].items():
        if listAll is True:
            globalEvents.add(itemKey)
            continue
        elif itemVal == False:
            globalEvents.add(itemKey)
    return globalEvents


def getEventConfig(by: str = "id"):
    """Returns list of events allowed per server by either ID or config name."""
    print("getEventConfigRead")
    configuration = readJSON(filename="config")
    globalEvents = getGlobalEventConfig()
    events = {}
    for item in configuration:
        if by == "name":
            try:
                nameID = configuration[item]["Config_Name"]
            except:
                pass
        elif by == "id":
            try:
                configuration[item]["Config_Name"]
                nameID = item
            except:
                pass
        eventList = []
        try:
            for elementKey, elementVal in configuration[item]["Events"].items():
                if (elementKey not in globalEvents) and (elementVal == True):
                    eventList.append(elementKey)
                events[nameID] = eventList
        except:
            pass
    return events


def getGuilds(includeGlobal: bool = False, by: str = "id"):
    """Returns dict(ID|ConfigName) of all guilds and their ids"""
    configuration = readJSON(filename="config")
    IDs = {}
    for item in configuration:
        if by == "id":
            try:
                IDs[item] = configuration[item]["Config_Name"]
            except:
                pass
        if by == "name":
            try:
                IDs[configuration[item]["Config_Name"]] = item
            except:
                pass
    if includeGlobal:
        IDs["Global"] = "General"
    return IDs


# MIT APasz
