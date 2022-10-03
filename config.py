import logging
import math
import os
import platform
from dataclasses import dataclass

from util.fileUtil import readJSON, writeJSON

print("Config")

log = logging.getLogger("discordGeneral")
try:
    log.debug("TRY CONFIG IMPORT MODULES")
    import nextcord
    import psutil
    from packaging import version
except Exception:
    log.exception("CONFIG IMPORT MODULES")


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
        log.debug(item)
        if "General" not in item:
            try:
                configuration[item]["SlashCommands"]
            except KeyError:
                configuration[item]["SlashCommands"] = True

            try:
                configuration[item]["Events"]["AutoReact"]
            except KeyError:
                configuration[item]["Events"]["AutoReact"] = True

            try:
                del configuration[item]["Events"]["Artwork"]
            except Exception:
                log.exception(f"Could Not Delete Artwork Event {item=}")

            try:
                configuration[item]["AutoReact"]
            except KeyError:
                configuration[item]["AutoReact"] = {}

            if "Artwork" in configuration[item]["Channels"]:
                log.debug("Update Artwork")
                chan = str(configuration[item]["Channels"]["Artwork"])
                configuration[item]["AutoReact"] = {}
                configuration[item]["AutoReact"]["Artwork"] = {}
                configuration[item]["AutoReact"]["Artwork"]["Channel"] = [chan]
                configuration[item]["AutoReact"]["Artwork"]["Contains"] = [
                    "author"]
                configuration[item]["AutoReact"]["Artwork"]["Emoji"] = ["❤️"]
                configuration[item]["AutoReact"]["Artwork"]["isExactMatch"] = False
                del configuration[item]["Channels"]["Artwork"]
            if "infoBattles" in configuration[item]["Channels"]:
                log.debug("Update Battles")
                chan = str(configuration[item]["Channels"]["infoBattles"])
                configuration[item]["AutoReact"] = {}
                configuration[item]["AutoReact"]["BattlesThumb"] = {}
                configuration[item]["AutoReact"]["BattlesThumb"]["Channel"] = [
                    chan]
                configuration[item]["AutoReact"]["BattlesThumb"]["Contains"] = [
                    "👍"]
                configuration[item]["AutoReact"]["BattlesThumb"]["Emoji"] = [
                    "👍"]
                configuration[item]["AutoReact"]["BattlesThumb"]["isExactMatch"] = False

                configuration[item]["AutoReact"]["BattlesCheck"] = {}
                configuration[item]["AutoReact"]["BattlesCheck"]["Channel"] = [
                    chan]
                configuration[item]["AutoReact"]["BattlesCheck"]["Contains"] = [
                    "☑️"]
                configuration[item]["AutoReact"]["BattlesCheck"]["Emoji"] = [
                    "☑️"]
                configuration[item]["AutoReact"]["BattlesCheck"]["isExactMatch"] = False

                del configuration[item]["Channels"]["infoBattles"]

            if "ModPreview" in configuration[item]["Events"]:
                try:
                    configuration[item]["Events"]["ModPreview_DeleteTrigger"]
                except KeyError:
                    configuration[item]["Events"]["ModPreview_DeleteTrigger"] = True

    if writeJSON(data=configuration, filename="config.json"):
        log.debug("Updated Config")


