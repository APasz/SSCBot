import gettext
import inspect
import logging
import math
import os
import platform
from dataclasses import dataclass
from pathlib import Path as Pathy

from util.fileUtil import readJSON, writeJSON, paths

print("Config")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY CONFIG IMPORT MODULES")
    import nextcord
    import psutil
    from nextcord import Locale
    from packaging import version as packVersion
except Exception:
    logSys.exception("CONFIG IMPORT MODULES")

defaultEvents = [
    "ReadyMessage",
    "MemberJoin",
    "MemberJoin_RecentCreation",
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
    "ModPreview_Global",
    "ModPreview_DeleteTrigger",
    "AutoReact",
    "SSC_NotifyRole_Assignment",
]
"For GeneralEvent"


def verifyConfigJSON() -> bool:
    """Checks that certain elements are present and if not, gives a default value.
    Also to be used to update the config when the bot gets an update."""

    configuration = readJSON(file=paths.work.joinpath("config"))
    genCF = configuration
    if not isinstance(genCF["delTime"], int | float) or (genCF["delTime"] > 120):
        genCF["delTime"] = 20

    if not isinstance(genCF["logLevel"], str):
        genCF["logLevel"] = "DEBUG"

    if not isinstance(genCF["purgeLimit"], int | float) or (genCF["purgeLimit"] > 100):
        genCF["purgeLimit"] = 100
    configuration = genCF

    for item in defaultEvents:
        if item not in configuration["Events"]:
            configuration["Events"][item] = True

    for file in paths.conf.iterdir():
        logSys.debug(item)
        if file.stem.isdigit():
            data = {
                "SlashCommands": True,
                "PrefixCommands": True,
                "Config_Name": None,
                "Description": None,
                "MISC": {},
                "Channels": {},
                "Channels_Admin": {},
                "Events": {},
                "Roles": {},
                "AutoReact": {},
            }
            k = readJSON(file=file)
            kata = data | k

            dataMISC = {
                "Prefix": None,
                "Welcome": "{user}, Welcome to {guild}",
                "Rules": "Please keep {rules} in mind",
                "MemberJoin_RecentCreationHours": 48,
                "Language": "en-GB",
            }
            kata["MISC"] = dataMISC | kata["MISC"]

            dataChannels = {
                "Rules": None,
                "Welcome": None,
                "ReadyMessage": None,
                "NewModPreview": None,
                "NewModRelease": None,
            }
            kata["Channels"] = dataChannels | kata["Channels"]

            dataChannels_Admin = {"Admin": None, "Audit": None, "Notify": None}
            kata["Channels_Admin"] = dataChannels_Admin | kata["Channels_Admin"]

            dataEvents = {
                "ReadyMessage": True,
                "MemberJoin": False,
                "MemberJoin_RecentCreation": False,
                "MemberAccept": False,
                "MemberNameChange": False,
                "MemberVerifiedRole": False,
                "MemberKick": False,
                "MemberBan": False,
                "MemberUnban": False,
                "MemberLeave": False,
                "MemberWelcome": False,
                "MessageDelete": False,
                "AutoReact": True,
                "ModPreview": False,
                "ModPreview_Global": False,
                "ModPreview_DeleteTrigger": False,
            }
            kata["Events"] = dataEvents | kata["Events"]

            dataRoles = {
                "Admin": None,
                "Moderator": None,
                "Modder": None,
                "SSC_Notify_General": None,
                "SSC_Notify_Prize": None,
                "SSC_Manager": None,
            }
            kata["Roles"] = dataRoles | kata["Roles"]

            writeJSON(data=kata, file=file, sort=True)

    if writeJSON(data=configuration, file=paths.work.joinpath("config")):
        logSys.debug("Updated Config")
        return True
    else:
        return False


verifyConfigJSON()


