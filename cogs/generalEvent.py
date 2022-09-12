import asyncio
import logging
import time

from config import generalEventConfig as geConfig
from config import genericConfig as gxConfig
from util.fileUtil import readJSON, writeJSON
from util.genUtil import getChan, getGuildID, getRole

from cogs.auditLog import auditLogger
from cogs.modding import modding

print("CogGeneralEvent")

log = logging.getLogger("discordGeneral")
logMess = logging.getLogger("discordMessages")
try:
    log.debug("TRY GENERAL_EVENT IMPORT MODULES")
    import nextcord
    from discord import Permissions
    from nextcord import Interaction, SlashOption, slash_command
    from nextcord.ext import commands
except Exception:
    log.exception("GENERAL_EVENT IMPORT MODULES")


class generalEvent(commands.Cog, name="GeneralEvent"):
    """Class containing listeners"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.debug(f"{self.__cog_name__} Ready")

    @commands.command(name="updateEventList")
    @commands.is_owner()
    async def updateEventList(self, ctx):
        """Updates the config for discord events"""
        guildID = str(ctx.guild.id)
        log.debug(f"{guildID=}")
        try:
            geConfig.update()
        except Exception:
            log.exception("Event List")

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
        guildID = str(interaction.guild_id)
        log.debug(f"{guildID=}")
        event = event.removeprefix("O | ")
        event = event.removeprefix("X | ")
        configuraton = readJSON("config")
        try:
            oldState = configuraton[guildID]["Events"][event]
        except KeyError:
            await interaction.send(
                "This item is not avaliable for this guild", ephemeral=True
            )
            return
        except Exception:
            log.exception("Toggle Event")
        configuraton[guildID]["Events"][event] = newState
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
        if await self.updateEventList(self):
            try:
                await interaction.send(
                    f"Event: **{event}** was {oldState}, set to **{newState}**"
                )
            except Exception:
                log.exception(f"Toggle Event Send")
        try:
            del dataObject
        except Exception:
            log.exception(f"Del TE /COMM")

    @toggleevents.on_autocomplete("event")
    async def eventList(self, interaction: Interaction, event: str):
        """Toggle event command autocomplete for event"""
        guildID = getGuildID(obj=interaction)
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

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send welcome message when new user joins"""
        await self.bot.wait_until_ready()
        guildID = getGuildID(obj=member)
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
                configuration = readJSON(filename="config")[guildID]
                try:
                    crtTime = (configuration["MISC"]["MemberJoin_RecentCreationHours"]
                               * 60) * 60
                except KeyError:
                    configuration["MISC"]["MemberJoin_RecentCreationHours"] = 48
                    writeJSON(data=configuration, filename="config")
                    crtTime = 48
                except Exception:
                    log.exception("RecentMemberJoin")
                unix = int(time.time())
                threshold = unix - crtTime
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

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
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
        if before.pending and after.pending is False:
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
                    ruleChan = getChan(guildID, "Rules")
                except Exception:
                    log.exception(f"Get Rules Chan")
                    ruleChan = None
                else:
                    ruleChan = int(ruleChan)
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
                role = getRole(guild=after.guild, role="Verified")
                if role != None:
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

    @commands.Cog.listener()
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
            geConfig.onMemberFired = True
            from config import dataObject
            dataObject.TYPE = "MemberLeave"
            dataObject.userObject = member
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            dataObject.guildObject = self.bot.get_guild(member.guild.id)
            await auditLogger.userRemove(self, dataObject)
            log.info(
                f"MemberLeave: {geConfig.guildListID[guildID]}, {member.id=}")
            await asyncio.sleep(3)
            geConfig.onMemberFired = False
            try:
                del dataObject
            except Exception:
                log.exception(f"Del MR")

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload):
        """Create an auditlog entry when a member leaves and isn't in cache"""
        await self.bot.wait_until_ready()
        await asyncio.sleep(1.5)
        guildID = getGuildID(obj=payload)
        if guildID is None:
            return
        log.debug(f"{guildID=} | {payload.user=}")
        if geConfig.onMemberFired:
            return
        if guildID not in geConfig.guildListID:
            return
        if "MemberLeave" in geConfig.eventConfigID[guildID]:
            guildData = self.bot.get_guild(payload.guild_id)
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
            geConfig.onMemberFired = False
            try:
                del dataObject
            except Exception:
                log.exception(f"Del RMR")

    @commands.Cog.listener()
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

    @commands.Cog.listener()
    async def on_member_unban(self, guild, usr):
        """Log to audit-log channel when member is unbanned."""
        await self.bot.wait_until_ready()
        guildID = str(guild.id)
        log.debug(f"{guildID=} | {usr.id=} | {usr.display_name=}")
        if guildID not in geConfig.guildListID:
            return
        if "MemberUnban" in geConfig.eventConfigID[guildID]:
            log.info(
                f"MemberUnban: {geConfig.guildListID[guildID]}, {usr.id=}, {usr.display_name=}"
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

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """Create an auditlog entry when a message is deleted and isn't in the cache"""
        await self.bot.wait_until_ready()
        guildID = getGuildID(obj=payload)
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

    @commands.Cog.listener()
    async def on_message(self, ctx):
        """Check for Author in message and adds heart reaction. Restricted to artwork channel in TpF server.
        Check if a mod link and create a mod mod preview embed.
        Check for certain emoji in the Battles channel and add those emoji"""
        await self.bot.wait_until_ready()
        guildID = getGuildID(obj=ctx)
        if guildID is None:
            return
        log.debug(
            f"{geConfig.guildListID[guildID]} {guildID=} | {ctx.channel.id=} | {ctx.author.id=}")
        if "Artwork" in geConfig.eventConfigID[guildID]:
            artChan = getChan(guildID, "Artwork")
            if ctx.channel.id == artChan:
                log.debug("AW listener")
                if "author" in ctx.content.casefold():
                    try:
                        await ctx.add_reaction(gxConfig.emoHeart)
                    except Exception:
                        log.exception(f"AW Reaction")
                    log.info("AW Reaction")
                    return
                else:
                    log.debug("AW")
            event = True
        if "ModPreview" in geConfig.eventConfigID[guildID]:
            nmrChan = getChan(guildID, "NewModRelease")
            log.debug(f"{nmrChan=}")
            if (ctx.channel.id == nmrChan) and (ctx.author.bot is False):
                nmpChan = getChan(guildID, "NewModPreview")
                globalnmpChan = getChan(
                    geConfig.guildListName["TPFGuild"], "NewModPreview")
                log.debug(f"NMR listener | {nmpChan=} | {globalnmpChan=}")
                try:
                    nmp = await self.bot.fetch_channel(nmpChan)
                except Exception:
                    log.exception(f"Fetch NMP Chan")
                log.debug(f"{geConfig.eventConfigID[guildID]=}")
                if ("ModPreviewGlobal" in geConfig.eventConfigID[guildID]) and (
                    nmpChan != globalnmpChan
                ):
                    globalPreview = True
                else:
                    globalPreview = False
                await modding.modRelease(
                    self=self,
                    ctx=ctx,
                    chan=nmp,
                    globalPreview=globalPreview,
                )
                log.info("modReleaseSent")
            event = True
        if "Battles" in geConfig.eventConfigID[guildID]:
            BattlesChan = getChan(guildID, "infoBattles")
            if ctx.channel.id == BattlesChan:
                log.debug("vkListener")
                if gxConfig.emoCheck in ctx.content:
                    try:
                        await ctx.add_reaction(gxConfig.emoCheck)
                    except Exception:
                        log.exception(f"VK_Checkmark")
                    log.info("VK_Checkmark")
                if gxConfig.emoTmbUp in ctx.content:
                    try:
                        await ctx.add_reaction(gxConfig.emoTmbUp)
                    except Exception:
                        log.exception(f"VK_ThumbsUp")
                    log.info("VK_ThumbsUp")
            event = True
        if not event:
            log.debug(f"GE on_message: No event. {guildID=}")


def setup(bot: commands.Bot):
    bot.add_cog(generalEvent(bot))


# MIT APasz
