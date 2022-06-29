print("CogGeneralEvent")
import asyncio
import logging
import os
import time

import config
import nextcord
from nextcord.ext import commands
from util.modding import modRelease

from cogs.auditLog import auditLogger

log = logging.getLogger("discordGeneral")
logMess = logging.getLogger("discordMessages")
from util.fileUtil import readJSON, writeJSON, parentDir
from util.genUtil import getChan, getEventConfig, getGuilds

global onMemberFired
onMemberFired = False


def setupEventList():
    log.debug("run")
    data = {}
    data["event"] = getEventConfig()
    data["guild"] = getGuilds()
    evDir = os.path.join(parentDir(), "eventConfig.json")
    if os.path.exists(path=evDir):
        os.remove(evDir)
    time.sleep(0.1)
    if writeJSON(data=data, filename="eventConfig"):
        return True


setupEventList()


class generalEvent(commands.Cog, name="GeneralEvent"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.debug("Ready")

    @commands.command(name="updateEventList")
    @commands.has_permissions(administrator=True)
    async def updateEventList(self, ctx):
        """Updates the config for discord events"""
        if setupEventList() is True:
            await ctx.send("Done!")
        else:
            await ctx.send(f"Error!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send welcome message when new user joins"""
        await self.bot.wait_until_ready()
        guildID = str(member.guild.id)
        eventJSON = readJSON("eventConfig")
        eventsAllowed = eventJSON["event"]
        guildsList = eventJSON["guild"]
        if member.bot:
            return
        if guildID not in guildsList:
            return
        configName = guildsList[guildID]
        if "MemberJoin" in eventsAllowed[guildID]:
            log.info(f"MemberJoin: {configName}, {member.id}, {member.display_name}")
            audit = getChan(guild=configName, chan="Audit", admin=True)
            guildCount = member.guild.member_count
            usrDic = {
                "type": "MemberJoin",
                "auth": member,
                "guildExta": guildCount,
                "chanAudit": audit,
            }
            await auditLogger.logEmbed(self, usrDic)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Check if new user has passed membership or display name changes."""
        await self.bot.wait_until_ready()
        guildID = str(after.guild.id)
        eventJSON = readJSON("eventConfig")
        eventsAllowed = eventJSON["event"]
        guildsList = eventJSON["guild"]
        if guildID not in guildsList:
            return
        log.debug("on_member_update")
        configName = guildsList[guildID]
        audit = getChan(guild=configName, chan="Audit", admin=True)
        if before.pending and after.pending is True:
            return
        elif before.pending and after.pending is False:
            if "MemberAccept" in eventsAllowed[guildID]:
                log.info(
                    f"MemberAccept: {configName}, {after.id}: {after.display_name}"
                )
                guildCount = after.guild.member_count
                usrDic = {
                    "type": "MemberAccept",
                    "auth": after,
                    "guildExta": guildCount,
                    "chanAudit": audit,
                }
                await auditLogger.logEmbed(self, usrDic)
            if "MemberVerifiedRole" in eventsAllowed[guildID]:
                log.info(
                    f"MemberVerifiedRole: {configName}, {after.id}: {after.display_name}"
                )
                role = nextcord.utils.get(
                    before.guild.roles,
                    id=readJSON(filename="config")[configName]["Roles"]["Verified"],
                )
                await after.add_roles(role, atomic=True)
            if "MemberWelcome" in eventsAllowed[guildID]:
                log.info(
                    f"MemberVerifiedRole: {configName}, {after.id}: {after.display_name}"
                )
                guild = after.guild
                if guild.system_channel is None:
                    return
                toSend = (
                    f"{after.mention}, Welcome to {after.guild.name}"
                    + config.txt_TpFwelcome
                )
                await guild.system_channel.send(toSend)

        elif before.display_name != after.display_name:
            if "MemberNameChange" in eventsAllowed[guildID]:
                usrDic = {
                    "type": "MemberNameChange",
                    "auth": before,
                    "exta": after,
                    "chanAudit": audit,
                }
                log.info(
                    f"UserNameChange: {configName}, {after.id}: {before.display_name} | {after.display_name}"
                )
                await auditLogger.logEmbed(self, usrDic)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log to audit-log channel when member leaves."""
        await self.bot.wait_until_ready()
        guildID = str(member.guild.id)
        eventJSON = readJSON("eventConfig")
        eventsAllowed = eventJSON["event"]
        guildsList = eventJSON["guild"]
        if guildID not in guildsList:
            return
        if "MemberLeave" in eventsAllowed[guildID]:
            global onMemberFired
            onMemberFired = True
            configName = guildsList[guildID]
            audit = getChan(guild=configName, chan="Audit", admin=True)
            guildData = self.bot.get_guild(member.guild.id)
            await auditLogger.userRemove(self, member, audit, guildData)
            await asyncio.sleep(3)
            onMemberFired = False

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload):
        await self.bot.wait_until_ready()
        guildID = str(payload.guild_id)
        await asyncio.sleep(1.5)
        eventJSON = readJSON("eventConfig")
        eventsAllowed = eventJSON["event"]
        guildsList = eventJSON["guild"]
        global onMemberFired
        if onMemberFired:
            return
        if guildID not in guildsList:
            return
        if "MemberLeave" in eventsAllowed[guildID]:
            guildData = self.bot.get_guild(payload.guild_id)
            guildCount = guildData.member_count
            configName = guildsList[guildID]
            audit = getChan(guild=configName, chan="Audit", admin=True)
            log.info(f"RawMemberLeave: {configName}, {payload.user}")
            usrDic = {
                "type": "RawMemberLeave",
                "auth": payload.user,
                "guildExta": guildCount,
                "chanAudit": audit,
            }
            await auditLogger.logEmbed(self, usrDic)
            onMemberFired = False

    @commands.Cog.listener()
    async def on_member_ban(self, guild, usr):
        """Log to audit-log channel when member is banned."""
        await self.bot.wait_until_ready()
        guildID = str(guild.id)
        eventJSON = readJSON("eventConfig")
        eventsAllowed = eventJSON["event"]
        guildsList = eventJSON["guild"]
        if guildID not in guildsList:
            return
        if "MemberBan" in eventsAllowed[guildID]:
            configName = guildsList[guildID]
            log.info(f"MemberBan: {configName}, {usr.id}, {usr.display_name}")
            audit = getChan(guild=configName, chan="Audit", admin=True)
            await auditLogger.checkKickBan(self, usr, audit, guild)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, usr):
        """Log to audit-log channel when member is unbanned."""
        await self.bot.wait_until_ready()
        guildID = str(guild.id)
        eventJSON = readJSON("eventConfig")
        eventsAllowed = eventJSON["event"]
        guildsList = eventJSON["guild"]
        if guildID not in guildsList:
            return
        if "MemberUnban" in eventsAllowed[guildID]:
            configName = guildsList[guildID]
            log.info(f"MemberUnban: {configName}, {usr.id}, {usr.display_name}")
            audit = getChan(guild=configName, chan="Audit", admin=True)
            usrDic = {"type": "MemberUnban", "auth": usr, "chanAudit": audit}
            await auditLogger.logEmbed(self, usrDic)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        await self.bot.wait_until_ready()
        guildID = str(payload.guild_id)
        eventJSON = readJSON("eventConfig")
        eventsAllowed = eventJSON["event"]
        guildsList = eventJSON["guild"]
        if guildID not in guildsList:
            return
        if "MessageDelete" in eventsAllowed[guildID]:
            configName = guildsList[guildID]
            log.debug(f"MessageDelete: {configName}")
            audit = getChan(guild=configName, chan="Audit", admin=True)
            message = payload.cached_message
            if message is not None:
                logMess.info(
                    f"""MessageID: {message.id}:
				Author: {message.author.id}: {message.author.name} | {message.author.display_name};
				\nContent: '' {message.content} ''"""
                )
                usrDic = {"type": "MessageDelete", "mess": message, "chanAudit": audit}
            else:
                log.info(
                    f"R_M_D; MessageID: {payload.message_id}, ChannelID: {payload.channel_id}"
                )
                usrDic = {
                    "type": "RawMessageDelete",
                    "mess": payload.message_id,
                    "chan": payload.channel_id,
                    "chanAudit": audit,
                }
            await auditLogger.logEmbed(self, usrDic)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        """Check for Author in message and adds heart reaction. Restricted to artwork channel in TpF server."""
        await self.bot.wait_until_ready()
        guildID = str(ctx.guild.id)
        eventJSON = readJSON("eventConfig")
        eventsAllowed = eventJSON["event"]
        guildsList = eventJSON["guild"]
        configName = guildsList[guildID]
        log.debug(f"{configName}, {guildID}")
        if "Artwork" in eventsAllowed[guildID]:
            artChan = getChan(configName, "Artwork")
            if ctx.channel.id == artChan:
                log.debug("AW listener")
                if "author" in ctx.content.casefold():
                    await ctx.add_reaction(config.emoHeart)
                    log.info("AW Reaction")
                    return
                else:
                    log.debug("AW")
        if "ModPreview" in eventsAllowed[guildID]:
            nmrChan = getChan(configName, "NewModRelease")
            nmpChan = getChan(configName, "NewModPreview")
            globalNMPChan = getChan("TPFGuild", "NewModPreview")
            if (ctx.channel.id == nmrChan) and (ctx.author.bot is False):
                log.debug("NMR listener")
                nmp = await self.bot.fetch_channel(nmpChan)
                globalPreviewChan = await self.bot.fetch_channel(globalNMPChan)
                if ("ModPreviewGlobal" in eventsAllowed[guildID]) and (
                    guildID != str(readJSON("config")["TPFGuild"]["ID"])
                ):
                    globalPreview = True
                else:
                    globalPreview = False
                await modRelease(
                    ctx=ctx,
                    chan=nmp,
                    globalPreviewChan=globalPreviewChan,
                    globalPreview=globalPreview,
                )
                log.info("modReleaseSent")
        if "Battles" in eventsAllowed[guildID]:
            BattlesChan = getChan(configName, "infoBattles")
            if ctx.channel.id == BattlesChan:
                log.debug("vkListener")
                if config.emoCheck in ctx.content:
                    await ctx.add_reaction(config.emoCheck)
                    log.info("VK_Checkmark")
                if config.emoTmbUp in ctx.content:
                    await ctx.add_reaction(config.emoTmbUp)
                    log.info("VK_ThumbsUp")


def setup(bot: commands.Bot):
    bot.add_cog(generalEvent(bot))


# MIT APasz
