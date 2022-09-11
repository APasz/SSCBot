import logging
import math
import os
import platform
import sys
from dataclasses import dataclass

from util.fileUtil import readJSON, writeJSON

print("Config")

log = logging.getLogger("discordGeneral")
try:
    log.debug("TRY CONFIG IMPORT MODULES")
    import nextcord
    import psutil
    from nextcord.ext import commands
    from packaging import version
except Exception:
    log.exception("CONFIG IMPORT MODULES")


configuration = readJSON(filename="config")


def slashList() -> set:
    """Gets guild IDs of all servers it's allowed for + owner guild"""
    slashes = set()
    for item in configuration:
        try:
            state = configuration[item]["SlashCommands"]
        except:
            continue
        if state is True:
            slashes.add(int(item))
    slashes.add(int(431272247001612309))
    return slashes


if 246190532949180417 in slashList():
    emoNotifi = "<:notified:427470234463502336>"
else:
    emoNotifi = "🙃"


class _singleton_(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass(slots=True)
class genericConfig(metaclass=_singleton_):
    """Class for basic bot configuration"""

    @classmethod
    def update(cls):
        "Reassign default class attributes from their source"
        cls.slashServers = slashList()
        "Servers which the bot has a config for and thus can use slash commands"
        return True

    emoNotifi = emoNotifi
    emoHeart = "❤️"
    emoStar = "⭐"
    emoTmbUp = "👍"
    emoTmbDown = "👎"
    emoCheck = "☑️"
    emo0 = "0️⃣"
    emo1 = "1️⃣"
    emo2 = "2️⃣"
    emo3 = "3️⃣"
    emo4 = "4️⃣"
    emo5 = "5️⃣"
    emo6 = "6️⃣"
    emo7 = "7️⃣"
    emo8 = "8️⃣"
    emo9 = "9️⃣"

    Wiki0 = "https://train-fever.fandom.com/wiki/Train_Fever_Wiki"
    Wiki1 = "https://www.transportfever.com/wiki/doku.php"
    Wiki2 = "https://www.transportfever2.com/wiki/doku.php"
    Wiki2modInstall = Wiki2 + "?id=gamemanual:modinstallation"
    Wiki2gameFiles = Wiki2 + "?id=gamemanual:gamefilelocations"

    BOT_PREFIX = "~"
    "Prefix the bot listens to"
    botName = "Katoku"
    "Name of the bot user"
    botID = 762054632510849064
    "ID of the bot user"

    configCommGroupWhitelist = ["Channels", "Channels_Admin", "Roles", "MISC"]
    "Groups of the config JSON that are accessible by the configuration command"
    importantFiles = ["facts.json", "missing.png"]
    "List of files that are important to the function of the bot but aren't covered by initial startup"
    factsJSON = "facts.json"
    "Name of the file which contains all the facts"
    pingingChan = 1018012984053870622

    ownerID = 375547210760454145
    "Discord user ID of owner"
    ownerName = "APasz"
    "Name the owner goes by"
    ownerSteamID = 76561198062050071
    "SteamID of the owner"
    ownerTpFNetID = 35634
    "Transportfever.net user ID of owner"
    ownerNexusID = 6561498
    "Nexusmods user ID of owner"
    ownerAuditChan = 935677246482546748
    "Auditlog channel ID of the owners personal server"
    ownerGuild = 431272247001612309
    "Guild ID of the owners personal server"

    metricUnits = {
        "Micrometre": "micrometre",
        "Millimetre": "millimetre",
        "Centimetre": "centimetre",
        "Metre": "metre",
        "Kilometre": "kilometre",
        "Microgram": "microgram",
        "Miligram": "miligram",
        "Gram": "gram",
        "Kilogram": "kilogram",
        "Tonne": "tonne",
        "Millilitre": "millilitre",
        "Litre": "litre",
    }
    "For Pint"

    imperialUnits = {
        "Inch": "inch",
        "Feet": "feet",
        "Yard": "yard",
        "Mile": "mile",
        "Teaspoon": "teaspoon",
        "Tablespoon": "tablespoon",
        "Fluid ounce": "fluid ounce",
        "Cup": "cup",
        "Pint US": "pint",
        "Pint UK": "imperial_pint",
        "Quart US": "quart",
        "Quart UK": "imperial_quart",
        "Gallon US": "gallon",
        "Gallon UK": "imperial_gallon",
        "Ounce US": "ounce",
        "Ounce UK": "imperial_ounce",
        "Pound": "pound",
        "Ton US": "US_ton",
        "Ton UK": "UK_ton",
    }
    "For Pint"

    timeUnits = {
        "Seconds": "seconds",
        "Minute": "minute",
        "Hour": "hour",
        "Day": "day",
        "Week": "week",
        "Year": "year",
    }
    "For Pint"


genericConfig.update()


def bytesMagnitude(byteNum: int, magnitude: str, bi: bool, bit: bool) -> float:
    """Turns an int into a more friendly magnitude
    magnitude=['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']"""
    magnitude = magnitude.upper()
    if bi:
        bi = 1024
    else:
        bi = 1000
    if bit:
        byteNum = byteNum * 8
    ratios = {'K': 1, 'M': 2, 'G': 3, 'T': 4,
              'P': 5, 'E': 6, 'Z': 7, 'Y': 8}
    try:
        return round(byteNum / math.pow(bi, ratios[magnitude]), 3)
    except Exception:
        log.exception("BytesMag")
        return False


def bytesToHuman(byteNum: int, magnitude: str, bi: bool = True, bit: bool = False) -> str:
    """Turns an int into a friendly notation
    magnitude=['AUTO', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']"""
    if not isinstance(byteNum, int):
        log.error("BytesHuman, Not INT")
        return False
    nota = ['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    magnitude = magnitude.upper()
    if magnitude not in nota:
        log.error("BytesHuman, Not MAG")
        return False
    size = bytesMagnitude(
        byteNum=byteNum, magnitude=magnitude, bi=bi, bit=bit)
    if bi:
        power = "i"
    else:
        power = ""
    if bit:
        length = "b"
    else:
        length = "B"
    return f"{size}{magnitude}{power}{length}"


def getGuilds(includeGeneral: bool = False, by: str = "id") -> dict:
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
    if includeGeneral:
        IDs["Global"] = "General"
    return IDs


def getGlobalEventConfig(listAll: bool = False) -> set:
    """Gets list of either all or only globally disabled events"""
    log.debug(f"{listAll=}")
    globalEvents = set()
    configuration = readJSON(filename="config")
    for itemKey, itemVal in configuration["General"]["Events"].items():
        log.debug(f"{itemKey=} | {itemVal=}")
        if listAll == True:
            globalEvents.add(itemKey)
        elif itemVal == False:
            globalEvents.add(itemKey)
    log.debug(f"{globalEvents=}")
    return globalEvents


def getEventConfig(by: str = "id") -> dict:
    """Returns list of events allowed per server by either ID or config name."""
    log.debug(f"getEventConfigRead {by=}")
    configuration = readJSON(filename="config")
    globalEvents = getGlobalEventConfig()
    events = {}
    for item in configuration:
        if item != "General":
            if by == "name":
                try:
                    nameID = configuration[item]["Config_Name"]
                except Exception:
                    log.exception("ConfigName to nameID")
            elif by == "id":
                try:
                    configuration[item]["Config_Name"]
                    nameID = item
                except Exception:
                    log.exception("ConfigID to nameID")
            eventList = []
            try:
                for elementKey, elementVal in configuration[item]["Events"].items():
                    if (elementKey not in globalEvents) and (elementVal == True):
                        eventList.append(elementKey)
                    events[nameID] = eventList
            except Exception:
                log.exception("nameID and Events")
    return events


@dataclass(slots=True)
class screenShotCompConfig(metaclass=_singleton_):
    """Common data for the SSC"""

    @classmethod
    def update(cls):
        "Reassign default class attributes from their source"
        cls.tpfID = int(getGuilds(by="name")["TPFGuild"])
        "ID of the TPF|Gloabal server"
        _configuration = readJSON(filename="config")
        _tpfConfig = _configuration[str(cls.tpfID)]
        cls.curTheme = _configuration["General"]["SSC_Data"]["theme"]
        "The current theme of the competition"
        cls.sscmanager = str(_tpfConfig["Roles"]["SSC_Manager"])
        "ID of the SSCManager role"
        cls.winner = str(_tpfConfig["Roles"]["SSC_Winner"])
        "ID of the SSC Winner role"
        cls.winnerPrize = str(_tpfConfig["Roles"]["SSC_WinnerPrize"])
        "ID of the SSC Prize Winner role"
        cls.runnerUp = str(_tpfConfig["Roles"]["SSC_Runnerup"])
        "ID of the SSC Runnerup role"
        cls.remindChan = str(_tpfConfig["Channels"]["SSC_Remind"])
        "Channel competition reminder should be sent"
        cls.sscChan = str(_tpfConfig["Channels"]["SSC_Comp"])
        "Channel the competition takes place"
        cls.TPFssChan = str(_tpfConfig["Channels"]["ScreenshotsTPF"])
        "Channel where TpF screenshots should go "
        cls.OGssChan = str(_tpfConfig["Channels"]["ScreenshotsGames"])
        "Channel where non-TpF screenshots should go"
        cls.themesDict = _configuration["General"]["SSC_Data"]["allThemes"]
        "Dict of all themes and their notes"

        _genCF = readJSON(filename="config")["General"]
        "General block of config"
        cls.delTime = float(_genCF["delTime"])
        "Time to delay deleting a message"
        return True


screenShotCompConfig.update()


@dataclass(slots=True)
class generalEventConfig(metaclass=_singleton_):
    """Config for the General Events"""

    @classmethod
    def update(cls):
        "Reassign default class attributes from their source"
        cls.onMemberFired = False
        "Flag for if the regular member left event triggered"
        cls.guildListID = getGuilds(by="id")
        "getGuilds by ID"
        cls.guildListName = getGuilds(by="name")
        "getGuilds by Name"
        cls.guildListIDGen = getGuilds(by="id", includeGeneral=True)
        "getGuilds by ID includes General"
        cls.guildListNameGen = getGuilds(by="name", includeGeneral=True)
        "getGuilds by Name includes General"
        cls.eventConfigID = getEventConfig(by="id")
        "getEventConfig by ID"
        cls.eventConfigName = getEventConfig(by="name")
        "getEventConfig by Name"
        cls.globalEvent = getGlobalEventConfig(listAll=False)
        "getGlobalEvent | only disabled"
        cls.globalEventAll = getGlobalEventConfig(listAll=True)
        "getGlobalEvent | listAll"
        cls.defaultEvents = [
            "ReadyMessage",
            "Artwork",
            "Battles",
            "MemberJoin",
            "MemberJoinRecentCreation",
            "MemberAccept",
            "MemberNameChange",
            "MemberVerifiedRole",
            "MemberKick",
            "MemberBan",
            "MemberUnban",
            "MemberLeave",
            "MemberWelcome",
            "MessageDelete",
            "ModPreview",
            "ModPreviewGlobal", ]
        "All recognised events"
        return True


generalEventConfig.update()


@dataclass(slots=True)
class botInformation(metaclass=_singleton_):
    """Store various bits of info about the bot and what it's running on"""

    @classmethod
    def update(cls):
        "Reassign default class attributes from their source"
        _data = readJSON(filename="changelog")
        _verKey = str(list(_data.keys())[-1])
        cls.name = _data[_verKey][0].split("::")[0]
        "Name of current version"
        cls.date = _data[_verKey][0].split("::")[1]
        "Date update was published"
        _ver = version.parse(_verKey)
        cls.major = _ver.major
        "Major number of the bot version"
        cls.minor = _ver.minor
        "Minor number of the bot version"
        cls.micro = _ver.micro
        "Point/Micro number of the bot version"
        cls.base = _ver.base_version
        "Str of the bot version"
        cls.release = _ver.release
        "Tuple of the bot version"
        cls.nextcordVer = nextcord.__version__
        "Version of Nextcord installed"
        cls.hostname = platform.node()
        "Hostname/Network-name of host"
        cls.hostOS = f"{platform.system()}"
        "Operating System of host"
        cls.hostPython = platform.python_version()
        "Version of Python installed"
        cls.hostRAM = bytesToHuman(
            byteNum=(int(psutil.virtual_memory().total)), magnitude="G")
        "Total RAM in GiB of host system | Includes notation"
        cls.hostCores = psutil.cpu_count(logical=True)
        "Number of logical cores host has"
        cls.hostCPUfreq = psutil.cpu_freq()
        "Frequency of host CPU"
        cls.processPID = os.getpid()
        "Current process ID"
        return True


botInformation.update()


@dataclass(slots=True)
class dataObject:
    """Class for transferring data from events to auditlog but can be used for anything obviously"""

    TYPE: str
    auditChan: nextcord.TextChannel
    "Channel Object (as received from Discord) of channel where audit logs should be sent"
    auditID: int
    "Channel ID of channel where audit logs should be sent"
    caseID: int
    "ID if a case"
    local: str
    "local"
    category: str
    "Category of a thing"
    categorySub: str
    "Subcategory of a thing"
    categoryGroup: str
    "Category group of a thing"
    channelID: int
    "ID of any type of channel"
    channelType: str
    "The type of channel, eg text, voice, thread, etc"
    channelName: str
    "Name of any type of channel"
    channelText: nextcord.TextChannel
    "Channel object of a text channel"
    channelVoice: nextcord.VoiceChannel
    "Channel object of a voice channel"
    commandArgList: list
    "List of arguments that go with or are for a command"
    commandArg1: any
    "The first argument of a command"
    commandArg2: any
    "The second argument of a command"
    commandArg3: any
    "The third argument of a command"
    commandArg4: any
    "The forth argument of a command"
    count: int
    "The count of something"
    directory: str
    "The path to somewhere"
    extraData: any
    "Any additional data that is either of unknown type or doesn't fit anywhere else"
    filename: str
    "Name of a file"
    guildConfigName: str
    "The friendly name of a guild that is found in the config file"
    guildExtra: any
    "Any additional data related to a guild"
    guildID: int
    "The ID of a guild"
    guildName: str
    "Name of a guild"
    guildObject: nextcord.Guild
    "Guild Object as received from Discord"
    limit: int
    "Limit of something"
    messageChan: int
    "Channel ID of a message"
    messageContent: str
    "Content of a message"
    messageID: int
    "ID of a message"
    messageObject: nextcord.Message
    "Message object as received from Discord"
    messageObjectExtra: nextcord.Message
    "Additional message object"
    reason: str
    "If something has a reason"
    userExtra: any
    "Any additional data related to a user/member"
    userID: int
    "ID of a user/member"
    userName: str
    "Either account name or displayname of a user/member"
    userObject: nextcord.User | nextcord.Member | nextcord.ClientUser
    "User or Member object as recieved from Discord"
    userObjectExtra: nextcord.User | nextcord.Member | nextcord.ClientUser
    "An additional user/member object"


def verifyConfigJSON() -> bool:
    """Checks that certain elements are present and if not, gives a default value.
    Also to be used to update the config when the bot gets an update."""

    configuration = readJSON(filename="config.json")
    genCF = configuration["General"]
    if (not isinstance(genCF["delTime"], int | float) or (genCF["delTime"] > 120)):
        genCF["delTime"] = 20

    if (not isinstance(genCF["logLevel"], str)):
        genCF["logLevel"] = "DEBUG"

    if (not isinstance(genCF["purgeLimit"], int | float) or (genCF["purgeLimit"] > 100)):
        genCF["purgeLimit"] = 100

    for item in generalEventConfig.defaultEvents:
        if item not in configuration["General"]["Events"]:
            configuration["General"]["Events"][item] = True

    for item in configuration:
        if "General" not in item:
            try:
                configuration[item]["SlashCommands"]
            except KeyError:
                configuration[item]["SlashCommands"] = True

    genCF["EmbedColours"]["botInfo"] = [250, 0, 0]
    genCF["EmbedColours"]["ssc"] = [190, 0, 70]

    return writeJSON(data=configuration, filename="config.json")


# secrets
secret = readJSON(directory=["secrets"], filename="nolooky", cache=False)
DISTOKEN = secret["DISCORD_TOKEN"]
STEAMAPI = secret["STEAM_WEB_API"]
NEXUSAPI = secret["NEXUSMODS_API"]