async def syncCommands(bot):
    "Force sync all slash commands"
    func = inspect.stack()[1][3]
    logSys.info(f"{func=} | Ensure /Commands Loaded")
    try:
        bot.add_all_application_commands()
        await bot.sync_all_application_commands()
        return True
    except Exception:
        logSys.exception(f"Ensure /Commands")
        return False


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
    def slashList(cls) -> set[int]:
        """Gets guild IDs of all servers it's allowed for + owner guild"""
        slashes = set()
        for file in paths.conf.iterdir():
            if not file.stem.isdigit():
                continue
            slashCF = readJSON(file=file)["SlashCommands"]
            if slashCF:
                slashes.add(int(file.stem))
        slashes.add(cls.ownerGuild)
        return list(slashes)

    @classmethod
    def getGuildLangs(cls) -> dict[str, str]:
        """Gets the configured lang for each guild and adds to dict"""
        langs = {}
        for file in paths.conf.iterdir():
            if not file.stem.isdigit():
                continue
            lang = readJSON(file=file)["MISC"]["Language"]
            if lang:
                langs[file.stem] = lang
            else:
                langs[file.stem] = cls.defaultLang
        return langs

    @classmethod
    def update(cls):
        "Reassign default class attributes from their source"
        cls.slashServers = cls.slashList()
        "Servers which the bot has a config for and thus can use slash commands"
        if 811250905335857172 in cls.slashServers:
            cls.emoNotifi = "<:notified:427470234463502336>"
            cls.botID = 762054632510849064
            cls.Prod = True
        else:
            cls.emoNotifi = "🙃"
            cls.botID = 764270771350142976
            cls.Prod = False

        cls.langs = cls.getGuildLangs()

        configsDir = Pathy().parent.absolute().joinpath("configs")
        cls.GUILD_BOT_PREFIX = {}

        for item in configsDir.iterdir():
            if not (item.stem).isdigit():
                continue
            logSys.debug(f"prefix get {item.stem=} {item=}")
            guildConf = readJSON(file=paths.conf.joinpath(item))
            try:
                prefix = guildConf["MISC"]["Prefix"]
                logSys.debug(f"{prefix=}")
                if prefix is None:
                    prefix = cls.BOT_PREFIX
                cls.GUILD_BOT_PREFIX[int(item.stem)] = prefix
            except Exception:
                logSys.exception(f"guild prefix")
                continue

        return True

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
    "Default prefix the bot listens to"
    GUILD_BOT_PREFIX: dict
    "Guild specific prefixes the bot listens to"
    defaultLang = Locale.en_GB.value
    """Lang to use when only one must be used. /command name for example.
    Must be Nextcord locale"""

    configCommGroupWhitelist = ("Channels", "Channels_Admin", "Roles", "MISC")
    "Groups of the config JSON that are accessible by the configuration command"
    importantFiles = ("facts.json", "missing.png")
    "List of files that are important to the function of the bot but aren't covered by initial startup"
    factsJSON = "facts.json"
    "Name of the file which contains all the facts"
    pingingChan = 1018012984053870622
    "Channel ID to use for API pinging"
    botDir = Pathy().absolute()
    "Real path directory of the bot"
    changelog = "changelog2"
    "Filename of the changelog"

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
    if bi:
        bi = 1024
    else:
        bi = 1000
    if bit:
        byteNum = byteNum * 8
    ratios = "KMGTPEZY"
    try:
        return round(byteNum / math.pow(bi, ratios.index(magnitude.upper()) + 1), 3)
    except Exception:
        log.exception("BytesMag")
        return False


def bytesToHuman(
    byteNum: int, magnitude: str, bi: bool = True, bit: bool = False
) -> str:
    """Turns an int into a friendly notation
    magnitude=['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']"""
    if not isinstance(byteNum, int):
        log.error("BytesHuman, Not INT")
        return False
    nota = "KMGTPEZY"
    magnitude = magnitude.upper()
    if magnitude not in nota:
        log.error("BytesHuman, Not MAG")
        return False
    size = bytesMagnitude(byteNum=byteNum, magnitude=magnitude, bi=bi, bit=bit)
    power = "i" if bi else ""
    length = "B" if bi else "b"
    return f"{size}{magnitude}{power}{length}"


