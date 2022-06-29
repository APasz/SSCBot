print("UtilGen")
import config
import os
import nextcord
from nextcord import Role

from util.fileUtil import readJSON

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


def hasRole(role: Role, roles):
    """Checks if user has role object"""
    log.debug(role)
    if role in roles:
        return True
    else:
        return False


def getUserID(obj):
    """Gets the user id from either ctx or interaction types"""
    log.debug(obj)
    if hasattr(obj, "author"):
        return str(obj.author.id)
    if hasattr(obj, "user"):
        return str(obj.user.id)


def getChan(guild: str, chan: str, admin: bool = False):
    """Gets the channel id using the guild name in config."""
    if admin is True:
        admin = "Channels_Admin"
    else:
        admin = "Channels"
    configuration = readJSON(filename="config")
    return configuration[guild][admin][chan]


async def blacklistCheck(ctx, blklstType: str = "gen"):
    """Checks if user in the blacklist"""
    log.debug(ctx)

    def check():
        if blklstType == "gen":
            filename = "GeneralBlacklist"
        elif blklstType == "ssc":
            filename = "SSCBlacklist"
        return readJSON(filename=filename, directory=["secrets"])

    userID = None
    userID = getUserID(obj=ctx)
    log.debug(userID)
    if userID == config.ownerID:
        return True
    if userID == ctx.guild.owner.id:
        return True
    BL = check()
    if not bool(BL.get(userID)):
        return True
    txt = f"""You're blacklisted from using **{config.botName}**.
If you believe this to be error, please contact a server Admin/Moderator."""
    if "inter" in str(type(ctx)):
        await ctx.response.send_message(txt, ephemeral=True)
    elif "user" in str(type(ctx)):
        await ctx.send(txt)
    elif "member" in str(type(ctx)):
        await ctx.send(txt)
    log.info(f"BLCheck: {userID} | {blklstType}")
    return False


def getGlobalEventConfig(configuration, listAll: bool = False):
    """Gets list of globally disabled events"""
    globalEvents = set()
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
    globalEvents = getGlobalEventConfig(configuration)
    events = {}
    for item in configuration:
        if by == "name":
            try:
                configuration[item]["ID"]
                nameID = item
            except:
                pass
        elif by == "id":
            try:
                configuration[item]["ID"]
                nameID = configuration[item]["ID"]
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


def getGuilds(includeGlobal: bool = False):
    """Returns dict(ID|ConfigName) of all guilds and their ids"""
    configuration = readJSON(filename="config")
    IDs = {}
    for item in configuration:
        try:
            guildID = configuration[item]["ID"]
            IDs[guildID] = item
        except:
            pass
    if includeGlobal:
        IDs["Global"] = "General"
    return IDs


# MIT APasz
