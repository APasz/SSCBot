import asyncio
import logging
import time

from config import generalEventConfig as geConfig
from config import genericConfig as gxConfig
from util.fileUtil import readJSON, writeJSON
from util.genUtil import getChan, getChannelID, getGuildID, getRole

from cogs.auditLog import auditLogger
from cogs.modding import modding

print("CogGeneralEvent")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
logMess = logging.getLogger("discordMessages")
try:
    logSys.debug("TRY GENERAL_EVENT IMPORT MODULES")
    import nextcord
    from discord import Permissions
    from nextcord import Interaction, SlashOption, slash_command
    from nextcord.ext import commands
except Exception:
    logSys.exception("GENERAL_EVENT IMPORT MODULES")


class generalEvent(commands.Cog, name="GeneralEvent"):
    """Class containing listeners"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.onMemberFired = False

    @commands.Cog.listener()
    async def on_ready(self):
        logSys.debug(f"{self.__cog_name__} Ready")

    @commands.command(name="updateEventList")
    @commands.is_owner()
    async def updateEventList(self, ctx):
        """Updates the config for discord events"""
        guildID = int(getGuildID(obj=ctx))
        log.debug(f"{guildID=}")
        try:
            geConfig.update()
        except Exception:
            log.exception("Event List")
        else:
            log.info("events updated")

    @slash_command(
        name="toggleevents",
        default_member_permissions=Permissions(administrator=True),
        guild_ids=gxConfig.slashServers,
    )
    async def toggleevents(
        self,
        interaction: Interaction,
        event: str = SlashOption(
            name="event", required=True, description="Which event you want to toggle?"
        ),
        newState: bool = SlashOption(
            name="newstate",
            required=True,
            description="Whether to allow or disallow the event.",
            default=True,
        ),
    ):
        """Finds and changes specified event config value"""
        guildID = int(interaction.guild_id)
        log.debug(f"{guildID=}")
        event = event.removeprefix("O | ")
        event = event.removeprefix("X | ")
        configuraton = readJSON("config")
        try:
            oldState = configuraton[str(guildID)]["Events"][event]
        except KeyError:
            await interaction.send(
                "This item is not avaliable for this guild", ephemeral=True
            )
            return
        except Exception:
            log.exception("Toggle Event")
        configuraton[str(guildID)]["Events"][event] = newState
        from config import dataObject
        dataObject.TYPE = "CommandToggleEvent"
        dataObject.auditChan = getChan(
            self=self, guild=guildID, chan="Audit", admin=True
        )
        dataObject.category = event
        dataObject.commandArg1 = oldState
        dataObject.commandArg2 = newState
        dataObject.userObject = interaction.user
        print(dataObject)
        await auditLogger.logEmbed(self, dataObject)
        log.warning(f"{event}, {guildID}, {oldState}|{newState}")
        writeJSON(data=configuraton, filename="config")
        if await generalEvent.updateEventList(self, interaction):
            try:
                await interaction.send(
                    f"Event: **{event}** was {oldState}, set to **{newState}**"
                )
            except Exception:
                log.exception(f"Toggle Event Send")
        else:
            try:
                await interaction.send(f"An error occured. Event: **{event}** is still {oldState}")
            except Exception:
                log.exception(f"Toggle Event Error Send")
        try:
            del dataObject
        except Exception:
            log.exception(f"Del TE /COMM")

    @toggleevents.on_autocomplete("event")
    async def eventList(self, interaction: Interaction, event: str):
        """Toggle event command autocomplete for event"""
        guildID = int(getGuildID(obj=interaction))
        if guildID is None:
            return
        log.debug(f"{guildID=} | {event=} | {type(event)=} | {len(event)=}")
        guildEvents = geConfig.eventConfigID[guildID]
        globalEvents = geConfig.globalEventAll
        log.debug(f"{guildEvents=} | {globalEvents=}")
        enabledEvents = []
        for item in globalEvents:
            if item in guildEvents:
                enabledEvents.append(f"O | {item}")
            else:
                enabledEvents.append(f"X | {item}")
        log.debug(f"{enabledEvents=}")
        finalEventList = ["Error!"]
        if len(event) == 0:
            finalEventList = enabledEvents
        elif len(event) > 0:
            finalEventList = []
            eventArg = event.lower()
            for item in enabledEvents:
                itemLow = item.lower()
                if eventArg in itemLow:
                    finalEventList.append(item)

        log.debug(f"{finalEventList=}")
        if len(finalEventList) >= 25:
            finalEventList = finalEventList[0:25]
            finalEventList[0] = "**Options Truncated**"
        try:
            await interaction.response.send_autocomplete(finalEventList)
        except Exception:
            log.exception(f"EventList Autocomplete")

    @ commands.Cog.listener()
    async def on_member_join(self, member):
        """Send welcome message when new user joins"""
        await self.bot.wait_until_ready()
        guildID = int(getGuildID(obj=member))
        if member.bot:
            return
        if guildID is None:
            return
        log.debug(f"{guildID=}")
        if guildID not in geConfig.guildListID:
            return
        if "MemberJoin" in geConfig.eventConfigID[guildID]:
            logMess = f"{geConfig.guildListID[guildID]}, {member.id}: {member.display_name}"
            log.info(f"MemberJoin: {logMess}")
            from config import dataObject
            dataObject.TYPE = "MemberJoin"
            dataObject.userObject = member
            dataObject.count = member.guild.member_count
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            await auditLogger.logEmbed(self, dataObject)
            if "MemberJoinRecentCreation" in geConfig.eventConfigID[guildID]:
                usrCrtd = int(round(member.created_at.timestamp()))
                configuration = readJSON(filename="config")[
                    str(guildID)]["MISC"]
                try:
                    crtTime = (
                        configuration["MemberJoin_RecentCreationHours"] * 60) * 60
                except KeyError:
                    configuration["MemberJoin_RecentCreationHours"] = 48
                    writeJSON(data=configuration, filename="config")
                    crtTime = (48 * 60) * 60
                except Exception:
                    log.exception("RecentMemberJoin")
                unix = int(time.time())
                threshold = unix - crtTime
                log.debug(
                    f"MJ_RC: {unix=}, {crtTime=}, {threshold=}, {usrCrtd=}, is new {usrCrtd > threshold}")
                if usrCrtd > threshold:
                    notifyChan = getChan(
                        self=self, guild=guildID, chan="Notify", admin=True
                    )
                    from config import dataObject
                    dataObject.TYPE = "MemberJoinRecentCreation"
                    dataObject.count = unix - usrCrtd
                    dataObject.auditChan = notifyChan
                    await auditLogger.logEmbed(self, dataObject)
            try:
                del dataObject
            except Exception:
                log.exception(f"Del MJ")

    @ commands.Cog.listener()
    async def on_member_update(self, before, after: nextcord.Member):
        """Check if new user has passed membership or display name changes."""
        await self.bot.wait_until_ready()
        guildID = getGuildID(obj=after)
        if guildID is None:
            return
        log.debug(f"{guildID=}")
        if guildID not in geConfig.guildListID:
            return
        if before.pending and after.pending is True:
            return
        log.debug("on_member_update")
        logMess = f"guildID={geConfig.guildListID[guildID]}, {before.id=}: {before.display_name=}"
        from config import dataObject
        dataObject.auditChan = getChan(
            self=self, guild=guildID, chan="Audit", admin=True
        )
        if before.pending is False and after.pending is False:
            if "MemberAccept" in geConfig.eventConfigID[guildID]:
                log.info(f"MemberAccept: {logMess}")
                dataObject.TYPE = "MemberAccept"
                dataObject.userObject = after
                dataObject.count = after.guild.member_count
                await auditLogger.logEmbed(self, dataObject)
            if "MemberWelcome" in geConfig.eventConfigID[guildID]:
                log.info(f"MemberWelcome: {logMess}")
                guild = after.guild
                if guild.system_channel is None:
                    return
                strServ = readJSON(filename="strings")["en"]["Server"]
                welcome = strServ["Common"]["Welcome"]
                rules = strServ["Common"]["Rules"]
                try:
                    ruleChan = int(getChan(guildID, "Rules"))
                except Exception:
                    log.exception(f"Get Rules Chan")
                    ruleChan = None
                if isinstance(ruleChan, int):
                    welcomeMess = '\n'.join([welcome, rules])

                toSend = welcomeMess.format(
                    user=after.mention, guild=after.guild.name, rules=f"<#{ruleChan}>")
                try:
                    await guild.system_channel.send(toSend)
                except Exception:
                    log.exception(f"Send Guild Welcome")
            if "MemberVerifiedRole" in geConfig.eventConfigID[guildID]:
                log.info(f"MemberVerifiedRole: {logMess}")
                role = getRole(guild=after.guild.id, role="Verified")
                if role is not None:
                    try:
                        await after.add_roles(role, reason="Passed Membership Screen.", atomic=True)
                    except Exception:
                        log.exception(f"Add Verified")

        elif before.display_name != after.display_name:
            if "MemberNameChange" in geConfig.eventConfigID[guildID]:
                dataObject.TYPE = "MemberNameChange"
                dataObject.userObject = before
                dataObject.userObjectExtra = after
                log.info(f"UserNameChange: {logMess} | {after.display_name=}")
                await auditLogger.logEmbed(self, dataObject)
        try:
            del dataObject
        except Exception:
            log.exception(f"Del MU")

    @ commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log to audit-log channel when member leaves."""
        await self.bot.wait_until_ready()
        guildID = getGuildID(obj=member)
        if guildID is None:
            return
        log.debug(f"{guildID=} | {member.id=}")
        if guildID not in geConfig.guildListID:
            return
        if "MemberLeave" in geConfig.eventConfigID[guildID]:
            self.onMemberFired = True
            from config import dataObject
            dataObject.TYPE = "MemberLeave"
            dataObject.userObject = member
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            dataObject.guildObject = self.bot.get_guild(int(member.guild.id))
            await auditLogger.userRemove(self, dataObject)
            log.info(
                f"MemberLeave: {geConfig.guildListID[guildID]}, {member.id=}")
            await asyncio.sleep(3)
            self.onMemberFired = False
            try:
                del dataObject
            except Exception:
                log.exception(f"Del MR")

    @ commands.Cog.listener()
    async def on_raw_member_remove(self, payload):
        """Create an auditlog entry when a member leaves and isn't in cache"""
        await self.bot.wait_until_ready()
        await asyncio.sleep(1.5)
        guildID = getGuildID(obj=payload)
        if guildID is None:
            return
        log.debug(f"{guildID=} | {payload.user=}")
        if self.onMemberFired:
            return
        if guildID not in geConfig.guildListID:
            return
        if "MemberLeave" in geConfig.eventConfigID[guildID]:
            guildData = self.bot.get_guild(int(payload.guild_id))
            log.info(
                f"RawMemberLeave: {geConfig.guildListID[guildID]}, {payload.user=}")
            from config import dataObject
            dataObject.TYPE = "RawMemberLeave"
            dataObject.userObject = guildData
            dataObject.count = guildData.member_count
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            await auditLogger.logEmbed(self, dataObject)
            self.onMemberFired = False
            try:
                del dataObject
            except Exception:
                log.exception(f"Del RMR")

    @ commands.Cog.listener()
    async def on_member_ban(self, guild, usr):
        """Log to audit-log channel when member is banned."""
        await self.bot.wait_until_ready()
        guildID = str(guild.id)
        log.debug(f"{guildID=} | {usr.id=} | {usr.display_name=}")
        if guildID not in geConfig.guildListID:
            return
        if "MemberBan" in geConfig.eventConfigID[guildID]:
            log.info(
                f"MemberBan: {geConfig.guildListID[guildID]}, {usr.id=}, {usr.display_name=}"
            )
            from config import dataObject
            dataObject.TYPE = "MemberBan"
            dataObject.userObject = usr
            dataObject.guildObject = guild
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            await auditLogger.checkKickBan(self, dataObject)
            try:
                del dataObject
            except Exception:
                log.exception(f"Del MB")

    @ commands.Cog.listener()
    async def on_member_unban(self, guild, usr):
        """Log to audit-log channel when member is unbanned."""
        await self.bot.wait_until_ready()
        guildID = int(guild.id)
        log.debug(f"{guildID=} | {usr.id=} | {usr.display_name=}")
        if guildID not in geConfig.guildListID:
            return
        if "MemberUnban" in geConfig.eventConfigID[guildID]:
            log.info(
                f"MemberUnban: {geConfig.guildListID[str(guildID)]}, {usr.id=}, {usr.display_name=}"
            )
            from config import dataObject
            dataObject.TYPE = "MemberUnban"
            dataObject.userObject = usr
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            await auditLogger.logEmbed(self, dataObject)
            try:
                del dataObject
            except Exception:
                log.exception(f"Del MuB")

    @ commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """Create an auditlog entry when a message is deleted and isn't in the cache"""
        await self.bot.wait_until_ready()
        guildID = int(getGuildID(obj=payload))
        if guildID is None:
            return
        log.debug(f"{guildID=}")
        if guildID not in geConfig.guildListID:
            return
        if "MessageDelete" in geConfig.eventConfigID[guildID]:
            log.debug(f"MessageDelete: {geConfig.guildListID[guildID]}")
            message = payload.cached_message
            from config import dataObject
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            if message is not None:
                logMess.info(
                    f"""MessageID: {message.id}:
                Author: {message.author.id}: {message.author.name} | {message.author.display_name};
                \nContent: '' {message.content} ''"""
                )
                dataObject.TYPE = "MessageDelete"
                dataObject.messageObject = message
            else:
                log.info(
                    f"R_M_D; MessageID: {payload.message_id}, ChannelID: {payload.channel_id}"
                )
                dataObject.TYPE = "RawMessageDelete"
                dataObject.messageID = payload.message_id
                dataObject.channelID = payload.channel_id
            await auditLogger.logEmbed(self, dataObject)
            try:
                del dataObject
            except Exception:
                log.exception(f"Del RMD")

    @ commands.Cog.listener()
    async def on_message(self, ctx: commands.Context):
        """Check for Author in message and adds heart reaction. Restricted to artwork channel in TpF server.
        Check if a mod link and create a mod mod preview embed.
        Check for certain emoji in the Battles channel and add those emoji"""
        await self.bot.wait_until_ready()
        guildID = int(getGuildID(obj=ctx))
        chanID = int(getChannelID(obj=ctx))
        if guildID is None:
            return
        cfName = "**"
        if guildID in list(geConfig.guildListID):
            cfName = geConfig.guildListID[guildID]

        log.debug(
            f"GE_on_message; {cfName}: {guildID=} | {chanID=} | {ctx.author.id=}")
        event = False
        if "AutoReact" in geConfig.eventConfigID[guildID]:
            async def addReact(emoji):
                """Adds a reaction to a message"""
                if isinstance(emoji, int):
                    emoji = self.bot.get_emoji(emoji)
                try:
                    log.debug(f"Try add emoji {emoji}")
                    await ctx.add_reaction(emoji)
                except Exception:
                    log.exception(f"Add Reaction")

            log.debug(
                f"AutoReact: {guildID=} | {chanID=} | {list(geConfig.autoReactsChans)}")
            if guildID in list(geConfig.autoReactsChans):
                if chanID in list(geConfig.autoReactsChans[guildID]):
                    reactorList = geConfig.autoReactsChans[guildID][chanID]
                    emojiAdd = []
                    for item in reactorList:
                        reactor = geConfig.autoReacts[guildID][item]
                        match = False
                        log.debug(f"{reactor=}")
                        for element in reactor["Contains"]:
                            if reactor["isExactMatch"]:
                                if element in ctx.content:
                                    match = True
                            else:
                                if element in ctx.content.casefold():
                                    match = True
                        log.debug(f"{match=}")
                        if match:
                            for emoji in reactor["Emoji"]:
                                if isinstance(emoji, list):
                                    emoji = int(emoji[1])
                                if emoji not in emojiAdd:
                                    emojiAdd.append(emoji)

                    log.debug(f"{emojiAdd=}")
                    for emo in emojiAdd:
                        await addReact(emo)
                    event = True

        if "ModPreview" in geConfig.eventConfigID[guildID]:
            nmrChan = int(getChan(guildID, "NewModRelease"))
            log.debug(f"{nmrChan=} {chanID == nmrChan} | bot {ctx.author.bot}")
            if (chanID == nmrChan) and (ctx.author.bot is False):
                try:
                    nmpChan = int(getChan(guildID, "NewModPreview"))
                    globalnmpChan = int(getChan(
                        geConfig.guildListName["TPFGuild"], "NewModPreview"))
                except Exception:
                    log.exception(f"Get NMP Chans")
                log.debug(f"NMR listener | {nmpChan=} | {globalnmpChan=}")
                try:
                    nmp = await self.bot.fetch_channel(int(nmpChan))
                except Exception:
                    log.exception(f"Fetch NMP Chan")
                log.debug(f"{geConfig.eventConfigID[guildID]=}")
                globalPreview = False
                if "ModPreviewGlobal" not in geConfig.eventConfigID[guildID]:
                    if nmpChan != globalnmpChan:
                        globalPreview = True
                await modding.modRelease(
                    self=self,
                    ctx=ctx,
                    chan=nmp,
                    globalPreview=globalPreview,
                )
                delTrig = False
                if "ModPreview_DeleteTrigger" in geConfig.eventConfigID[guildID]:
                    delTrig = True
                log.info(f"modReleaseSent | delete {delTrig}")
                if delTrig:
                    try:
                        await ctx.delete()
                    except Exception:
                        log.exception(f"Delete Trig")
                event = True

        if not event:
            log.debug(f"GE on_message: No event.")


def setup(bot: commands.Bot):
    bot.add_cog(generalEvent(bot))


# MIT APasz
