import asyncio
import logging
import time

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

    from cogs.auditLog import auditLogger
    from config import generalEventConfig as geConfig
    from config import genericConfig as gxConfig
    from config import localeConfig as lcConfig
    from util.fileUtil import paths, readJSON, writeJSON
    from util.genUtil import (
        commonData,
        getChan,
        getRole,
        getServConf,
        onMessageCheck,
        setServConf,
    )
except Exception:
    logSys.exception("GENERAL_EVENT IMPORT MODULES")

_ = lcConfig.getLC


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
        cd = commonData(ctx)
        log.debug(f"{cd.intGuild=}")
        try:
            geConfig.update()
        except Exception:
            log.exception("Event List")
            return False
        else:
            log.info("events updated")
            return True

    @slash_command(
        name=_("COMM_TOGGLEEVENT_NAME", gxConfig.defaultLang),
        name_localizations=_("COMM_TOGGLEEVENT_NAME"),
        description=_("COMM_TOGGLEEVENT_DESC", gxConfig.defaultLang),
        description_localizations=_("COMM_TOGGLEEVENT_DESC"),
        default_member_permissions=Permissions(administrator=True),
        guild_ids=gxConfig.slashServers,
    )
    async def toggleevents(
        self,
        interaction: Interaction,
        event: str = SlashOption(
            name=_("COMM_TOGGLEEVENT_EVENT_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_TOGGLEEVENT_EVENT_NAME"),
            description=_("COMM_TOGGLEEVENT_EVENT_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_TOGGLEEVENT_EVENT_DESC"),
            required=True,
        ),
        newState: bool = SlashOption(
            name=_("COMM_TOGGLEEVENT_STATE_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_TOGGLEEVENT_STATE_NAME"),
            description=_("COMM_TOGGLEEVENT_STATE_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_TOGGLEEVENT_STATE_DESC"),
            default=bool(True),
            required=True,
        ),
    ):
        """Finds and changes specified event config value"""
        cd = commonData(interaction)
        log.debug(f"{cd.intGuild=}")
        event = (event.removeprefix("O | ")).removeprefix("X | ")
        configuraton = readJSON(file=paths.work.joinpath("config"))
        oldState = getServConf(guildID=cd.intGuild, group="Events", option=event)
        if oldState == newState:
            return
        if oldState is None:
            txt = _("COMM_TOGGLEEVENT_UNAVALIBLE", cd.locale)
            await interaction.send(txt.format(event=f"**{event}**"), ephemeral=True)
            return
        setServConf(guildID=cd.intGuild, group="Events", option=event, value=newState)

        from config import dataObject

        dataObject.TYPE = "CommandToggleEvent"
        dataObject.auditChan = getChan(
            self=self, guild=cd.intGuild, chan="Audit", admin=True
        )
        dataObject.category = event
        dataObject.commandArg1 = oldState
        dataObject.commandArg2 = newState
        dataObject.userObject = interaction.user
        print(dataObject)
        await auditLogger.logEmbed(self, dataObject)
        log.warning(f"{event}, {cd.intGuild}, {oldState}|{newState}")
        writeJSON(data=configuraton, file=paths.work.joinpath("config"))
        k = await generalEvent.updateEventList(self, interaction)
        logSys.debug(f"updateEventList {k}")
        await asyncio.sleep(0.05)
        if k:
            try:
                txt = _("COMM_TOGGLEEVENT_UPDATE_SUCCESS", cd.locale)
                await interaction.send(
                    txt.format(
                        event=f"**{event}**",
                        oldState=oldState,
                        newState=f"**{newState}**",
                    )
                )
            except Exception:
                log.exception(f"Toggle Event Send")
        else:
            try:
                txt = _("COMM_TOGGLEEVENT_UPDATE_FAIL", cd.locale)
                await interaction.send(
                    txt.format(event=f"**{event}**", oldState=f"**{oldState}**")
                )
            except Exception:
                log.exception(f"Toggle Event Error Send")
        try:
            del dataObject
        except Exception:
            log.exception(f"Del TE /COMM")

    @toggleevents.on_autocomplete("event")
    async def eventList(self, interaction: Interaction, event: str):
        """Toggle event command autocomplete for event"""
        cd = commonData(interaction)
        if cd.intGuild is None:
            return
        log.debug(f"{cd.intGuild=} | {event=} | {type(event)=} | {len(event)=}")
        guildEvents = geConfig.eventConfigID[cd.intGuild]
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
            finalEventList[0] = _("COMM_OPTIONS_TRUNCATED", cd.locale)
        try:
            await interaction.response.send_autocomplete(finalEventList)
        except Exception:
            log.exception(f"EventList Autocomplete")

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        """Send welcome message when new user joins"""
        await self.bot.wait_until_ready()
        guildID = member.guild.id
        if member.bot:
            return
        if guildID is None:
            return
        log.debug(f"{guildID=}")
        if guildID not in geConfig.guildListID:
            return
        if "MemberJoin" in geConfig.eventConfigID[guildID]:
            logMess = (
                f"{geConfig.guildListID[guildID]}, {member.id}: {member.display_name}"
            )
            log.info(f"MemberJoin: {logMess}")
            from config import dataObject

            dataObject.TYPE = "MemberJoin"
            dataObject.userObject = member
            dataObject.count = member.guild.member_count
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            await auditLogger.logEmbed(self, dataObject)
            if "MemberJoin_RecentCreation" in geConfig.eventConfigID[guildID]:
                usrCrtd = int(round(member.created_at.timestamp()))
                configuration = readJSON(file=paths.work.joinpath("config"))[
                    str(guildID)
                ]["MISC"]
                try:
                    crtTime = (
                        configuration["MemberJoin_RecentCreationHours"] * 60
                    ) * 60
                except KeyError:
                    configuration["MemberJoin_RecentCreationHours"] = 48
                    writeJSON(data=configuration, file=paths.work.joinpath("config"))
                    crtTime = (48 * 60) * 60
                except Exception:
                    log.exception("RecentMemberJoin")
                unix = int(time.time())
                threshold = unix - crtTime
                log.debug(
                    f"MJ_RC: {unix=}, {crtTime=}, {threshold=}, {usrCrtd=}, is new {usrCrtd > threshold}"
                )
                if usrCrtd > threshold:
                    notifyChan = getChan(
                        self=self, guild=guildID, chan="Notify", admin=True
                    )
                    from config import dataObject

                    dataObject.TYPE = "MemberJoin_RecentCreation"
                    dataObject.count = unix - usrCrtd
                    dataObject.auditChan = notifyChan
                    await auditLogger.logEmbed(self, dataObject)
            try:
                del dataObject
            except Exception:
                log.exception(f"Del MJ")

    @commands.Cog.listener()
    async def on_member_update(self, before, after: nextcord.Member):
        """Check if new user has passed membership or display name changes."""
        await self.bot.wait_until_ready()
        guildID = after.guild.id
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
        if before.pending and not after.pending:
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
                welcome = getServConf(
                    guildID=after.guild.id, group="MISC", option="Welcome"
                )
                rules = getServConf(
                    guildID=after.guild.id, group="MISC", option="Rules"
                )
                try:
                    ruleChan = int(getChan(guildID, "Rules"))
                except Exception:
                    log.exception(f"Get Rules Chan")
                    ruleChan = None
                if isinstance(ruleChan, int):
                    welcomeMess = "\n".join([welcome, rules])

                toSend = welcomeMess.format(
                    user=after.mention, guild=after.guild.name, rules=f"<#{ruleChan}>"
                )
                try:
                    await guild.system_channel.send(toSend)
                except Exception:
                    log.exception(f"Send Guild Welcome")
            if "MemberVerifiedRole" in geConfig.eventConfigID[guildID]:
                log.info(f"MemberVerifiedRole: {logMess}")
                roles = []
                role = getRole(guild=after.guild, role="Verified")
                if role:
                    roles.append(role)
                if "SSC_NotifyRole_Assignment" in geConfig.eventConfigID[guildID]:
                    role = getRole(guild=after.guild, role="SSC_Notify_General")
                    if role:
                        roles.append(role)
                    role = getRole(guild=after.guild, role="SSC_Notify_Prize")
                    if role:
                        roles.append(role)
                if len(roles) > 0:
                    try:
                        await after.add_roles(
                            *roles, reason="Passed Membership Screen.", atomic=True
                        )
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

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log to audit-log channel when member leaves."""
        await self.bot.wait_until_ready()
        guildID = member.guild.id
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
            log.info(f"MemberLeave: {geConfig.guildListID[guildID]}, {member.id=}")
            await asyncio.sleep(3)
            self.onMemberFired = False
            try:
                del dataObject
            except Exception:
                log.exception(f"Del MR")

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload):
        """Create an auditlog entry when a member leaves and isn't in cache"""
        await self.bot.wait_until_ready()
        await asyncio.sleep(1.5)
        if hasattr(payload, "guild"):
            guildID = payload.guild.id
        else:
            guildID = payload.guild_id
        if guildID is None:
            logSys.warning("GuildID None")
            return
        log.debug(f"{guildID=} | {payload.user=}")
        if self.onMemberFired:
            return
        if guildID not in geConfig.guildListID:
            return
        if "MemberLeave" in geConfig.eventConfigID[guildID]:
            guildData = self.bot.get_guild(int(payload.guild_id))
            log.info(
                f"RawMemberLeave: {geConfig.guildListID[guildID]}, {payload.user=}"
            )
            from config import dataObject

            dataObject.TYPE = "RawMemberLeave"
            dataObject.userObject = payload.user
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

    @commands.Cog.listener()
    async def on_member_ban(self, guild: nextcord.Guild, usr):
        """Log to audit-log channel when member is banned."""
        await self.bot.wait_until_ready()
        guildID = int(guild.id)
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

    @commands.Cog.listener()
    async def on_member_unban(self, guild: nextcord.Guild, usr):
        """Log to audit-log channel when member is unbanned."""
        await self.bot.wait_until_ready()
        log.debug(f"{guild.id=} | {usr.id=} | {usr.display_name=}")
        if guild.id not in geConfig.guildListID:
            return
        if "MemberUnban" in geConfig.eventConfigID[guild.id]:
            log.info(
                f"MemberUnban: {geConfig.guildListID[guild.id]}, {usr.id=}, {usr.display_name=}"
            )
            from config import dataObject

            dataObject.TYPE = "MemberUnban"
            dataObject.userObject = usr
            dataObject.auditChan = getChan(
                self=self, guild=guild.id, chan="Audit", admin=True
            )
            await auditLogger.logEmbed(self, dataObject)
            try:
                del dataObject
            except Exception:
                log.exception(f"Del MuB")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """Create an auditlog entry when a message is deleted and isn't in the cache"""
        await self.bot.wait_until_ready()
        if hasattr(payload, "guild"):
            guildID = payload.guild.id
        else:
            guildID = payload.guild_id
        if guildID is None:
            logSys.warning("GuildID None")
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

    @commands.Cog.listener()
    async def on_message(self, ctx: nextcord.Message):
        """Check for AutoReacts"""
        await self.bot.wait_until_ready()
        if not onMessageCheck(ctx):
            return
        cd = commonData(ctx)
        cfName = "**"
        if cd.intGuild in list(geConfig.guildListID):
            cfName = geConfig.guildListID[cd.intGuild]
        else:
            return

        log.debug(
            f"GE_on_message; {cfName}: {cd.intGuild=} | {cd.chanID_Name} | {cd.userID_Name}"
        )
        event = False
        if "AutoReact" in geConfig.eventConfigID[cd.intGuild]:

            async def addReact(emoji):
                """Adds a reaction to a message"""
                if isinstance(emoji, int):
                    emoji = self.bot.get_emoji(emoji)
                try:
                    logSys.debug(f"Try add emoji {emoji}")
                    await ctx.add_reaction(emoji)
                except Exception:
                    logSys.exception(f"Add Reaction")

            log.debug(
                f"AutoReact: {cd.intGuild=} | {cd.intChan=} | {list(geConfig.autoReactsChans)}"
            )
            if cd.intGuild in list(geConfig.autoReactsChans):
                if cd.intChan in list(geConfig.autoReactsChans[cd.intGuild]):
                    reactorList = geConfig.autoReactsChans[cd.intGuild][cd.intChan]
                    emojiAdd = []
                    for item in reactorList:
                        reactor = geConfig.autoReacts[cd.intGuild][item]
                        match = False
                        log.debug(f"{reactor=}")
                        for element in reactor["Contains"]:
                            if reactor["isExactMatch"]:
                                if element in ctx.content:
                                    match = True
                            else:
                                if element.casefold() in ctx.content.casefold():
                                    match = True
                        # log.debug(f"{match=}")
                        if match:
                            for emoji in reactor["Emoji"]:
                                if isinstance(emoji, list):
                                    emoji = int(emoji[1])
                                if emoji not in emojiAdd:
                                    emojiAdd.append(emoji)

                    # log.debug(f"{emojiAdd=}")
                    for emo in emojiAdd:
                        await addReact(emo)
                    event = True

        if not event:
            log.debug(f"GE_on_message: No event.")


def setup(bot: commands.Bot):
    bot.add_cog(generalEvent(bot))


# MIT APasz
