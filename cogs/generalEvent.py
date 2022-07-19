print("CogGeneralEvent")
import asyncio
import logging
import time

log = logging.getLogger("discordGeneral")
logMess = logging.getLogger("discordMessages")

import nextcord
from config import dataObject, genericConfig
from discord import Permissions
from nextcord import Interaction, SlashOption, slash_command
from nextcord.ext import commands
from util.fileUtil import readJSON, writeJSON
from util.genUtil import (
    getChan,
    getEventConfig,
    getGlobalEventConfig,
    getGuilds,
    getGuildID,
)

from cogs.auditLog import auditLogger
from cogs.modding import modding


class generalEvent(commands.Cog, name="GeneralEvent"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.onMemberFired = False
        self.eventConfig = getEventConfig()
        self.guildList = getGuilds()

    @commands.Cog.listener()
    async def on_ready(self):
        log.debug("Ready")

    @commands.command(name="updateEventList")
    @commands.is_owner()
    async def updateEventList(self, ctx=None):
        """Updates the config for discord events"""
        try:
            self.eventConfig = getEventConfig()
            self.guildList = getGuilds()
            log.info("Events updated")
            return True
        except Exception as xcp:
            log.error(xcp)
            return False

    @slash_command(
        name="toggleevents",
        default_member_permissions=Permissions(administrator=True),
        guild_ids=genericConfig.slashServers,
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
        configuraton[guildID]["Events"][event] = newState
        dataObject.type = "CommandToggleEvent"
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
            await interaction.send(
                f"Event: **{event}** was {oldState}, set to **{newState}**"
            )

    @toggleevents.on_autocomplete("event")
    async def eventList(self, interaction: Interaction, event: str):
        guildID = getGuildID(obj=interaction)
        if guildID is None:
            return
        guildEvents = self.eventConfig[guildID]
        globalEvents = getGlobalEventConfig(listAll=True)
        enabledEvents = []
        for item in globalEvents:
            if item in guildEvents:
                enabledEvents.append(f"O | {item}")
            else:
                enabledEvents.append(f"X | {item}")

        if not event:
            finalEventList = enabledEvents
        elif event:
            eventArg = event.lower()
            for item in enabledEvents:
                itemLow = item.lower()
                if eventArg in itemLow:
                    finalEventList.append(item)
        if len(finalEventList) >= 25:
            finalEventList = finalEventList[0:25]
            finalEventList[0] = "**Options Truncated**"
        await interaction.response.send_autocomplete(finalEventList)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send welcome message when new user joins"""
        await self.bot.wait_until_ready()
        if member.bot:
            return
        guildID = getGuildID(obj=member)
        if guildID is None:
            return
        if guildID not in self.guildList:
            return
        if "MemberJoin" in self.eventConfig[guildID]:
            logMess = f"{self.guildList[guildID]}, {member.id}: {member.display_name}"
            log.info(f"MemberJoin: {logMess}")
            dataObject.type = "MemberJoin"
            dataObject.userObject = member
            dataObject.count = member.guild.member_count
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            await auditLogger.logEmbed(self, dataObject)
            if "MemberJoinRecentCreation" in self.eventConfig[guildID]:
                usrCrtd = int(round(member.created_at.timestamp()))
                configuration = readJSON(filename="config")[guildID]
                crtTime = (
                    configuration["MISC"]["MemberJoinRecentCreationTimeHours"] * 60
                ) * 60
                unix = int(time.time())
                threshold = unix - crtTime
                if usrCrtd > threshold:
                    notifyChan = getChan(
                        self=self, guild=guildID, chan="Notify", admin=True
                    )
                    dataObject.type = "MemberJoinRecentCreation"
                    dataObject.count = unix - usrCrtd
                    dataObject.auditChan = notifyChan
                    await auditLogger.logEmbed(self, dataObject)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Check if new user has passed membership or display name changes."""
        await self.bot.wait_until_ready()
        guildID = getGuildID(obj=after)
        if guildID is None:
            return
        if guildID not in self.guildList:
            return
        if before.pending and after.pending is True:
            return
        log.debug("on_member_update")
        logMess = f"{self.guildList[guildID]}, {before.id}: {before.display_name}"
        dataObject.auditChan = getChan(
            self=self, guild=guildID, chan="Audit", admin=True
        )
        if before.pending and after.pending is False:
            if "MemberAccept" in self.eventConfig[guildID]:
                log.info(f"MemberAccept: {logMess}")
                dataObject.type = "MemberAccept"
                dataObject.userObject = after
                dataObject.count = after.guild.member_count
                await auditLogger.logEmbed(self, dataObject)
            if "MemberWelcome" in self.eventConfig[guildID]:
                log.info(f"MemberVerifiedRole: {logMess}")
                guild = after.guild
                if guild.system_channel is None:
                    return
                from config import txt_TpFwelcome

                toSend = (
                    f"{after.mention}, Welcome to {after.guild.name}" + txt_TpFwelcome
                )
                await guild.system_channel.send(toSend)
            if "MemberVerifiedRole" in self.eventConfig[guildID]:
                log.info(f"MemberVerifiedRole: {logMess}")
                role = nextcord.utils.get(
                    before.guild.roles,
                    id=readJSON(filename="config")[guildID]["Roles"]["Verified"],
                )
                await after.add_roles(role, atomic=True)

        elif before.display_name != after.display_name:
            if "MemberNameChange" in self.eventConfig[guildID]:
                dataObject.type = "MemberNameChange"
                dataObject.userObject = before
                dataObject.userObjectExtra = after
                log.info(f"UserNameChange: {logMess} | {after.display_name}")
                await auditLogger.logEmbed(self, dataObject)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log to audit-log channel when member leaves."""
        await self.bot.wait_until_ready()
        guildID = getGuildID(obj=member)
        if guildID is None:
            return
        if guildID not in self.guildList:
            return
        if "MemberLeave" in self.eventConfig[guildID]:
            self.onMemberFired = True
            dataObject.userObject = member
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            dataObject.guildObject = self.bot.get_guild(member.guild.id)
            await auditLogger.userRemove(self, dataObject)
            log.info(f"MemberLeave: {self.guildList[guildID]}, {member.id}")
            await asyncio.sleep(3)
            self.onMemberFired = False

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1.5)
        guildID = getGuildID(obj=payload)
        if guildID is None:
            return
        if self.onMemberFired:
            return
        if guildID not in self.guildList:
            return
        if "MemberLeave" in self.eventConfig[guildID]:
            guildData = self.bot.get_guild(payload.guild_id)
            log.info(f"RawMemberLeave: {self.guildList[guildID]}, {payload.user}")
            dataObject.type = "RawMemberLeave"
            dataObject.userObject = guildData
            dataObject.count = guildData.member_count
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            await auditLogger.logEmbed(self, dataObject)
            self.onMemberFired = False

    @commands.Cog.listener()
    async def on_member_ban(self, guild, usr):
        """Log to audit-log channel when member is banned."""
        await self.bot.wait_until_ready()
        guildID = str(guild.id)
        if guildID not in self.guildList:
            return
        if "MemberBan" in self.eventConfig[guildID]:
            log.info(
                f"MemberBan: {self.guildList[guildID]}, {usr.id}, {usr.display_name}"
            )
            dataObject.userObject = usr
            dataObject.guildObject = guild
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            await auditLogger.checkKickBan(self, dataObject)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, usr):
        """Log to audit-log channel when member is unbanned."""
        await self.bot.wait_until_ready()
        guildID = str(guild.id)
        if guildID not in self.guildList:
            return
        if "MemberUnban" in self.eventConfig[guildID]:
            log.info(
                f"MemberUnban: {self.guildList[guildID]}, {usr.id}, {usr.display_name}"
            )
            dataObject.type = "MemberUnban"
            dataObject.userObject = usr
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            await auditLogger.logEmbed(self, dataObject)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        await self.bot.wait_until_ready()
        guildID = getGuildID(obj=payload)
        if guildID is None:
            return
        if guildID not in self.guildList:
            return
        if "MessageDelete" in self.eventConfig[guildID]:
            log.debug(f"MessageDelete: {self.guildList[guildID]}")
            message = payload.cached_message
            dataObject.auditChan = getChan(
                self=self, guild=guildID, chan="Audit", admin=True
            )
            if message is not None:
                logMess.info(
                    f"""MessageID: {message.id}:
				Author: {message.author.id}: {message.author.name} | {message.author.display_name};
				\nContent: '' {message.content} ''"""
                )
                dataObject.type = "MessageDelete"
                dataObject.messageObject = message
            else:
                log.info(
                    f"R_M_D; MessageID: {payload.message_id}, ChannelID: {payload.channel_id}"
                )
                dataObject.type = "RawMessageDelete"
                dataObject.messageID = payload.message_id
                dataObject.channelID = payload.channel_id
            await auditLogger.logEmbed(self, dataObject)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        """Check for Author in message and adds heart reaction. Restricted to artwork channel in TpF server."""
        await self.bot.wait_until_ready()
        guildID = getGuildID(obj=ctx)
        if guildID is None:
            return
        log.debug(f"{self.guildList[guildID]}, {guildID}")
        if "Artwork" in self.eventConfig[guildID]:
            artChan = getChan(guildID, "Artwork")
            if ctx.channel.id == artChan:
                log.debug("AW listener")
                if "author" in ctx.content.casefold():
                    await ctx.add_reaction(genericConfig.emoHeart)
                    log.info("AW Reaction")
                    return
                else:
                    log.debug("AW")
        if "ModPreview" in self.eventConfig[guildID]:
            nmrChan = getChan(guildID, "NewModRelease")
            nmpChan = getChan(guildID, "NewModPreview")
            globalnmpChan = getChan(guildID, "NewModPreview")
            if (ctx.channel.id == nmrChan) and (ctx.author.bot is False):
                log.debug("NMR listener")
                nmp = await self.bot.fetch_channel(nmpChan)
                if ("ModPreviewGlobal" in self.eventConfig[guildID]) and (
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
        if "Battles" in self.eventConfig[guildID]:
            BattlesChan = getChan(guildID, "infoBattles")
            if ctx.channel.id == BattlesChan:
                log.debug("vkListener")
                if genericConfig.emoCheck in ctx.content:
                    await ctx.add_reaction(genericConfig.emoCheck)
                    log.info("VK_Checkmark")
                if genericConfig.emoTmbUp in ctx.content:
                    await ctx.add_reaction(genericConfig.emoTmbUp)
                    log.info("VK_ThumbsUp")


def setup(bot: commands.Bot):
    bot.add_cog(generalEvent(bot))


# MIT APasz
