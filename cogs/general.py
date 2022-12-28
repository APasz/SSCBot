import logging
import random
import time

print("CogGeneral")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")


try:
    logSys.debug("TRY GENERAL IMPORT MODUELS")
    import nextcord
    import pint
    import psutil
    from nextcord import Embed, Interaction, SlashOption, slash_command
    from nextcord.ext import commands

    from config import botInformation as botInfo
    from config import genericConfig as gxConfig
    from config import localeConfig as lcConfig
    from util.fileUtil import paths, readJSON
    from util.genUtil import (
        _ping,
        blacklistCheck,
        commonData,
        formatTime,
        getCol,
        getServConf,
    )
    from util.views import factSubmit
except Exception:
    logSys.exception("GENERAL IMPORT MODUELS")

_ = lcConfig.getLC


class general(commands.Cog, name="General"):
    """Class containing commands that aren't for bot management or inherently related to TpF"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logSys.debug(f"{self.__cog_name__} Ready")

    @slash_command(
        name="submitfact",
        guild_ids=gxConfig.slashServers,
        # default_member_permissions=Permissions(manage_messages=True),
    )
    async def factAdd(self, interaction: nextcord.Interaction):
        """Submit a fact related to transportation, Transport Fever, or Urban Games."""
        try:
            await interaction.response.send_modal(modal=factSubmit())
        except Exception:
            log.exception(f"Fact Submit Modal")

    async def factGet(
        self,
        cd: commonData,
        index: int = -1,
        metadata: bool = False,
    ) -> str | nextcord.Embed:
        """Retrieves a fact from the facts JSON file."""
        log.debug(f"run| {index=}| {metadata=}")
        data = f"'An error occurred' Alert <@{gxConfig.ownerID}>"
        if facts := readJSON(file=paths.work.joinpath(gxConfig.factsJSON)):
            keys = list(facts.keys())
        else:
            return data

        index = str(index)
        if index == "-1":
            index = str(random.choice(keys))
        elif (len(index) != 3) and index.isdigit():
            index = index.zfill(3)
            if index not in keys:
                index = str(random.choice(keys))
        factDic = facts[index]
        log.debug(str(factDic))
        ID = _("COMM_FACT_ID", cd.locale).format(index=index)
        # TODO support content in multiple languages.
        content = factDic["content"]
        source = factDic["source"]
        sourceLink = factDic["sourceLink"]
        extraLinks = factDic["extraLinks"]
        initialAdd = factDic["initialAdd"]
        lastUpdate = factDic["lastUpdate"]
        providerID = factDic["providerID"]
        if providerID is None:
            providerID = "*Not avaliable*"
        providerName = factDic["providerName"]
        if providerName is None:
            providerName = "*Not avaliable*"
        if source is None and sourceLink is None:
            source = "Someone forgot the source."
        if sourceLink is None:
            data = nextcord.Embed(title=ID, description=content, colour=getCol("fact"))
        else:
            data = nextcord.Embed(
                title=ID, description=content, colour=getCol("fact"), url=sourceLink
            )
        if source and sourceLink:
            source = f"Source;\n{source}\n{sourceLink}"
        elif sourceLink and not source:
            source = "Source;\n" + sourceLink
        elif not sourceLink and source:
            source = "Source;\n" + source
        data.set_footer(text=source)
        if len(extraLinks) > 0:
            extraLinks = "\n".join(extraLinks)
            data.add_field(name="Extra Links", value=extraLinks, inline=False)
        if metadata:
            txt = [
                f"Provider Name|ID: {providerName} | {providerID}",
                f"Date Added|Updated: {initialAdd} | {lastUpdate}",
            ]
            data.add_field(
                name="Metadata",
                value="\n".join(txt),
            )
        return data

    @commands.command(name="fact", aliases=["randomFact"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def factCommand(
        self, ctx: commands.Context, index: int = -1, metadata: bool = False
    ):
        """Serves Random Facts"""
        log.debug("factCommand")
        async with ctx.typing():
            cd = commonData(ctx)
            fact = await self.factGet(cd=cd, index=index, metadata=metadata)
            try:
                if isinstance(fact, Embed):
                    await ctx.send(embed=fact)
                else:
                    await ctx.send(fact)
            except Exception:
                log.exception("factCOMM")
            log.info(f"Fact: {cd.userID_Name}")

    @slash_command(
        name=_("COMM_FACT_NAME", gxConfig.defaultLang),
        name_localizations=_("COMM_FACT_NAME"),
        description=_("COMM_FACT_DESC", gxConfig.defaultLang),
        description_localizations=_("COMM_FACT_DESC"),
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def factSlash(
        self,
        interaction: Interaction,
        index: int = SlashOption(
            name=_("COMM_FACT_INDEX_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_FACT_INDEX_NAME"),
            description=_("COMM_FACT_INDEX_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_FACT_INDEX_DESC"),
            required=False,
            default=-1,
        ),
        metadata: bool = SlashOption(
            name=_("COMM_FACT_METADATA_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_FACT_METADATA_NAME"),
            description=_("COMM_FACT_METADATA_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_FACT_METADATA_DESC"),
            required=False,
            default=bool(False),
        ),
    ):
        """Serves Random Facts"""
        if not await blacklistCheck(ctx=interaction, blklstType="gen"):
            return
        log.debug("factSlash")
        cd = commonData(interaction)
        fact = await self.factGet(cd=cd, index=index, metadata=metadata)
        try:
            if isinstance(fact, Embed):
                await interaction.response.send_message(embed=fact)
            else:
                await interaction.response.send_message(fact)
        except Exception:
            log.exception("factSLASH")
        log.info(f"Fact: {cd.userID_Name}")

    async def pingDo(self, ctx, api: bool, testNum: int, cd: commonData):
        """Sends a formated string containing the latency"""
        log.debug("run")
        tests = await _ping(self, api=api, testNum=testNum)
        if api:
            txt = _("COMM_PING_BOTH", cd.locale)
            txt = txt.format(gw=tests[0], api=tests[1])
        else:
            txt = _("COMM_PING_GATEWAY", cd.locale)
            txt = txt.format(ping=tests[0])
        log.debug(txt)
        try:
            await ctx.send(txt)
        except Exception:
            log.exception(f"PingSend")

    @commands.command(name="ping")
    @commands.cooldown(1, 2.5, commands.BucketType.user)
    async def ping(self, ctx: commands.Context, testNum: int = 1, api: str = False):
        """Gives ping to server the bot is running on"""
        if testNum > 5:
            testNum = 5
        if api is None:
            api = False
        log.debug(f"pingCommand {testNum=} | {api=}")
        cd = commonData(ctx)
        await self.pingDo(ctx=ctx, api=api, testNum=testNum, cd=cd)
        log.info(f"Ping: {cd.userID_Name}")

    @slash_command(
        name=_("COMM_PING_NAME", gxConfig.defaultLang),
        name_localizations=_("COMM_PING_NAME"),
        description=_("COMM_PING_DESC", gxConfig.defaultLang),
        description_localizations=_("COMM_PING_DESC"),
    )
    async def pingSlash(
        self,
        interaction: Interaction,
        api: bool = SlashOption(
            name=_("COMM_PING_API_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_PING_API_NAME"),
            description=_("COMM_PING_API_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_PING_API_DESC"),
            required=False,
            default=bool(False),
        ),
        testNum: int = SlashOption(
            name=_("COMM_PING_TESTNUM_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_PING_TESTNUM_NAME"),
            description=_("COMM_PING_TESTNUM_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_PING_TESTNUM_DESC"),
            default=1,
            max_value=5,
        ),
    ):
        """Gives ping to server the bot is running on"""
        cd = commonData(interaction)
        log.debug(cd.strUser)
        BL = await blacklistCheck(ctx=interaction, blklstType="gen")
        if BL is False:
            return
        if api is None:
            api = False
        log.debug(f"pingCommand {testNum=} | {api=}")
        await interaction.response.defer()
        await self.pingDo(ctx=interaction, api=api, testNum=testNum, cd=cd)
        log.info(f"Ping: {cd.userID_Name}")

    @slash_command(
        guild_ids=gxConfig.slashServers,
        name=_("COMM_INFO_BASE_NAME", gxConfig.defaultLang),
        name_localizations=_("COMM_INFO_BASE_NAME"),
    )
    async def infoBASE(self, interaction: Interaction):
        log.debug(f"infoBASE {interaction.user.id}")

    @infoBASE.subcommand(
        name=_("COMM_INFO_BOT_NAME", gxConfig.defaultLang),
        name_localizations=_("COMM_INFO_BOT_NAME"),
        description=_("COMM_INFO_BOT_DESC", gxConfig.defaultLang),
        description_localizations=_("COMM_INFO_BOT_DESC"),
    )
    async def infoBOT(
        self,
        interaction: Interaction,
        category: str = SlashOption(
            name=_("COMM_INFO_BOT_CATEGORY_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_INFO_BOT_CATEGORY_NAME"),
            description=_("COMM_INFO_BOT_CATEGORY_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_INFO_BOT_CATEGORY_DESC"),
            required=False,
            choices={
                "Description": _(
                    "COMM_INFO_BOT_CATEGORY_CHOICE_DESC", gxConfig.defaultLang
                ),
                "System": _(
                    "COMM_INFO_BOT_CATEGORY_CHOICE_SYSTEM", gxConfig.defaultLang
                ),
            },
            choice_localizations={
                "Description": _("COMM_INFO_BOT_CATEGORY_CHOICE_DESC"),
                "System": _("COMM_INFO_BOT_CATEGORY_CHOICE_SYSTEM"),
            },
        ),
    ):
        """Gathers and returns info regarding the bot"""
        cd = commonData(interaction)
        logSys.debug(f"{cd.locale=}")
        await interaction.response.defer()

        def _embed_desc():
            "Return an embed containing a general description of the bot"
            title = _("BOT_INFO_INTRO", cd.locale)
            title = title.format(botName=f"**{botInfo.botName}**")
            desc = _("BOT_INFO_DESC", cd.locale)
            desc = desc.format(
                creator="**APasz**",
                repo=f"**{botInfo.repoNice}**",
                prefix=gxConfig.BOT_PREFIX,
            )
            emb = nextcord.Embed(
                title=title, description=desc, colour=getCol("botInfo")
            )
            return emb

        async def _embed_sys():
            "Returns an embed containing system info"
            emb = nextcord.Embed(
                title=_("COMM_INFO_BOT_SYSTEM_TITLE", cd.locale),
                colour=getCol("botInfo"),
            )

            emb.add_field(
                name=_("BOT_INFO_HOST_TITLE", cd.locale),
                value=_("BOT_INFO_HOST_BODY", cd.locale).format(
                    hostname=botInfo.hostname,
                    os=botInfo.hostOS,
                    hoster=f"{botInfo.hostProvider} {botInfo.hostLocation}",
                ),
                inline=False,
            )

            emb.add_field(
                name=_("BOT_INFO_RAM_TITLE", cd.locale),
                value=_("BOT_INFO_RAM_BODY", cd.locale).format(
                    total=botInfo.hostRAM,
                    used=psutil.virtual_memory().percent,
                    bot=botInfo.memMiB(),
                ),
                inline=False,
            )

            emb.add_field(
                name=_("BOT_INFO_CPU_TITLE", cd.locale),
                value=_("BOT_INFO_CPU_BODY", cd.locale).format(
                    cores=botInfo.hostCores,
                    freq=round(psutil.cpu_freq()[0]),
                    usage=psutil.cpu_percent(),
                ),
                inline=False,
            )

            def uptime():
                try:
                    bootTime = int(psutil.boot_time())
                    utc = int(time.time())
                    return formatTime.time_format(total=(utc - bootTime))
                except Exception:
                    log.exception("InfoCommand_boot")
                    return _("ERROR_UNKNOWN", cd.locale)

            emb.add_field(
                name=_("BOT_INFO_UPTIME_TITLE", cd.locale),
                value=_("BOT_INFO_UPTIME_BODY", cd.locale).format(time=uptime()),
                inline=False,
            )

            latency = await _ping(self=self, api=True)
            emb.add_field(
                name=_("BOT_INFO_LATENCY_TITLE", cd.locale),
                value=_("BOT_INFO_LATENCY_BODY", cd.locale).format(
                    gateway=latency[0], api=latency[1]
                ),
                inline=False,
            )

            emb.add_field(
                name=_("BOT_INFO_LINES_TITLE", cd.locale),
                value=_("BOT_INFO_LINES_BODY", cd.locale).format(
                    py=botInfo.linePyCount, json=botInfo.lineJSONCount
                ),
                inline=False,
            )
            return emb

        toSend = []
        if category == "Description" or category is None:
            toSend.append(_embed_desc())
        if category == "System" or category is None:
            toSend.append(await _embed_sys())

        if len(toSend) > 0:
            for item in toSend:
                try:
                    await interaction.send(embed=item)
                except Exception:
                    log.exception(f"Send Info {category=}")

    @infoBASE.subcommand(
        name=_("COMM_INFO_GUILD_NAME", gxConfig.defaultLang),
        name_localizations=_("COMM_INFO_GUILD_NAME"),
        description=_("COMM_INFO_GUILD_DESC", gxConfig.defaultLang),
        description_localizations=_("COMM_INFO_GUILD_DESC"),
    )
    async def infoGUILD(
        self,
        interaction: Interaction,
        category: str = SlashOption(
            name=_("COMM_INFO_GUILD_CATEGORY_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_INFO_GUILD_CATEGORY_NAME"),
            description=_("COMM_INFO_GUILD_CATEGORY_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_INFO_GUILD_CATEGORY_DESC"),
            required=False,
            choices={
                "Description": _(
                    "COMM_INFO_GUILD_CATEGORY_CHOICE_DESC", gxConfig.defaultLang
                ),
                "Stats": _(
                    "COMM_INFO_GUILD_CATEGORY_CHOICE_STATS", gxConfig.defaultLang
                ),
            },
            choice_localizations={
                "Description": _("COMM_INFO_GUILD_CATEGORY_CHOICE_DESC"),
                "Stats": _("COMM_INFO_GUILD_CATEGORY_CHOICE_STATS"),
            },
        ),
    ):
        """Gathers and returns info regarding the current guild"""
        cd = commonData(interaction)
        logSys.debug(f"{cd.locale=}")
        await interaction.response.defer()

        def _embed_desc():

            emb = nextcord.Embed(
                title=_("COMM_INFO_GUILD_DESC_TITLE", cd.locale),
                colour=getCol("botInfo"),
            )
            servDesc = getServConf(guildID=cd.strGuild, option="Description")
            if servDesc is None:
                servDesc = f"There is no description for this server.\nTo add one please contact {gxConfig.ownerName}"
            emb.description = servDesc
            return emb

        def _embed_stats():

            emb = nextcord.Embed(
                title=_("COMM_INFO_GUILD_STATS_TITLE", cd.locale),
                colour=getCol("botInfo"),
            )
            emb.add_field(
                name="Stats",
                value=f"Member Count: {interaction.guild.member_count}",
                inline=False,
            )
            return emb

        toSend = []
        if category == "Description" or category is None:
            toSend.append(_embed_desc())
        if category == "Stats" or category is None:
            toSend.append(_embed_stats())

        if len(toSend) > 0:
            for item in toSend:
                try:
                    await interaction.send(embed=item)
                except Exception:
                    log.exception(f"Send Info {category=}")

    @commands.command(name="MemberCount", aliases=["GuildCount", "UserCount"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def memberCount(self, ctx: commands.Context):
        """Gives number of members current guild has"""
        log.info(f"{ctx.author.id=},{ctx.author.display_name=}")
        try:
            await ctx.send(f"**Member Count**: {ctx.guild.member_count}")
        except Exception:
            log.exception(f"Member Count")

    @slash_command(name="membercount", guild_ids=gxConfig.slashServers)
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def memberCountSlash(self, interaction: Interaction):
        """Gives number of members current guild has"""
        log.info(f"{interaction.user.id},{interaction.user.display_name}")
        if not await blacklistCheck(ctx=interaction, blklstType="gen"):
            return
        try:
            await interaction.send(interaction.user.guild.member_count)
        except Exception:
            log.exception(f"Member Count /")

    @slash_command(name="convert")
    async def convert(
        self,
        interaction: Interaction,
        value: float = SlashOption(
            name="value", description="What is it we are converting?", required=True
        ),
        fromMetric: str = SlashOption(
            name="original-metric",
            description="What Metric unit are we converting from?",
            required=False,
            choices=gxConfig.metricUnits,
        ),
        fromImperialUS: str = SlashOption(
            name="original-imperial-us",
            description="What Imperial/US unit are we converting from?",
            required=False,
            choices=gxConfig.imperialUnits,
        ),
        fromTime: str = SlashOption(
            name="original-time",
            description="If a original-unit is also given, original-unit/original-time",
            required=False,
            choices=gxConfig.timeUnits,
        ),
        toMetric: str = SlashOption(
            name="new-metric",
            description="What unit are we converting to?",
            required=False,
            choices=gxConfig.metricUnits,
        ),
        toImperialUS: str = SlashOption(
            name="new-imperial-us",
            description="What unit are we converting to?",
            required=False,
            choices=gxConfig.imperialUnits,
        ),
        toTime: str = SlashOption(
            name="new-time",
            description="If a new-unit is also given, new-unit/original-time",
            required=False,
            choices=gxConfig.timeUnits,
        ),
    ):
        """Converts between units using pint."""
        logSys.debug("convert comm")
        if not await blacklistCheck(ctx=interaction):
            return
        logSys.debug(
            f"{value=} | {fromMetric=} | {fromImperialUS=} | {fromTime=} | {toMetric=} | {toImperialUS=} | {toTime=}"
        )
        if fromMetric and fromImperialUS:
            try:
                await interaction.send(
                    f"Conflicting `originalUnit` arguments. {fromMetric.title()} {fromImperialUS.title()}",
                    ephemeral=True,
                )
            except Exception:
                log.exception(f"Convert /Command Conflict Orig")
            return
        if toMetric and toImperialUS:
            try:
                await interaction.send(
                    f"Conflicting `toUnit` arguments. {toMetric.title()} {toImperialUS.title()}",
                    ephemeral=True,
                )
            except Exception:
                log.exception(f"Convert /Command Conflict To")
            return
        fromUnit = "".join(filter(None, [fromMetric, fromImperialUS, fromTime]))
        toUnit = "".join(filter(None, [toMetric, toImperialUS, toTime]))
        logSys.debug(f"{fromUnit=} | {toUnit=}")
        if len(fromUnit) == 0 or len(toUnit) == 0:
            try:
                await interaction.send(
                    "Must have both `original` and `to` units.", ephemeral=True
                )
            except Exception:
                log.exception(f"Convert Orig|To")
            return
        if fromUnit and fromTime is not None:
            fromTime = "/" + fromTime
        if toUnit and toTime is not None:
            toTime = "/" + toTime
        u = pint.UnitRegistry()
        Q = u.Quantity

        try:
            orig = Q(value, ("".join(filter(None, [fromUnit, fromTime]))))
            new = round(orig.to("".join(filter(None, [toUnit, toTime]))), 3)
            logSys.debug(f"{orig=} | {new=}")
        except Exception as xcp:
            if "cannot convert" in str(xcp).casefold():
                try:
                    await interaction.send(
                        f"Conflicting units: {fromUnit.title()} {toUnit.title()}",
                        ephemeral=True,
                    )
                except Exception:
                    log.exception(f"Conflicting")
            else:
                log.exception("Convert")
                await interaction.send(f"An Error Occured!\n{xcp}")
            return
        orig = str(orig)
        new = str(new)
        orig = orig.replace("meter", "metre").replace("_", " ").title()
        orig = orig.replace("Uk", "UK").replace("Us", "US")
        new = new.replace("meter", "metre").replace("_", " ").title()
        new = new.replace("Uk", "UK").replace("Us", "US")
        text = f"Conversion;\n{orig} -> {new}"
        try:
            await interaction.send(text)
        except Exception:
            log.exception(f"Convert /Command")

    @slash_command(
        name=_("COMM_CHANGELOG_NAME", gxConfig.defaultLang),
        name_localizations=_("COMM_CHANGELOG_NAME"),
        description=_("COMM_CHANGELOG_DESC", gxConfig.defaultLang),
        description_localizations=_("COMM_CHANGELOG_DESC"),
    )
    async def changelog(
        self,
        interaction: Interaction,
        _version: str = SlashOption(
            name=_("COMM_CHANGELOG_VERSION_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_CHANGELOG_VERSION_NAME"),
            description=_("COMM_CHANGELOG_VERSION_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_CHANGELOG_VERSION_DESC"),
            required=False,
        ),
    ):
        """Provides the changelog"""
        BL = await blacklistCheck(ctx=interaction, blklstType="gen")
        if BL is False:
            return
        cd = commonData(interaction)
        logSys.debug(f"changelog: {_version} | {cd.userID_Name}")

        async def sendMess(vers: str, content: str, number: int = None):
            "Send a message with changelog format for consistency"
            toSend = [f"Version {vers}", f"\n```\n{content}\n```"]
            if number is not None:
                toSend.insert(1, f"      Items: {number} ")
            try:
                await interaction.response.send_message("".join(toSend))
            except Exception:
                logSys.exception(f"Send Changelog Message")

        if _version is None:
            version = botInfo.version
        elif "list" in _version.casefold():
            await sendMess(vers="List", content=" | ".join(botInfo.version.all))
            return
            # txt = " | ".join(botInfo.allVersions)
        elif "." in _version:
            if _version.replace(".", "").isdigit():
                if len(_version.split(".")) == 2:
                    _version = _version + ".0"
                elif _v := len(_version.split(".")) < 3:
                    _version = ".".join(_v[0:2])
                _ver = botInfo.verParse(_version)
                if str(_ver.base_version) not in botInfo.version.all:
                    logSys.debug(f"not in {_ver=}")
                    await sendMess(
                        vers=_ver,
                        content=_("COMM_CHANGELOG_VERSION_NOTFOUND", cd.locale),
                    )
                    return
                else:
                    version = _ver
        logSys.debug(f"{version=}")

        chLog = readJSON(file=paths.work.joinpath(gxConfig.changelog))

        version.title = chLog[str(version.minor)]["Title"]
        version.date = chLog[str(version.minor)][str(version.micro)][0]
        changeList = chLog[str(version.minor)][str(version.micro)][1:]

        def chunkList(maxChars: int, txtList: list):
            logLength = 0
            entryList = []
            for i, item in enumerate(txtList):
                logLength += len(item)
                if logLength <= maxChars:
                    entryList.append(i)
                else:
                    yield entryList
                    entryList = [i]
                    logLength = len(item)
            yield (entryList)

        chunks = list(chunkList(maxChars=1900, txtList=changeList))
        for item in chunks:
            eles = [changeList[i] for i in item]
            txt = "\n".join(eles)
            toSend = "Undefined"
            if interaction.response.is_done():
                log.debug("Followup")
                toSend = f"... continued ... \n```\n{txt}\n```"
                try:
                    await interaction.send(content=toSend)
                except Exception:
                    log.exception(f"Send Changelog Continue")
            else:
                log.debug("Response")
                verDate = (
                    f"{version.base_version} | {version.title}\nDate: {version.date}"
                )
                await sendMess(vers=verDate, number=len(changeList), content=txt)

    @slash_command(name="profile", guild_ids=gxConfig.slashServers)
    async def profile(
        self,
        interaction: Interaction,
        usr: nextcord.Member = SlashOption(
            name="member", description="If looking for member", required=False
        ),
    ):
        """Provides an embed with information about a user."""
        if not await blacklistCheck(ctx=interaction, blklstType="gen"):
            return
        cd = commonData(interaction)
        log.debug(f"profile: {usr} | {cd.userID_Name}")
        if usr is None:
            usr = interaction.user
        try:
            fetched = await self.bot.fetch_user(usr.id)
        except Exception:
            log.exception(f"Profile")  # cause Discord is stupid.
        if fetched.accent_colour is not None:
            usrCol = fetched.accent_colour  # 18191c
        else:
            usrCol = usr.colour
        e = nextcord.Embed(
            description=f"Mention: <@{usr.id}>\nAccount: {usr.name}{usr.discriminator}\nID: {usr.id}",
            colour=usrCol,
        )
        if fetched.banner is not None:
            e.set_image(url=fetched.banner.url)
        e.set_author(name=usr.display_name, icon_url=usr.display_avatar.url)
        created = int(round(usr.created_at.timestamp()))
        e.add_field(name="Registered;", value=f"<t:{created}:R>", inline=True)
        roles = []
        permsList2 = []
        if "member" in str(type(usr)):
            joined = int(round(usr.joined_at.timestamp()))
            e.add_field(name="Last Joined;", value=f"<t:{joined}:R>", inline=True)
            if usr.premium_since is not None:
                premium = int(round(usr.premium_since.timestamp()))
                e.add_field(
                    name="Booster Since;", value=f"<t:{premium}:R>", inline=True
                )
            roleList = usr.roles
            roleList.pop(0)
            roleList.reverse()
            for r in roleList:
                r = f"<@&{r.id}>"
                roles.append(r)
            roles = "".join(roles)
            roleNum = len(roleList)
            e.add_field(name=f"Roles: {roleNum}", value=roles, inline=False)
            permsList = []
            notePerms = [
                "manage",
                "moderate",
                "kick",
                "ban",
                "mute",
                "move",
                "deafen",
                "everyone",
                "audit",
                "timeout",
            ]
            for (
                perm
            ) in (
                usr.guild_permissions
            ):  # put all permissions into a list only if the user has it.
                alpha, bravo = perm
                if bravo is True:
                    permsList.append(alpha.lower())
            for element in permsList:  # If admin skip the rest.
                element = element.lower()
                if "admin" in element:
                    log.debug("admin")
                    permsList2 = ["Administrator"]
                    break
                else:  # check if any of the noteable perms partially match each element of the permissions list.
                    for note in notePerms:
                        if note in element:
                            log.debug("else")
                            element = element.replace("_", " ")
                            permsList2.append(element.title())
                            # there must be a better way to do this?
        flags = usr.public_flags.all()
        flagsList = []
        for f in flags:
            f = f.name
            f = f.replace("_", " ")
            flagsList.append(f.title())
        attris = flagsList + permsList2
        attris = ", ".join(attris)
        if len(attris) > 0:
            e.add_field(name="Attributes", value=attris)
        if usr.bot is True:
            e.set_footer(text="Is Bot")
        try:
            await interaction.send(embed=e)
        except Exception:
            log.exception(f"SendProfile")


def setup(bot: commands.Bot):
    bot.add_cog(general(bot))


# MIT APasz
