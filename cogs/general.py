import logging
import random
import time

from config import botInformation as botInfo
from config import bytesToHuman
from config import generalEventConfig as geConfig
from config import genericConfig as gxConfig
from util.fileUtil import readJSON
from util.genUtil import _ping, blacklistCheck, getCol, formatTime
from util.views import factSubmit

print("CogGeneral")

log = logging.getLogger("discordGeneral")
try:
    log.debug("TRY GENERAL IMPORT MODUELS")
    import nextcord
    import pint
    import psutil
    from nextcord import Embed, Interaction, SlashOption, slash_command
    from nextcord.ext import commands
except Exception:
    log.exception("GENERAL IMPORT MODUELS")


class general(commands.Cog, name="General"):
    """Class containing commands that aren't for bot management or inherently related to TpF"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.debug(f"{self.__cog_name__} Ready")

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

    async def factGet(self, index: int = -1, metadata: bool = False) -> str | nextcord.Embed:
        """Retrieves a fact from the facts JSON file."""
        log.debug(f"run| {index=}| {metadata=}")
        data = f"'An error occurred' Alert <@{gxConfig.ownerID}>"
        if facts := readJSON(filename=gxConfig.factsJSON):
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
        ID = f"Fact #{index}"
        content = factDic["content"]
        source = factDic["source"]
        sourceLink = factDic["sourceLink"]
        extraLinks = factDic["extraLinks"]
        initialAdd = factDic["initialAdd"]
        lastUpdate = factDic["lastUpdate"]
        providerID = factDic["providerID"]
        if providerID == None:
            providerID = "*Not avaliable*"
        providerName = factDic["providerName"]
        if providerName == None:
            providerName = "*Not avaliable*"
        if source == None and sourceLink == None:
            source = "Someone forgot the source."
        if sourceLink == None:
            data = nextcord.Embed(
                title=ID, description=content, colour=getCol("fact"))
        else:
            data = nextcord.Embed(
                title=ID, description=content, colour=getCol("fact"), url=sourceLink)
        if source and sourceLink:
            source = f"Source;\n{source}\n{sourceLink}"
        elif sourceLink and not source:
            source = "Source;\n" + sourceLink
        data.set_footer(text=source)
        if len(extraLinks) > 0:
            extraLinks = "\n".join(extraLinks)
            data.add_field(name="Extra Links", value=extraLinks, inline=False)
        if metadata:
            data.add_field(
                name="Metadata", value=f"Provider Name|ID: {providerName} | {providerID}\nDate Added|Updated: {initialAdd} | {lastUpdate}")
        return data

    @commands.command(name="fact", aliases=["randomFact"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def factCommand(self, ctx, index: int = -1, metadata: bool = False):
        """Serves Random Facts"""
        log.debug("factCommand")
        async with ctx.typing():
            fact = await self.factGet(index=index, metadata=metadata)
            try:
                if isinstance(fact, Embed):
                    await ctx.send(embed=fact)
                else:
                    await ctx.send(fact)
            except Exception:
                log.exception("factCOMM")
            log.info(f"Fact: {ctx.author.id},{ctx.author.display_name}")

    @slash_command(name="fact")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def factSlash(self, interaction: Interaction, index: int = SlashOption(
            name="index", required=False, default=-1,
            description="When looking for a specific fact. If in an invalid index is given, one will be picked at random"),
            metadata: bool = SlashOption(name="metadata", required=False, default=bool(False),
                                         description="Whether to show addition information such as who submitted a fact and when.")):
        """Serves Random Facts"""
        if not await blacklistCheck(ctx=interaction, blklstType="gen"):
            return
        log.debug("factSlash")
        fact = await self.factGet(index=index, metadata=metadata)
        try:
            if isinstance(fact, Embed):
                await interaction.response.send_message(embed=fact)
            else:
                await interaction.response.send_message(fact)
        except Exception:
            log.exception("factSLASH")
        log.info(
            f"Fact: {interaction.user.id},{interaction.user.display_name}")

    async def pingDo(self, ctx, api: bool, testNum: int):
        """Sends a formated string containing the latency"""
        log.debug("run")
        tests = await _ping(self, api=api, testNum=testNum)
        if api:
            txt = f"Gateway: {tests[0]}ms   API: {tests[1]}ms"
        else:
            txt = f"I'm ping ponging at {tests[0]}ms"
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
        if api == None:
            api = False
        log.debug(f"pingCommand {testNum=} | {api=}")
        await self.pingDo(ctx=ctx, api=api, testNum=testNum)
        log.info(f"Ping: {ctx.author.id=},{ctx.author.display_name=}")

    @slash_command(name="ping")
    async def pingSlash(
            self,
            interaction: Interaction,
            api: bool = SlashOption(
                name="api", description="Do you want to check API latency?", required=False, default=bool(False)
            ),
            testNum: int = SlashOption(
                name="test-count", description="How many tests to do?", default=1, max_value=5)
    ):
        """Gives ping to server the bot is running on"""
        log.debug(interaction.user.id)
        BL = await blacklistCheck(ctx=interaction, blklstType="gen")
        if BL is False:
            return
        if api == None:
            api = False
        log.debug(f"pingCommand {testNum=} | {api=}")
        await interaction.response.defer()
        await self.pingDo(ctx=interaction, api=api, testNum=testNum)
        log.info(
            f"Ping: {interaction.user.id=},{interaction.user.display_name=}")

    @slash_command(name="info", guild_ids=gxConfig.slashServers)
    async def info(self, interaction: Interaction,
                   category: str = SlashOption(name="category", required=True, choices=["Bot", "Server", "Member"],
                                               description="What sort of info are you looking for?"),):
        """Get info about the bot or current server."""
        guildID = str(interaction.guild_id)
        await interaction.response.defer()
        if category == "Bot":
            strBot = readJSON(filename="strings")["en"]["Bot"]
            # generate description
            if botInfo.botName == "SSCBot":
                desc = strBot["InfoNameSame"]
            else:
                try:
                    desc = '\n'.join(
                        [strBot["InfoNameDiff"], strBot["InfoDesc"]])
                    desc = desc.format(name=botInfo.botName,
                                       prefix=gxConfig.BOT_PREFIX)
                except Exception:
                    log.exception("InfoComand_desc")
            embd = nextcord.Embed(title="Bot Info", description=desc,
                                  colour=getCol(col="botInfo"))
            # generate memory info
            try:
                processBot = psutil.Process(botInfo.processPID)
                memB = processBot.memory_info().rss
                memMiB = bytesToHuman(byteNum=memB, magnitude="M")
            except Exception:
                log.exception("InfoCommand_mem")
                memMiB = "*undefined*"
            # generate time since sys boot
            try:
                bootTime = int(psutil.boot_time())
            except Exception:
                log.exception("InfoCommand_boot")
                sinceBoot = "*undefined*"
            else:
                utc = int(time.time())
                sinceBoot = formatTime.time_format(total=(utc - bootTime))
            # generate latency string
            latency = await _ping(self=self, api=True)
            latencyTxt = f"Gateway: {latency[0]}ms, API: {latency[1]}ms"
            # add field to embed
            embd.add_field(name="Host System",
                           value=f"""Hostname: {botInfo.hostname} | OS: {botInfo.hostOS} | Host: {botInfo.hostProvider} {botInfo.hostLocation}
