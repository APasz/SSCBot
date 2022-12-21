import asyncio
import logging
import re
import textwrap
from dataclasses import dataclass

from config import generalEventConfig as geConfig
from config import genericConfig as gxConfig
from config import localeConfig as lcConfig
from config import bytesToHuman
from util.apiUtil import nexusModGet, parseURL, steamUsrGet, steamWSGet, tpfnetModGet
from util.genUtil import getChan, getCol, commonData

print("CogModding")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY MODDING IMPORT MODULES")
    import nextcord
    from nextcord.ext import commands
except Exception:
    logSys.exception("MODDING IMPORT MODULES")

_ = lcConfig.getLC

steam = "steam"
nexus = "nexus"
tpfnet = "tpfnet"


class modding(commands.Cog, name="Modding"):
    """Class containing commands and functions related to game modding"""

    tpfID = int(geConfig.guildListName["TPFGuild"])
    globalPreviewChan = int(getChan(guild=tpfID, chan="NewModPreview"))

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logSys.debug(
            f"""{self.__cog_name__} Ready\n{self.globalPreviewChan=} | {self.tpfID=}"""
        )

    @classmethod
    def _findURL(cls, content: list) -> dict | None:
        """Find any URLs within the message content.\n
        {content} is message.content split at space"""
        logSys.debug("Finding URLs")

        URLs = {}
        for item in content:
            if not re.search(r"https:", item):
                continue
            urlDict = parseURL(item)
            try:
                if urlDict["platform"] == tpfnet:
                    if not re.search(r"filebase", item):
                        continue
                URLs[urlDict["ID"]] = urlDict
            except Exception:
                log.exception(f"urlDict")
                continue

        uLen = len(URLs)
        if uLen == 0:
            URLs = None
        logSys.debug(f"{uLen} {URLs=}")
        return URLs

    @classmethod
    async def _fetchDets(cls, URLs: dict, lang: str) -> dict:
        """Fetches file details from the appropriate service and returns the details in a dict"""
        logSys.debug(f"Fetching Details for {len(URLs)} dets | {lang=}")

        URLdets = {}

        def checkDets(typ: str, details: dict) -> bool:
            logSys.debug("Checking Details")
            if isinstance(details, int):
                log.error(f"{typ} | {ID=} | {dets=}")
                URLdets[ID] = dets
                return False
            return True

        for ID in URLs:
            ID: int
            game: str = URLs[ID]["game"]
            platform: str = URLs[ID]["platform"]
            logSys.debug(f"Fetch: {ID=} | {game=} | {platform=}")
            creator = {}
            if platform == steam:
                dets = steamWSGet(wsID=ID)
                if not checkDets("steamWS", dets):
                    continue
                creator = int(dets["creator"])
                creator = steamUsrGet(creator)
                if not checkDets("steamUsr", dets):
                    continue

            elif platform == nexus:
                dets = nexusModGet(game=game, modID=ID)
                if not checkDets(nexus, dets):
                    continue

            elif platform == tpfnet:
                # dets = tpfnetModGet(ID)
                dets = {"ID": ID, "name": game}
                # if not checkDets("nexus", dets):
                #    continue

            URLdets[ID] = dets | creator | {"platform": platform}
            if len(URLs) >= 2:  # Just to ensure ratelimits aren't hit
                await asyncio.sleep(0.25)
        logSys.debug(f"{URLdets=}")
        return URLdets

    @dataclass(slots=True)
    class modDetails:
        "Details of a mod"

        authorName: str = None
        "Name of the person who created the mod"
        authorID: int = None
        "ID of the author"
        authorURL: str = None
        "URL to the author's profile page"
        authorIcon: str = None
        "URL to the author's avatar"
        modName: str = None
        "Name of the mod"
        modID: int = None
        "ID of the mod"
        modURL: str = None
        "URL to the mod page"
        modThumb: str = None
        "URL to the mod's main/preview image"
        modDesc: str = None
        "Description of the mod"
        modFileSize: int = None
        "Number of bytes the mod is"
        modVersion: str = None
        "Version of the mod"
        tags: list = None
        "List of tags attached to the mod"
        modTags: str = None
        "Stringified tags list joined with ', '"
        createdAt: int = None
        "Unix timestamp of when the mod was uploaded"
        updatedAt: int = None
        "Unix timestamp of when the mod was last updated"
        platform: str = None
        "Platform the mod is hosted on"
        gameName: str = None
        "The game the mod belongs to"
        gameID: int = None
        "ID of the game the mod belongs to"
        NSFW: bool = False
        "Whether the mod is NSFW or not"
        public: bool = True
        "Whether the mod is actually public. Mainly just to inform user if not public"

    @classmethod
    def _sortDets_steam(cls, detsDict: dict) -> modDetails:
        logSys.debug(f"Sorting Steam {detsDict}")

        dets = cls.modDetails()

        dets.platform = steam

        dets.createdAt = detsDict["time_created"]
        dets.updatedAt = detsDict["time_updated"]

        dets.modName = detsDict["title"]
        dets.modFileSize = detsDict["file_size"]
        dets.modID = detsDict["publishedfileid"]
        dets.modThumb = detsDict["preview_url"]

        dets.gameID = detsDict["consumer_app_id"]

        dets.authorName = detsDict["personaname"]
        dets.authorIcon = detsDict["avatarmedium"]
        dets.authorURL = detsDict["profileurl"]
        dets.authorID = detsDict["creator"]

        dets.public = not bool(detsDict["visibility"])

        modTags = []
        for tag in detsDict["tags"]:
            k = tag["tag"]
            modTags.append(k)
        if len(modTags) > 0:
            dets.tags = modTags

        markTags = [
            "[h1]",
            "[/h1]",
            "[h2]",
            "[/h2]",
            "[b]",
            "[/b]",
            "[i]",
            "[/i]",
            "[strike]",
            "[/strike]",
            "[spoiler]",
            "[/spoiler]",
            "[noparse]",
            "[/noparse]",
            "[hr]",
            "[/hr]",
            "[list]",
            "[/list]",
            "[*]",
            "[code]",
            "[/code]",
            "[u]",
            "[/u]",
            "[img]",
            "[/img]",
        ]
        desc = detsDict["description"]
        for tag in markTags:
            desc = desc.replace(tag, "")

        dets.modDesc = textwrap.shorten(desc, width=500, placeholder="...")

        dets.modURL = (
            f"https://steamcommunity.com/sharedfiles/filedetails/?id={dets.modID}"
        )

        logSys.debug(dets)
        return dets

    @classmethod
    def _sortDets_nexus(cls, detsDict: dict[dict]) -> modDetails:
        logSys.debug(f"Sorting Nexus {detsDict}")

        dets = cls.modDetails()

        dets.platform = nexus

        dets.createdAt = detsDict["created_timestamp"]
        dets.updatedAt = detsDict["updated_timestamp"]

        dets.modName = detsDict["name"]
        dets.modID = detsDict["mod_id"]
        dets.modThumb = detsDict["picture_url"]
        dets.modVersion = detsDict["version"]

        dets.gameName = detsDict["domain_name"]
        dets.gameID = detsDict["game_id"]

        dets.authorName = detsDict["author"]
        dets.authorURL = detsDict["uploaded_users_profile_url"]
        dets.authorID = detsDict["user"]["member_id"]

        dets.NSFW = bool(detsDict["contains_adult_content"])

        dets.public = bool(detsDict["available"])

        tagRM = re.compile(r"<[^>]+>")
        dets.modDesc = tagRM.sub("", detsDict["summary"])

        dets.modURL = f"https://www.nexusmods.com/{dets.gameName}/mods/{dets.modID}"

        logSys.debug(dets)
        return dets

    @classmethod
    def _sortDets_tpfnet(cls, detsDict: dict[dict]) -> modDetails:
        logSys.debug(f"Sorting tpf|net {detsDict}")

        dets = cls.modDetails()

        dets.platform = tpfnet

        dets.modID = detsDict["ID"]
        dets.modName = ((detsDict["name"]).replace("-", " ")).removesuffix("/")
        dets.modDesc = (
            "tpf|net is not currently supported but here is an embed anyway :)"
        )
        dets.modURL = (
            f"https://www.transportfever.net/filebase/index.php?entry/{dets.modID}"
        )

        dets.NSFW = False

        dets.public = True

        logSys.debug(dets)
        return dets

    @classmethod
    def _buildEmbed(cls, dets: modDetails, lang: str, cd: commonData) -> nextcord.Embed:
        """Takes a single detsDict and builds an embed with the lang"""
        logSys.debug(f"Build Embed {lang=} | modID: {dets.modID}")

        if isinstance(dets.tags, list):
            if len(dets.tags) != 0:
                for index, item in enumerate(dets.tags):
                    dets.tags[index] = item.title()
                dets.modTags = ", ".join(dets.tags)
        else:
            dets.tags = []

        if "Map" in dets.tags or "Savegame" in dets.tags:
            modType = _("MODDING_PREVIEW_TYPE_MAP", lang)
        else:
            modType = _("MODDING_PREVIEW_TYPE_MOD", lang)

        titles = {
            steam: "MODDING_PREVIEW_STEAM_TITLE",
            nexus: "MODDING_PREVIEW_NEXUS_TITLE",
            tpfnet: "MODDING_PREVIEW_TPFNET_TITLE",
        }
        title = f"{_(titles[dets.platform], lang).format(type=modType)}\n{dets.modName}"

        emb = nextcord.Embed(title=title, colour=getCol(dets.platform), url=dets.modURL)
        logSys.debug("Embed Initial")

        if dets.authorName and dets.authorURL and dets.authorIcon:
            emb.set_author(
                name=dets.authorName, url=dets.authorURL, icon_url=dets.authorIcon
            )
        elif (dets.authorName and dets.authorURL) and not dets.authorIcon:
            emb.set_author(name=dets.authorName, url=dets.authorURL)
        elif dets.authorName and not (dets.authorURL and dets.authorIcon):
            emb.set_author(name=dets.authorName)
        else:
            pass

        if dets.modDesc:
            emb.add_field(
                name=_("MODDING_PREVIEW_DESC_TITLE", lang),
                value=f"\n```\n{dets.modDesc}\n```",
                inline=False,
            )

        if cd.authorNote:
            emb.add_field(
                name=_("MODDING_PREVIEW_AUTHORNOTE_TITLE", lang),
                value=f"\n```\n{cd.authorNote}\n```",
                inline=False,
            )

        if dets.createdAt:
            emb.add_field(
                name=_("MODDING_PREVIEW_PUBLISHED_TITLE", lang),
                value=f"<t:{dets.createdAt}:R>",
                inline=True,
            )
            if dets.updatedAt:
                if dets.createdAt != dets.updatedAt:
                    emb.add_field(
                        name=_("MODDING_PREVIEW_UPDATED_TITLE", lang),
                        value=f"<t:{dets.updatedAt}:R>",
                        inline=True,
                    )

        if dets.modTags:
            emb.add_field(
                name=_("MODDING_PREVIEW_TAGS_TITLE", lang),
                value=dets.modTags,
                inline=False,
            )
        if cd.imageURL:
            dets.modThumb = cd.imageURL
        if dets.modThumb:
            emb.set_image(url=dets.modThumb)

        if dets.NSFW:
            emb.set_image(None)
            emb.insert_field_at(
                index=1,
                name=_("MODDING_PREVIEW_NSFW_TITLE", lang),
                value=_("TRUE", lang),
                inline=False,
            )

        if dets.modFileSize:
            mib = bytesToHuman(byteNum=dets.modFileSize, magnitude="M")
            txt = _("MODDING_PREVIEW_FILESIZE_TITLE", lang)
            emb.set_footer(text=txt.format(size=mib))

        logSys.debug("Embed Built")
        return emb

    async def modRelease(self, ctx, cd: commonData):
        "Parse URLs"
        logSys.debug(f"{cd.intGuild=} | {cd.chanID_Name}")

        cd.globalPreview = False
        if "ModPreview_Global" in geConfig.eventConfigID[cd.intGuild]:
            if cd.previewChan != self.globalPreviewChan:
                cd.globalPreview = True

        cd.content = ctx.content.replace("\n", " ").split(" ")

        cd.URLs: dict = self._findURL(cd.content)
        if cd.URLs is None:
            logSys.info("URLs None")
            return False
        logSys.debug(f"{len(cd.URLs)} URLs Found")

        firstID: str = list(cd.URLs.keys())[0]
        firstURL = cd.URLs[firstID]["url"]
        print(firstURL)

        cd.authorNote: str = ""
        cd.authorNote: str = ctx.content.split(firstURL)[0]
        logSys.debug(f"authorNote {len(cd.authorNote) > 0}")
        for element in (firstURL, " ", ":", ";", ".", "|"):
            cd.authorNote = cd.authorNote.removesuffix(element)
        if not len(cd.authorNote) > 0:
            cd.authorNote = None

        detailsDict = {}
        detailsDict[cd.locale] = await self._fetchDets(URLs=cd.URLs, lang=cd.locale)
        if cd.locale != gxConfig.defaultLang:
            detailsDict[gxConfig.defaultLang] = await self._fetchDets(
                URLs=cd.URLs, lang=gxConfig.defaultLang
            )
        logSys.debug("DetailsDict")

        for lang in detailsDict:
            for item in detailsDict[lang]:
                dd = detailsDict[lang][item]
                if not isinstance(dd, dict):
                    logSys.warning(f"dd not dict: {type(dd)}")
                    continue
                if dd["platform"] == steam:
                    detailsDict[lang][item] = self._sortDets_steam(dd)
                elif dd["platform"] == nexus:
                    detailsDict[lang][item] = self._sortDets_nexus(dd)
                elif dd["platform"] == tpfnet:
                    detailsDict[lang][item] = self._sortDets_tpfnet(dd)
        logSys.debug(f"{len(detailsDict[cd.locale])} fileDetails ready")
        localEmb = []
        globalEmb = []
        for modDets in detailsDict[cd.locale]:
            localEmb.append(
                self._buildEmbed(
                    dets=detailsDict[cd.locale][modDets], lang=cd.locale, cd=cd
                )
            )
        if cd.globalPreview:
            for modDets in detailsDict[gxConfig.defaultLang]:
                globalEmb.append(
                    self._buildEmbed(
                        dets=detailsDict[gxConfig.defaultLang][modDets],
                        lang=gxConfig.defaultLang,
                        cd=cd,
                    )
                )
        logSys.debug(f"{len(localEmb)}|{len(globalEmb)} Local|Global Embeds Ready.")
        prevChan = self.bot.get_channel(cd.previewChan)
        for emb in localEmb:
            try:
                await prevChan.send(embed=emb)
            except Exception:
                log.exception(f"Send Local Emb")
        logSys.debug("Local Emb Sent")
        if cd.globalPreview:
            prevChan = self.bot.get_channel(self.globalPreviewChan)
            for emb in globalEmb:
                try:
                    await prevChan.send(embed=emb)
                except Exception:
                    log.exception(f"Send Global Emb")
            logSys.debug("Global Emb Sent")
        return True

    @commands.Cog.listener()
    async def on_message(self, ctx):
        """Check for modRelease"""
        await self.bot.wait_until_ready()
        if not gxConfig.Prod:
            return
        if ctx.guild is None:
            return
        cd = commonData(ctx)
        if cd.intUser == gxConfig.botID:
            print(f"User Match BotID | User: {cd.intUser} Bot: {gxConfig.botID}")
            return
        cfName = "**"
        if cd.intGuild in geConfig.guildListID:
            cfName = geConfig.guildListID[cd.intGuild]

        log.debug(
            f"GE_on_message; {cfName}: {cd.intGuild=} | {cd.chanID_Name} | {cd.userID_Name}"
        )
        event = False

        if "ModPreview" in geConfig.eventConfigID[cd.intGuild]:
            nmrChan = int(getChan(cd.intGuild, "NewModRelease"))
            log.debug(f"{nmrChan=} {cd.intChan == nmrChan} | bot {ctx.author.bot}")
            if (cd.intChan == nmrChan) and (ctx.author.bot is False):
                cd.previewChan = int(getChan(cd.intGuild, "NewModPreview"))
                cd.image = None
                if len(ctx.attachments) != 0:
                    attach = ctx.attachments[0]
                    if attach.content_type.startswith("image"):
                        cd.imageURL = attach.url
                okSend = await self.modRelease(ctx=ctx, cd=cd)
                if not okSend:
                    return
                delTrig = False
                if "ModPreview_DeleteTrigger" in geConfig.eventConfigID[cd.intGuild]:
                    delTrig = True
                logSys.info(f"modReleaseSent | {delTrig=} {okSend=}")
                if delTrig and okSend:
                    try:
                        await ctx.delete()
                    except Exception:
                        logSys.exception(f"Delete Trig")
                event = True

        if not event:
            log.debug(f"GE on_message: No event.")


def setup(bot: commands.Bot):
    bot.add_cog(modding(bot))


# MIT APasz