def getGuilds(by: str = "id") -> dict[int, str] | dict[str, int]:
    """Returns dict(ID|ConfigName) of all guilds and their ids"""
    logSys.debug(f"{by=}")
    IDs = {}
    for file in paths.conf.iterdir():
        if not file.stem.isdigit():
            continue
        cfName = readJSON(file=file)["Config_Name"]
        if by == "id":
            try:
                IDs[int(file.stem)] = cfName
            except KeyError:
                pass
            except Exception:
                logSys.exception("Name to ID")
        if by == "name":
            try:
                IDs[cfName] = int(file.stem)
            except KeyError:
                pass
            except Exception:
                logSys.exception("ID to Name")
    logSys.debug(f"{IDs=}")
    return IDs


def getGlobalEventConfig(listAll: bool = False) -> set:
    """Gets list of either all or only globally disabled events"""
    logSys.debug(f"{listAll=}")
    globalEvents = set()
    configuration = readJSON(file=paths.work.joinpath("config"))
    for itemKey, itemVal in configuration["Events"].items():
        # logSys.debug(f"{itemVal}| {itemKey=}")
        if listAll or not itemVal:
            globalEvents.add(str(itemKey))
    logSys.debug(f"{globalEvents=}")
    return globalEvents


def getEventConfig(by: str = "id") -> dict[int, str] | dict[str, str]:
    """Returns list of events allowed per server by either ID or config name."""
    logSys.debug(f"getEventConfigRead {by=}")
    globalEvents = getGlobalEventConfig()
    events = {}
    for file in paths.conf.iterdir():
        if not file.stem.isdigit():
            continue
        servConf = readJSON(file=file)
        cfName = servConf["Config_Name"]
        if by == "name":
            try:
                nameID = cfName
            except Exception:
                logSys.exception("ConfigName to nameID")
        elif by == "id":
            try:
                nameID = int(file.stem)
            except Exception:
                logSys.exception("ConfigID to nameID")
        eventList = []
        for elementKey, elementVal in servConf["Events"].items():
            if (elementKey not in globalEvents) and elementVal:
                eventList.append(elementKey)
            events[nameID] = eventList
    return events


@dataclass(slots=True)
class generalEventConfig(metaclass=_singleton_):
    """Config for the General Events"""

    def getNameID(k: list | tuple | set, name: bool = True) -> str | int:
        "Returns the first str or first int"
        if name:
            typ = str
        else:
            typ = int
        if not isinstance(k, list | tuple | set):
            return k
        for e in k:
            print(type(e), e)
            if isinstance(e, typ):
                return e
        return False

    def getAutoReacts() -> dict[int, dict]:
        """Gathers all autoReact dicts from config"""
        autoReactsConfig = {}
        for file in paths.conf.iterdir():
            if not file.stem.isdigit():
                continue
            logSys.debug(f"{file.stem=}")
            servConf = readJSON(file=file)
            try:
                reactors = servConf["AutoReact"]
                logSys.debug(f"{reactors=}")
            except Exception:
                logSys.exception(f"AutoReactCheck")
                continue
            if len(reactors) > 0:
                autoReactsConfig[int(file.stem)] = reactors
        return autoReactsConfig

    def getAutoReactChannels(autoReacts: dict) -> dict[int]:
        """Gets list of channels that are in autoReacts"""
        logSys.debug(f"aR, {autoReacts=}")
        reactChans = {}
        # add guild IDs to reactChans
        for guild in autoReacts:
            # logSys.debug(f"g in aR {guild=}")
            reactChans[int(guild)] = {}
        logSys.debug(f"rC1, {reactChans=}")
        guild = None

        # add every channel ID that all reactors of a guild to the appropriate guild ID in reactChans
        for G in reactChans:
            G = int(G)
            # logSys.debug(f"G in rC, {G=}")
            for reactor in autoReacts[G]:
                # logSys.debug(f"r in aR[G], {reactor=}")
                chans = autoReacts[G][reactor]["Channel"]
                for C in chans:
                    C = generalEventConfig.getNameID(C, name=False)
                    # logSys.debug(f"C in chans, {C=}")
                    reactChans[G][C] = set()
        logSys.debug(f"rC2, {reactChans=}")
        G = reactor = chans = C = None

        # go through each guild in reactChans,
        # get chans from all reactors of same guild in autoReacts,
        # and add to a set under the guild ID in reactChans
        for G in reactChans:
            G = int(G)
            for reactor in autoReacts[G]:
                # logSys.debug(f"r in aR[G], {reactor=}")
                chans = autoReacts[G][reactor]["Channel"]
                for element in chans:
                    element = generalEventConfig.getNameID(element, name=False)
                    # logSys.debug(f"e in chans, {element=}")
                    rS = set(reactChans[G][element])
                    # logSys.debug(f"rS, {rS=}")
                    rS.add(reactor)
                    reactChans[G][element] = list(rS)
                    # logSys.debug(f"rC[G][C], {reactChans[G]=}")
        logSys.debug(f"rC3, {reactChans=}")

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
        cls.eventConfigID = getEventConfig(by="id")
        "getEventConfig by ID"
        cls.eventConfigName = getEventConfig(by="name")
        "getEventConfig by Name"
        cls.globalEvent = getGlobalEventConfig(listAll=False)
        "getGlobalEvent | only disabled"
        cls.globalEventAll = getGlobalEventConfig(listAll=True)
        "getGlobalEvent | listAll"
        cls.defaultEvents = defaultEvents
        "All recognised events"
        cls.autoReacts = cls.getAutoReacts()
        # logSys.debug(f"{cls.autoReacts=}")
        cls.autoReactsChans = cls.getAutoReactChannels(cls.autoReacts)
        logSys.debug(f"{cls.autoReactsChans=}")
        return True


