import asyncio
from email import message
import logging
import textwrap
import time

from config import dataObject
from config import genericConfig as gxConfig
from util.genUtil import getCol, formatTime

print("CogAuditLog")

log = logging.getLogger("discordGeneral")
try:
    log.debug("TRY AUDIT_LOG IMPORT MODULES")
    import datetime
    from datetime import datetime, timezone

    import nextcord
    from dateutil import relativedelta
    from nextcord.ext import commands
except Exception:
    log.exception("AUDIT_LOG IMPORT MODULES")


class auditLogger(commands.Cog, name="AuditLogging"):
    """Class containing functions related to the creation of auditlog entries"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.debug(f"{self.__cog_name__} Ready")

    async def userRemove(self, data: dataObject):
        """Triggers the Member/User left entry. As well as function to check if user was kicked/banned"""
        await self.bot.wait_until_ready()
        dataObj = data
        log.info(
            f"MemberRemove: {data.userObject.id}: {data.userObject.display_name}")
        dataObj.TYPE = "MemberLeave"
        dataObject.count = data.guildObject.member_count
        await auditLogger.logEmbed(self, dataObj)
        await asyncio.sleep(0.05)
        await auditLogger.checkKickBan(self, data, uR=1)

    async def checkKickBan(self, data: dataObject, uR=0):
        """Check if a member/user was kicked or banned, if so trigger the kicked or banned entry"""
        await self.bot.wait_until_ready()
        dataObj = data
        log.debug(
            f"usrID={dataObj.userObject.id} | auditChan={dataObj.auditChan.id} | type={dataObj.TYPE}")
        async for entry in data.guildObject.audit_logs(limit=3):
            log.debug(entry.action)
            # if ("kick" or "ban") not in entry.action: continue
            auditLog = entry
            curStamp = int(time.time())
            checkStamp = curStamp - 15
            crtd = auditLog.created_at
            auditStamp = int(round(crtd.timestamp()))
            if auditStamp > checkStamp:
                if hasattr(auditLog, "reason"):
                    reason = auditLog.reason
                else:
                    reason = None
                dataObj.reason = reason
                usr = dataObj.userObject
                if "kick" in auditLog.action:
                    log.info(f"MemberKick: {usr.id}: {usr.name}: {reason=}")
                    dataObj.TYPE = "MemberKick"
                    log.debug(f"{dataObj.TYPE=}")
                    await auditLogger.logEmbed(self, dataObj)
                if uR == 1:
                    return
                elif "ban" in auditLog.action:
                    log.info(
                        f"MemberBan: {usr.id}: {usr.display_name}: {reason=}")
                    dataObj.TYPE = "MemberBan"
                    log.debug(f"{dataObj=}")
                    await auditLogger.logEmbed(self, dataObj)
                    uR = 0

    async def logEmbed(self, auditInfo: dataObject):
        """Format each type of entry and send to the appropriate audit channel"""
        await self.bot.wait_until_ready()
        stdName = "Author ID | Account | Nick | Live Nick"
        shtName = "Author ID | Account | Live Nick"
        minName = "Author ID | Account"
        TYPE = auditInfo.TYPE
        # There has to be a better way to assign None to multiple variables.
        # fmt: off
        fValue0 = fValue1 = fValue2 = fValue3 = fValue4 = fValue5 = fValue6 = fValue7 = fValue8 = fValue9 = None
        fName0 = fName1 = fName2 = fName3 = fName4 = fName5 = fName6 = fName7 = fName8 = fName9 = None
        # fmt: on
        unix = int(time.time())
        footer = f"UNIX: {unix}"
        log.debug(f"logType: {TYPE}")
        if "RawMessageDelete" == TYPE:
            log.debug(TYPE)
            title = "Uncached Message Deleted"
            fName1 = "Channel"
            fValue1 = f"<#{(auditInfo.channelID)}>"
            fName2 = "Message ID"
            fValue2 = auditInfo.messageID
            e = nextcord.Embed(title=title, colour=getCol("warning"))

        elif "MessageDelete" == TYPE:
            log.debug(TYPE)
            title = "Message Deleted"
            mess = auditInfo.messageObject
            attach = len(mess.attachments)
            fName1 = "Channel"
            fValue1 = f"<#{mess.channel.id}>"
            fName2 = "Message Created"
            crtd = mess.created_at
            crtdStamp = int(round(crtd.timestamp()))
            fValue2 = f"<t:{crtdStamp}:f>\n**Unix**: {crtdStamp}"
            fName4 = stdName
            auth = mess.author.name
            authDN = mess.author.display_name
            authID = mess.author.id
            fValue4 = f"{authID}\n{auth}\n{authDN}\n<@{authID}>"
            if mess.content is not None:
                fName5 = "Message"
                txt = cont = mess.content.replace("`", "")
                if len(cont) > 1000:
                    txt = textwrap.shorten(
                        cont, width=1000, placeholder=" ...")
                    footer = footer + " | Full message content in bot log."
                fValue5 = f"\n```\n{txt}\n```"
            if attach != 0:
                fName6 = "Attachments"
                fValue6 = attach
            e = nextcord.Embed(title=title, colour=getCol("warning"))

        elif "MemberBan" == TYPE:
            log.debug(TYPE)
            title = "Member Banned"
            usr = auditInfo.userObject
            fName4 = stdName
            auth = usr.name
            authDN = usr.display_name
            authID = usr.id
            fValue4 = f"{authID}\n{auth}\n{authDN}\n<@{authID}>"
            if auditInfo.reason is not None:
                fName5 = "Reason"
                fValue5 = f"```\n{auditInfo.reason}\n```"
            e = nextcord.Embed(title=title, colour=getCol("negative"))

        elif "MemberUnban" == TYPE:
            log.debug(TYPE)
            title = "Member Ban Revoked"
            usr = auditInfo.userObject
            fName4 = shtName
            auth = usr.name
            authID = usr.id
            fValue4 = f"{authID}\n{auth}\n<@{authID}>"
            e = nextcord.Embed(title=title, colour=getCol("neutral_Dark"))

        elif "MemberKick" == TYPE:
            log.debug(TYPE)
            title = "Member Kicked"
            usr = auditInfo.userObject
            fName4 = shtName
            auth = usr.name
            authID = usr.id
            fValue4 = f"{authID}\n{auth}\n<@{authID}>"
            if auditInfo.reason is not None:
                fName5 = "Reason"
                fValue5 = f"```\n{auditInfo.reason}\n```"
            e = nextcord.Embed(title=title, colour=getCol("negative_Low"))

        elif "MemberLeave" == TYPE:
            log.debug(TYPE)
            title = "Member Left"
            usr = auditInfo.userObject
            fName1 = stdName
            auth = usr.name
            authDN = usr.display_name
            authID = usr.id
            fValue1 = f"{authID}\n{auth}\n{authDN}\n<@{authID}>"
            fName2 = "Server Stats"
            joined = usr.joined_at
            joinedTZ = joined.replace(microsecond=0)
            joinedTZ = joinedTZ.replace(tzinfo=timezone.utc)
            joinedTZ = joinedTZ.replace(microsecond=0)
            joinedStamp = int(round(joined.timestamp()))
            curTime = datetime.utcnow()
            curTimeTZ = curTime.replace(microsecond=0)
            curTimeTZ = curTimeTZ.replace(tzinfo=timezone.utc)
            curTimeTZ = curTimeTZ.replace(microsecond=0)
            # Dunno why. replace(microsecond=0) only seems to work this way
            dT = relativedelta.relativedelta(curTimeTZ, joinedTZ)
            y, m, w, d, h, t, s = (
                dT.years,
                dT.months,
                dT.weeks,
                dT.days,
                dT.hours,
                dT.minutes,
                dT.seconds,
            )
            d = d + (w * 7)
            fValue2 = f"""**Joined**: <t:{joinedStamp}:f>
            **Unix**: {joinedStamp}
            **Duration**; Y/M/D | H:M:S\n {y:02d}/{m:02d}/{d:02d} | {h:02d}:{t:02d}:{s:02d}
            **Member Count**: {auditInfo.count}"""
            e = nextcord.Embed(title=title, colour=getCol("neutral_Mid"))

        elif "RawMemberLeave" == TYPE:
            log.debug(TYPE)
            title = "Uncached User Left"
            usr = auditInfo.userObject
            fName1 = "ID | Account"
            fValue1 = f"{usr.id} | {usr.name}"
            fName2 = "Server Stats"
            fValue2 = f"**Member Count**: {auditInfo.count}"
            e = nextcord.Embed(title=title, colour=getCol("neutral_Mid"))

        elif "MemberJoin" == TYPE:
            log.debug(TYPE)
            title = "User Joined"
            usr = auditInfo.userObject
            fName1 = shtName
            auth = usr.name
            authID = usr.id
            fValue1 = f"{authID}\n{auth}\n<@{authID}>"
            fName2 = "Account Created"
            crtd = usr.created_at
            crtdStamp = int(round(crtd.timestamp()))
            fValue2 = f"<t:{crtdStamp}:f>\n<t:{crtdStamp}:R>\n**Unix**: {crtdStamp}\n**Member Count**: {auditInfo.count}"
            e = nextcord.Embed(title=title, colour=getCol("positive2"))

        elif "MemberAccept" == TYPE:
            log.debug(TYPE)
            title = "User Accepted"
            usr = auditInfo.userObject
            fName1 = shtName
            auth = usr.name
            authID = usr.id
            fValue1 = f"{authID}\n{auth}\n<@{authID}>"
            fName2 = "Member Count"
            fValue2 = auditInfo.count
            e = nextcord.Embed(title=title, colour=getCol("positive"))

        elif "MemberJoinRecentCreation" == TYPE:
            log.debug(TYPE)
            title = "Recently Created User Joined"
            usr = auditInfo.userObject
            fName0 = minName
            auth = usr.name
            authID = usr.id
            fValue0 = f"{authID}\n{auth}"
            fName2 = "Account Created"
            accCrtdTime = formatTime.time_format(total=auditInfo.count)
            fValue2 = f"{accCrtdTime} ago\nSee auditlog channel for more info."
            e = nextcord.Embed(title=title, colour=getCol("warning_Low"))

        elif "MemberNameChange" == TYPE:
            log.debug(TYPE)
            title = "Member Name Change"
            before = auditInfo.userObject
            after = auditInfo.userObjectExtra
            auth = before.name
            authID = before.id
            authBe = before.display_name
            authAf = after.display_name
            fName0 = "Account ID | Name"
            fValue0 = f"{authID} | {auth}"
            fName1 = "Before"
            fValue1 = authBe
            fName2 = "After"
            fValue2 = authAf
            e = nextcord.Embed(title=title, colour=getCol("neutral_Dark"))

        elif "CommandAuditGet" == TYPE:
            log.debug(TYPE)
            title = "Member requested file"
            usr = auditInfo.userObject
            fName1 = shtName
            fValue1 = f"{usr.id}\n{usr.name}\n<@{usr.id}>"
            fName2 = "File"
            fValue2 = auditInfo.filename
            e = nextcord.Embed(title=title, colour=getCol("neutral_Light"))

        elif ("BlacklistAdd" == TYPE) or ("BlacklistRemove" == TYPE):
            log.debug(TYPE)
            auth = auditInfo.userObject
            usr = auditInfo.commandArg1
            fName1 = shtName
            fValue1 = f"{usr.id}\n{usr.name}\n<@{usr.id}>"
            fName2 = "Invoked by;"
            fValue2 = f"{auth.id}\n{auth.name}\n<@{auth.id}>"
            fName4 = "Reason"
            fValue4 = f"```\n{auditInfo.reason}\n```"
            if TYPE == "BlacklistAdd":
                if auditInfo.category != "General":
                    title = f"User Blacklisted [{auditInfo.category}]"
                else:
                    title = f"User Blacklisted"
                e = nextcord.Embed(title=title, colour=getCol("error"))
            else:
                if auditInfo.category != "General":
                    title = f"User Unblacklisted [{auditInfo.category}]"
                else:
                    title = f"User Unblacklisted"
                e = nextcord.Embed(
                    title=title, colour=getCol("neutral_Bright"))

        elif "CommandPurge" == TYPE:
            log.debug(TYPE)
            title = "Message Purge"
            usr = auditInfo.userObject
            fName1 = "Invoked by;"
            fValue1 = f"{usr.id}\n{usr.name}\n<@{usr.id}>"
            fName2 = "Number Purged"
            fValue2 = f"**{auditInfo.limit}** in <#{auditInfo.channelID}>"
            e = nextcord.Embed(title=title, colour=getCol("error"))

        elif "CommandToggleEvent" == TYPE:
            log.debug(TYPE)
            title = "Event Toggled"
            usr = auditInfo.userObject
            fName0 = shtName
            fValue0 = f"{usr.id}\n{usr.name}\n<@{usr.id}>"
            fName2 = f"{auditInfo.category}"
            fValue2 = f"{auditInfo.commandArg1} -> {auditInfo.commandArg2}"
            e = nextcord.Embed(title=title, colour=getCol("warning"))

        elif "CommandGuildConfiguration" == TYPE:
            log.debug(TYPE)
            title = "Guild Configuration Changed"
            usr = auditInfo.userObject
            fName0 = shtName
            fValue0 = f"{usr.id}\n{usr.name}\n<@{usr.id}>"
            group = auditInfo.categoryGroup
            option = auditInfo.category
            value = auditInfo.commandArg1
            oldValue = auditInfo.commandArg2
            fName1 = f"{group} {option}"
            fValue1 = f"{oldValue}  ->  {value}"
            e = nextcord.Embed(title=title, colour=getCol("warning"))

        elif "CommandAutoReact" == TYPE:
            log.debug(TYPE)
            title = "AutoReact Configuration Changed"
            usr = auditInfo.userObject
            fName9 = "Invoked by;"
            fValue9 = f"{usr.id}\n{usr.name}\n<@{usr.id}>"
            from util.genUtil import toStr
            oldChannel = toStr(auditInfo.channelExtra)
            newChannel = toStr(auditInfo.channelList)
            changed = False
            if oldChannel != newChannel:
                fName3 = "Channels"
                fValue3 = f"{oldChannel}  ->  {newChannel}"
                changed = True

            oldMessage = toStr(auditInfo.messageExtra)
            newMessage = toStr(auditInfo.messageContent)
            if oldMessage != newMessage:
                fName4 = "Words/Emoji To Match"
                fValue4 = f"{oldMessage}  ->  {newMessage}"
                changed = True

            oldEmoji = auditInfo.emojiExtra
            newEmoji = auditInfo.emojiList
            if oldEmoji != newEmoji:
                fName5 = "Reactions"
                fValue5 = f"{oldEmoji}  ->  {newEmoji}"
                changed = True

            oldIsExact = auditInfo.flag0
            newIsExact = auditInfo.flagA
            if oldIsExact != newIsExact:
                fName6 = "Is Exact Match"
                fValue6 = f"{oldIsExact}  ->  {newIsExact}"
                changed = True
            if not changed:
                fName0 = "No change"
                fValue0 = "Command was invoked but no changes were made"

            e = nextcord.Embed(title=title, colour=getCol("warning"))

        else:
            log.debug(TYPE)
            title = f"Unknown Event: {TYPE}"
            e = nextcord.Embed(title=title, colour=getCol("neutral_Black"))

        if fValue0 is not None:
            e.add_field(name=fName0, value=f"{fValue0}", inline=False)
        if fValue1 is not None:
            e.add_field(name=fName1, value=f"{fValue1}", inline=True)
        if fValue2 is not None:
            e.add_field(name=fName2, value=f"{fValue2}", inline=True)
        if fValue3 is not None:
            e.add_field(name=fName3, value=f"{fValue3}", inline=True)
        if fValue4 is not None:
            e.add_field(name=fName4, value=f"{fValue4}", inline=False)
        if fValue5 is not None:
            e.add_field(name=fName5, value=f"{fValue5}", inline=False)
        if fValue6 is not None:
            e.add_field(name=fName6, value=f"{fValue6}", inline=False)
        if fValue7 is not None:
            e.add_field(name=fName7, value=f"{fValue7}", inline=True)
        if fValue8 is not None:
            e.add_field(name=fName8, value=f"{fValue8}", inline=True)
        if fValue9 is not None:
            e.add_field(name=fName9, value=f"{fValue9}", inline=True)
        e.set_footer(text=footer)
        log.info(
            f"_auditChan{type(auditInfo.auditChan)} | {auditInfo.auditChan=}")
        log.info(f"_auditID{type(auditInfo.auditID)} | {auditInfo.auditID=}")
        if isinstance(auditInfo.auditChan, nextcord.TextChannel):
            log.debug(f"{type(auditInfo.auditChan)}")
            try:
                log.debug(f"OBJ {auditInfo.auditChan=}")
                chan = auditInfo.auditChan
            except Exception:
                log.exception(f"OBJ {auditInfo.auditChan=}")
        elif isinstance(auditInfo.auditID, int | str):
            log.debug(f"{type(auditInfo.auditID)}")
            try:
                log.debug(f"ID {auditInfo.auditID=}")
                chan = self.bot.get_channel(auditInfo.auditID)
            except Exception:
                log.exception(f"ID {auditInfo.auditID=}")
        else:
            log.error("chan is None")
            try:
                chan = self.bot.get_channel(gxConfig.ownerAuditChan)
            except Exception:
                log.exception(f"chan None Try")
        log.info(f"AuditChan: {chan=}")
        try:
            await chan.send(embed=e)
        except Exception:
            log.exception(f"Send Auditlog Entry {TYPE=}")


def setup(bot: commands.Bot):
    bot.add_cog(auditLogger(bot))


# MIT APasz