class _singleton_(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass(slots=True)
class genericConfig(metaclass=_singleton_):
    """Class for basic bot configuration"""

    def slashList() -> set[int]:
        """Gets guild IDs of all servers it's allowed for + owner guild"""
        configuration = readJSON(filename="config")
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

    @classmethod
    def update(cls):
        "Reassign default class attributes from their source"
        cls.slashServers = cls.slashList()
        "Servers which the bot has a config for and thus can use slash commands"
        if 246190532949180417 in cls.slashServers:
            cls.emoNotifi = "<:notified:427470234463502336>"
        else:
            cls.emoNotifi = "🙃"
        if 246190532949180417 in cls.slashServers:
            "If bot knows guild with above ID, assume bot is prod"
            cls.botID = 762054632510849064
            "ID of the bot"
        else:
            cls.botID = 764270771350142976
            "ID of the bot"
        return True

    emoNotifi = None
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
        _sscConifg = _configuration["General"]["SSC_Data"]
        _tpfConfig = _configuration[str(cls.tpfID)]
        cls.curTheme = _sscConifg["theme"]
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
        cls.themesDict = _sscConifg["allThemes"]
        "Dict of all themes and their notes"
        cls.ignoreWinner = _sscConifg["ignoreWinner"]
        "Flag if to ignore the fact a user has one of the winner roles"
        cls.isPrize = _sscConifg["isPrize"]
        "Flag to indicate if the current round has a prize"

        _genCF = readJSON(filename="config")["General"]
        "General block of config"
        cls.delTime = float(_genCF["delTime"])
        "Time to delay deleting a message"
        return True


screenShotCompConfig.update()


@dataclass(slots=True)
class generalEventConfig(metaclass=_singleton_):
    """Config for the General Events"""

    def getAutoReacts() -> dict[dict]:
        """Gathers all autoReact dicts from config"""
        configuration = readJSON(filename="config")
        autoReactsConfig = {}
        for item in configuration:
            log.debug(f"{item=}")
            if "General" == item:
                continue
            try:
                reactors = configuration[item]["AutoReact"]
                log.debug(f"{reactors=}")
            except Exception:
                log.exception(f"AutoReactCheck")
                continue
            if len(reactors) > 0:
                autoReactsConfig[item] = reactors
        return autoReactsConfig

    def getAutoReactChannels(autoReacts: dict):
        """Gets list of channels that are in autoReacts"""
        log.debug(f"aR, {autoReacts=}")
        reactChans = {}
        # add guild IDs to reactChans
        for guild in autoReacts:
            #log.debug(f"g in aR {guild=}")
            reactChans[guild] = {}
        log.debug(f"rC1, {reactChans=}")
        guild = None

        # add every channel ID that all reactors of a guild to the appropriate guild ID in reactChans
        for G in reactChans:
            #log.debug(f"G in rC, {G=}")
            for reactor in autoReacts[G]:
                #log.debug(f"r in aR[G], {reactor=}")
                chans = autoReacts[G][reactor]["Channel"]
                for C in chans:
                    #log.debug(f"C in chans, {C=}")
                    reactChans[G][C] = set()
        log.debug(f"rC2, {reactChans=}")
        G = reactor = chans = C = None

        # go through each guild in reactChans,
        # get chans from all reactors of same guild in autoReacts,
        # and add to a set under the guild ID in reactChans
        for G in reactChans:
            for reactor in autoReacts[G]:
                #log.debug(f"r in aR[G], {reactor=}")
                chans = autoReacts[G][reactor]["Channel"]
                for element in chans:
                    #log.debug(f"e in chans, {element=}")
                    rS = set(reactChans[G][element])
                    #log.debug(f"rS, {rS=}")
                    rS.add(reactor)
                    reactChans[G][element] = list(rS)
                    #log.debug(f"rC[G][C], {reactChans[G]=}")
        log.debug(f"rC3, {reactChans=}")

        return reactChans

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
            "Artwork",
            "Battles",
            "ReadyMessage",
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
            "ModPreviewGlobal",
            "ModPreview_DeleteTrigger",
            "AutoReact"]
        "All recognised events"
        cls.autoReacts = cls.getAutoReacts()
        log.debug(f"{cls.autoReacts=}")
        cls.autoReactsChans = cls.getAutoReactChannels(cls.autoReacts)
        log.debug(f"{cls.autoReactsChans=}")
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
        if 246190532949180417 in genericConfig.slashServers:
            "If bot knows guild with above ID, assume bot is prod"
            cls.botName = "Katoku"
            "Name of the bot user"
        else:
            cls.botName = "KatokuTest"
            "Name of the bot user"
        return True

    hostProvider = "OVH"
    hostLocation = "Sydney"
    linePyCount = 5124
    lineJSONCount = 1442


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
    channelList: list
    "List of channels"
    channelExtra: any
    "Any extra info related to channel"
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
    commandArg5: any
    "The fifth argument of a command"
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
    messageList: list
    "List of messages"
    messageExtra: any
    "Any additional data related to a message"
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
    emoji: str
    "An emoji"
    emojiObject: nextcord.Emoji
    "An emoji object"
    emojiID: int
    "An ID of an emoji"
    emojiName: str
    "Name of a emoji"
    emojiList: list
    "List of emoji"
    emojiExtra: any
    "Any additional data related to an emoji"
    flag0: bool
    flag1: bool
    flag2: bool
    flag3: bool
    flag4: bool
    flagA: bool
    flagB: bool
    flagC: bool
    flagD: bool
    flagE: bool


genericConfig.update()
screenShotCompConfig.update()
generalEventConfig.update()
botInformation.update()


# secrets
secret = readJSON(directory=["secrets"], filename="nolooky", cache=False)
DISTOKEN = secret["DISCORD_TOKEN"]
STEAMAPI = secret["STEAM_WEB_API"]
NEXUSAPI = secret["NEXUSMODS_API"]