generalEventConfig.update()


@dataclass(slots=True)
class botInformation(metaclass=_singleton_):
    """Store various bits of info about the bot and what it's running on"""

    @classmethod
    def verParse(cls, data: str) -> packVersion:
        "Packing.version.parse function. False on InvalidVersion, else return arg"
        try:
            return packVersion.parse(str(data))
        except packVersion.InvalidVersion:
            logSys.exception("Version.parse Invalid")
            return False
        except Exception:
            log.exception(f"Version.parse")
            return data

    @classmethod
    def _parseVer(cls) -> packVersion:
        "Gets latest version as verison object and attaches extra bits of info"
        _cgLog = readJSON(file=paths.work.joinpath(genericConfig.changelog))
        _BotVer = "2"
        _allMajor = list(_cgLog.keys())
        _min = str(_allMajor[0])
        _mic = str(list(_cgLog[_min].keys())[1])
        logSys.debug(f"BotVer: {_BotVer=}.{_min=}.{_mic=}")
        _var = cls.verParse(f"{_BotVer}.{_min}.{_mic}")
        _var.title = _cgLog[_min]["Title"]
        "Name current version"
        _var.date = _cgLog[_min][_mic][0]
        "Date current released"

        def listVer() -> list:
            _verList = []
            for _minVer in _cgLog:
                for _micVer in _cgLog[_minVer]:
                    if _micVer.isdigit():
                        _verList.append(f"{_BotVer}.{_minVer}.{_micVer}")
            return _verList

        _var.all = listVer()

        return _var

    @classmethod
    def update(cls):
        "Reassign default class attributes from their source"

        cls.version = cls._parseVer()
        "Packing.version object with extras"

        cls.nextcordVer = nextcord.__version__
        "Version of Nextcord installed"
        cls.hostname = platform.node()
        "Hostname/Network-name of host"
        cls.hostOS = f"{platform.system()}"
        "Operating System of host"
        cls.hostPython = platform.python_version()
        "Version of Python installed"
        cls.hostRAM = bytesToHuman(
            byteNum=(int(psutil.virtual_memory().total)), magnitude="G"
        )
        "Total RAM in GiB of host system | Includes notation"
        cls.hostCores = psutil.cpu_count(logical=True)
        "Number of logical cores host has"
        cls.hostCPUfreq = psutil.cpu_freq()
        "Frequency of host CPU"
        if 246190532949180417 in genericConfig.slashServers:
            "If bot knows guild with above ID, assume bot is prod"
            cls.botName = "Katoku"
            "Name of the bot user"
        else:
            cls.botName = "KatokuTest"
            "Name of the bot user"
        logSys.info(cls.botName)
        return True

    processPID = os.getpid()
    "Current process ID"
    hostProvider = "OVH"
    "Provider of the hardware"
    hostLocation = "Sydney"
    "Where is the hardware"
    linePyCount = 6000
    "Appox count of Python lines"
    lineJSONCount = 1757
    "Appox count of JSON lines"
    repoLink = "https://github.com/APasz/SSCBot"
    repoNice = f"[Github]({repoLink})"

    @classmethod
    def memMiB(cls):
        try:
            processBot = psutil.Process(cls.processPID)
            memB = processBot.memory_info().rss
            return bytesToHuman(byteNum=memB, magnitude="M")
        except Exception:
            log.exception("InfoCommand_mem")
            return "*undefined*"