RAM; Total: {botInfo.hostRAM} | Used: {psutil.virtual_memory().percent}% | Process: {memMiB}
CPU; Cores: {botInfo.hostCores} | Frequency: {round(psutil.cpu_freq()[0])}Mhz | Sys Usage: {psutil.cpu_percent()}%
Uptime: {sinceBoot}
Latency; {latencyTxt}
Python: {botInfo.hostPython} | Nextcord: {botInfo.nextcordVer} | Bot: {botInfo.base}
Line Count; Python: ~{botInfo.linePyCount} | JSON: ~{botInfo.lineJSONCount}
Guilds: {botInfo.guildCount}""")
        elif category == "Server":
            try:
                strServ = readJSON(filename="strings")["en"]["Server"]
                desc = strServ[geConfig.guildListID[guildID]]["Description"]
            except Exception:
                log.exception("InfoCommand_desc")
                desc = f"There is no description for this server yet.\nPlease contact {gxConfig.ownerName}"
            embd = nextcord.Embed(title="Server Info", description=desc,
                                  colour=getCol(col="neutral_Light"))
            embd.add_field(name="Stats",
                           value=f"""Member Count: {interaction.user.guild.member_count}\n *WIP*""")
        elif category == "Member":
            await self.profile(interaction=interaction, usr=interaction.user)
            return
        try:
            await interaction.send(embed=embd)
        except Exception:
            log.exception(f"SendInfo_embed {category=}")

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
        if not await blacklistCheck(ctx=interaction):
            return
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
        fromUnit = "".join(filter(None, [fromMetric, fromImperialUS]))
        toUnit = "".join(filter(None, [toMetric, toImperialUS]))
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
        orig = orig.replace('meter', 'metre').replace('_', ' ').title()
        orig = orig.replace('Uk', 'UK').replace('Us', 'US')
        new = new.replace('meter', 'metre').replace('_', ' ').title()
        new = new.replace('Uk', 'UK').replace('Us', 'US')
        text = f"Conversion;\n{orig} -> {new}"
        try:
            await interaction.send(text)
        except Exception:
            log.exception(f"Convert /Command")

    @slash_command(name="changelog")
    async def changelog(
            self,
            interaction: Interaction,
            ver=SlashOption(
                name="version",
                required=False,
                description="If looking for specific version; x.x.x or list",
            ),
    ):
        """Provides the changelog"""
        BL = await blacklistCheck(ctx=interaction, blklstType="gen")
        if BL is False:
            return
        log.debug(
            f"changelog: {ver} | {interaction.user.id},{interaction.user.display_name}"
        )
        data = readJSON(filename="changelog")
        keys = data.keys()
        if ver is not None:
            if "list" not in ver:
                ver2 = ver.split(".")
                print(len(ver2))
                if len(ver2) == 2:
                    ver = ver + ".0"
                elif len(ver2) == 1:
                    ver = ver + ".0.0"
            else:
                ver = "List"
        if ver is None:
            ver = list(data)[-1]  # default to last ver in changelog

        async def sendMess(version: str, content: str):
            await interaction.response.send_message(
                f"Version {version}```\n{content}\n```"
            )

        txt = "Undefinded"
        if "list" in ver.casefold():
            txt = " | ".join(list(keys))
            try:
                await sendMess(version=ver, content=txt)
            except Exception:
                log.exception(f"Changelog /Command")
            return
        elif ver not in keys:
            txt = "Version not in changelog."
            try:
                await sendMess(version=ver, content=txt)
            except Exception:
                log.exception(f"Changelog /Command")
            return
        else:
            verNameDate = str(data[f"{ver}"][0]).split("::")
            changeList = data[f"{ver}"][1:]
        version = f"{ver} | {verNameDate[0]}\nDate: {verNameDate[1]}"

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
            else:
                log.debug("Response")
                toSend = (
                    f"Version {version}      Items: {len(changeList)} ```\n{txt}\n```"
                )
            try:
                await interaction.send(content=toSend)
            except Exception:
                log.exception(f"Send Changelog")

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
        log.debug(
            f"profile: {usr} | {interaction.user.id},{interaction.user.display_name}"
        )
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
            e.add_field(name="Last Joined;",
                        value=f"<t:{joined}:R>", inline=True)
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