botInformation.update()


@dataclass(slots=True)
class screenShotCompConfig(metaclass=_singleton_):
    """Common data for the SSC"""

    @classmethod
    def update(cls):
        "Reassign default class attributes from their source"
        cls.tpfID = int(getGuilds(by="name")["TPFGuild"])
        "ID of the TPF|Gloabal server"
        _configuration = readJSON(file=paths.work.joinpath("config"))
        _sscConifg = _configuration["SSC_Data"]
        if "test" in botInformation.botName.lower():
            ID = str(genericConfig.ownerGuild)
        else:  # TODO ssc rewrite
            ID = "246190532949180417"
        _tpfConfig = readJSON(file=paths.conf.joinpath(ID))
        cls.curTheme = _sscConifg["theme"]
        "The current theme of the competition"
        cls.sscmanager = int(_tpfConfig["Roles"]["SSC_Manager"])
        "ID of the SSCManager role"
        cls.winner = int(_tpfConfig["Roles"]["SSC_Winner"])
        "ID of the SSC Winner role"
        cls.winnerPrize = int(_tpfConfig["Roles"]["SSC_WinnerPrize"])
        "ID of the SSC Prize Winner role"
        cls.runnerUp = int(_tpfConfig["Roles"]["SSC_Runnerup"])
        "ID of the SSC Runnerup role"
        cls.remindChan = int(_tpfConfig["Channels"]["SSC_Remind"])
        "Channel competition reminder should be sent"
        cls.sscChan = int(_tpfConfig["Channels"]["SSC_Comp"])
        "Channel the competition takes place"
        cls.TPFssChan = int(_tpfConfig["Channels"]["ScreenshotsTPF"])
        "Channel where TpF screenshots should go "
        cls.OGssChan = int(_tpfConfig["Channels"]["ScreenshotsGames"])
        "Channel where non-TpF screenshots should go"
        cls.themesDict = _sscConifg["allThemes"]
        "Dict of all themes and their notes"
        cls.ignoreWinner = _sscConifg["ignoreWinner"]
        "Flag if to ignore the fact a user has one of the winner roles"
        cls.isPrize = _sscConifg["isPrize"]
        "Flag to indicate if the current round has a prize"

        _genCF = readJSON(file=paths.work.joinpath("config"))
        "General block of config"
        cls.delTime = float(_genCF["delTime"])
        "Time to delay deleting a message"
        return True


screenShotCompConfig.update()


@dataclass(slots=True)
class localeConfig(metaclass=_singleton_):
    """Class for locale stuffs"""

    sameyLangs = {"en": [Locale.en_GB, Locale.en_US]}
    """Locales that are interchangable. English GB and US for example
    common locale : [nextcord.Locale]
    The first in the list will be the one used if a specific locale is required"""

    localeDict = {}

    _localePath = Pathy().parent.absolute().joinpath("locale")
    _enLoc = _localePath.joinpath("en", "LC_MESSAGES", "base.po")

    @classmethod
    def _findPOfiles(cls):
        "Look for po files and add their locale code to a dict with gettext.translation"

        cls._localGettext = {}
        for file in cls._localePath.iterdir():
            itemPO = file.joinpath("LC_MESSAGES", "base.po")
            print(itemPO)
            lang = str(file.stem)
            if not itemPO.exists():
                logSys.error(f"Missing base.po file {lang=}")
                continue
            trans = gettext.translation(
                domain="base", localedir=cls._localePath, languages=[lang]
            )
            langs = []
            if lang[:2] in cls.sameyLangs:
                for item in cls.sameyLangs[lang[:2]]:
                    if isinstance(item, Locale):
                        langs.append(str(item.value))
                    else:
                        langs.append(str(item))
            else:
                langs.append(lang)
            for element in langs:
                cls._localGettext[element] = trans
        logSys.debug(f"{cls._localGettext=}")

    @classmethod
    def _findEnMSGID(cls):
        "Get all MSGIDs from the en po file and add to the localeDict with empty dict"
        with cls._enLoc.open("r") as file:
            file = file.read().splitlines()
            for stringKey in file:
                if stringKey.startswith("msgid") and len(stringKey) > 8:
                    stringKey = stringKey.removeprefix('msgid "').removesuffix('"')
                    cls.localeDict[stringKey] = {}
        # logSys.debug(f"{cls.localeDict=}")

    @classmethod
    def _buildLocaleDict(cls):
        "Using the gettext from _findPOfiles, fill localeDict empty dicts with locale code and translated text"
        defLang = genericConfig.defaultLang
        langList = []
        for stringKey in cls.localeDict:
            for item in Locale:
                lang = item.value
                if lang not in langList:
                    langList.append(lang)

                # if the translation doesn't exist, fetch default lang translation
                if lang in cls._localGettext:
                    stringValue = cls._localGettext[lang].gettext(stringKey)
                else:
                    stringValue = cls._localGettext[defLang].gettext(stringKey)
                stringValue: str

                # gettext returns stringKey if there is no value, fetch default lang translation                #
                if stringKey == stringValue and lang != defLang:
                    stringValue = cls._localGettext[defLang].gettext(stringKey)

                # Ensure name and title translations fit Discord's 32 char limit
                if stringKey.endswith(("NAME")):
                    stringValue = stringValue.casefold()[:32]
                    stringValue = stringValue.replace(" ", "_")
                if stringKey.endswith(("TITLE")):
                    stringValue = stringValue[:32]

                cls.localeDict[stringKey][lang] = stringValue

        logSys.debug(f"locs: {langList}")
        writeJSON(
            data={"dict": cls.localeDict, "lang": langList},
            file=paths.work.joinpath("localeDict"),
        )
        # logSys.debug(f"locDict: {cls.localeDict=}")

    @classmethod
    def getLC(cls, key: str, lang: str = False) -> str:
        "Returns dict of all locale codes with translated text for specified key"
        # func = inspect.stack()[1][3]
        # logSys.debug(f"{func=} | {key=} | {lang=}")
        if key is None:
            return "***undefined***"
        if key.upper() in cls.localeDict:
            cls.localeDict: dict[str, dict[str, str]]
            if lang:
                if lang in cls.sameyLangs:
                    lang = cls.sameyLangs[lang][0].value
                k = cls.localeDict[key.upper()][lang]
            else:
                k = cls.localeDict[key.upper()]
        else:
            k = key.lower()[:32]
        # logSys.debug(f"{k=}")
        return k

    def getGuildLC(guildID: int | str) -> str:
        "With an id, retrieves the configured lang for the guild"
        func = inspect.stack()[1][3]
        logSys.debug(f"{func=} | {guildID=}")
        guildID = str(guildID)
        lang = None
        if int(guildID) in genericConfig.slashServers:
            lang = readJSON(file=paths.conf.joinpath(guildID))["MISC"]["Language"]
        if lang:
            return lang
        else:
            return genericConfig.defaultLang

    @classmethod
    def update(cls):
        "Reassign default class attributes from their source"
        if paths.work.joinpath("localeDict").exists():
            cached = readJSON(file=paths.work.joinpath("localeDict"), cache=False)
            if len(cached) > 0:
                cls.localeDict = cached["dict"]
                cls.langList = cached["lang"]
                logSys.info("Using Cached localeDict")
                return
        cls._findPOfiles()
        cls._findEnMSGID()
        cls._buildLocaleDict()


localeConfig.update()


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
secret = readJSON(file=paths.secret.joinpath("nolooky"), cache=False)
DISTOKEN = secret["DISCORD_TOKEN"]
STEAMAPI = secret["STEAM_WEB_API"]
NEXUSAPI = secret["NEXUSMODS_API"]
