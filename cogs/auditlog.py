print ("CogAuditLog")
import asyncio
import datetime
import logging
import time
from datetime import datetime, timezone

import nextcord
from dateutil import relativedelta
from nextcord.ext import commands

log = logging.getLogger("discordGeneral")

import config
from config import userDiction as usrDic


class auditlog(commands.Cog, name="AuditLogging"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		log.debug("Ready")

	async def userRemove(self, data, auditID, guildData):
		await self.bot.wait_until_ready()
		log.debug(f"userRemove")
		log.info(f"MemberRemove: {data.id}: {data.display_name}")
		usr = data
		guildCount = guildData.member_count
		usrDic = {'type': "U_R",
					'auth': usr,
					'chanAudit': auditID,
					'guildExta': guildCount}
		await auditlog.embed(self, usrDic)
		await asyncio.sleep(0.05)
		await auditlog.checkKickBan(self, usr, auditID, guildData, uR=1)

	async def checkKickBan(self, usr, auditID, guildData, uR=0):
		await self.bot.wait_until_ready()
		async for entry in guildData.audit_logs(limit=1):
				auditLog = entry
		curStamp = int(time.time())
		checkStamp = curStamp - 5
		crtd = auditLog.created_at
		auditStamp = int(round(crtd.timestamp()))
		if auditStamp > checkStamp:
			if "kick" in auditLog.action and usr.name == auditLog.guild.name:
				if hasattr(auditLog, "reason"): reason = auditLog.reason
				else: reason = None
				log.info(f"MemberKick: {usr.id}: {usr.name}: R;\n{reason}")
				usrDict = usrDic
				usrDict = {'type': "U_K",
							'auth': usr,
							'mess': reason,
							'chanAudit': auditID}
				await auditlog.embed(self, usrDict)
			if uR == 1: return
			elif "ban" in auditLog.action and usr.name == auditLog.guild.name:
				if hasattr(auditLog, "reason"): reason = auditLog.reason
				else: reason = None
				log.info(f"MemberBan: {usr.id}: {usr.display_name}: R;\n{reason}")
				usrDict = usrDic
				usrDict = {'type': "U_B",
							'auth': usr,
							'mess': reason,
							'chanAudit': auditID}
				await auditlog.embed(self, usrDict)
				uR = 0


	async def embed(self, data):
		await self.bot.wait_until_ready()
		stdName = "Author ID | Account | Nick | Live Nick"
		shtName = "Author ID | Account | Live Nick"
		type = (data['type'])
		#There has to be a better way to assign None to multiple variables.
		fValue0 = fValue1 = fValue2 = fValue3 = fValue4 = fValue5 = fValue6 = fValue7 = fValue8 = fValue9 = None
		fName0 = fName1 = fName2 = fName3 = fName4 = fName5 = fName6 = fName7 = fName8 = fName9 = None
		if "R_M_D" == type:
			title = "Uncached Message Deleted"
			fName1 = "Channel"
			fValue1 = f"<#{(data['chan'])}>"
			fName2 = "Message ID"
			fValue2 = (data['mess'])
			e = nextcord.Embed(title=title, colour=config.col_warning)
		
		elif "M_D" == type:
			title = "Message Deleted"
			mess = (data['mess'])
			a = len(mess.attachments)
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
				fValue5 = f"```\n{mess.content}\n```"
			if a != 0:
				fName6 = "Attachments"
				fValue6 = a
			e = nextcord.Embed(title=title, colour=config.col_warning)
		
		elif "U_B" == type:
			title = "User Banned"
			usr = (data['auth'])
			mess = (data['mess'])
			fName4 = stdName
			auth = usr.name
			authDN = usr.display_name
			authID = usr.id
			fValue4 = f"{authID}\n{auth}\n{authDN}\n<@{authID}>"
			if mess is not None:
				fName5 = "Reason"
				fValue5 = f"```\n{mess}\n```"
			e = nextcord.Embed(title=title, colour=config.col_negative)
		
		elif "U_uB" == type:
			title = "User Unbanned"
			usr = (data['auth'])
			fName4 = shtName
			auth = usr.name
			authID = usr.id
			fValue4 = f"{authID}\n{auth}\n<@{authID}>"
			e = nextcord.Embed(title=title, colour=config.col_neutDark)
		
		elif "U_K" == type:
			title = "User Kicked"
			usr = (data['auth'])
			mess = (data['mess'])
			fName4 = shtName
			auth = usr.name
			authID = usr.id
			fValue4 = f"{authID}\n{auth}\n<@{authID}>"
			if mess is not None:
				fName5 = "Reason"
				fValue5 = f"```\n{mess}\n```"
			e = nextcord.Embed(title=title, colour=config.col_warning)
		
		elif "U_R" == type:
			title = "User Left"
			usr = (data['auth'])
			guildCount = (data['guildExta'])
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
			#Dunno why. replace(microsecond=0) only seems to work this way
			dT = relativedelta.relativedelta(curTimeTZ, joinedTZ)
			y, m, w, d, h, t, s = (
				dT.years,
				dT.months,
				dT.weeks,
				dT.days,
				dT.hours,
				dT.minutes,
				dT.seconds,)
			d = d + (w * 7)
			fValue2 = f"""**Joined**: <t:{joinedStamp}:f>
			**Unix**: {joinedStamp}
			**Duration**; Y/M/D | H:M:S\n {y:02d}/{m:02d}/{d:02d} | {h:02d}:{t:02d}:{s:02d}
			**Member Count**: {guildCount}"""
			e = nextcord.Embed(title=title, colour=config.col_neutMid)
	
		elif "U_J" == type:
			title = "User Joined"
			usr = (data['auth'])
			fName1 = shtName
			auth = usr.name
			authID = usr.id
			fValue1 = f"{authID}\n{auth}\n<@{authID}>"
			fName2 = "Account Created"
			crtd = usr.created_at
			crtdStamp = int(round(crtd.timestamp()))
			fValue2 = f"<t:{crtdStamp}:f>\n<t:{crtdStamp}:R>\n**Unix**: {crtdStamp}"
			e = nextcord.Embed(title=title, colour=config.col_positive2)
		
		elif "U_A" == type:
			title = "User Accepted"
			usr = (data['auth'])
			guildCount = (data['guildExta'])
			fName1 = shtName
			auth = usr.name
			authID = usr.id
			fValue1 = f"{authID}\n{auth}\n<@{authID}>"
			fName2 = "Member Count"
			fValue2 = guildCount
			e = nextcord.Embed(title=title, colour=config.col_positive)
		
		elif "U_N_C" == type:
			title = "User Name Change"
			before = (data['auth'])
			after = (data['exta'])
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
			e = nextcord.Embed(title=title, colour=config.col_neutDark)
		
		elif "A_G" == type:
			title = "User requested file"
			usr = (data['auth'])
			file = (data['exta'])
			fName1 = shtName
			fValue1 = f"{usr.id}\n{usr.name}\n<@{usr.id}>"
			fName2 = "File"
			fValue2 = file
			e = nextcord.Embed(title=title, colour=config.col_neutLight)
		
		else:
			title = "Unknown Event"
			e = nextcord.Embed(title=title, colour=config.col_error)
		
		if fValue0 is not None: e.add_field(name=fName0, value=f"{fValue0}", inline=False)
		if fValue1 is not None: e.add_field(name=fName1, value=f"{fValue1}", inline=True)
		if fValue2 is not None: e.add_field(name=fName2, value=f"{fValue2}", inline=True)
		if fValue3 is not None: e.add_field(name=fName3, value=f"{fValue3}", inline=True)
		if fValue4 is not None: e.add_field(name=fName4, value=f"{fValue4}", inline=False)
		if fValue5 is not None: e.add_field(name=fName5, value=f"{fValue5}", inline=False)
		if fValue6 is not None: e.add_field(name=fName6, value=f"{fValue6}", inline=False)
		if fValue7 is not None: e.add_field(name=fName7, value=f"{fValue7}", inline=True)
		if fValue8 is not None: e.add_field(name=fName8, value=f"{fValue8}", inline=True)
		if fValue9 is not None: e.add_field(name=fName9, value=f"{fValue9}", inline=True)
		unix = int(time.time())
		e.set_footer(text=f"UNIX: {unix}")
		audit = (data['chanAudit'])
		if audit is not None:
			chan = self.bot.get_channel(audit)
			await chan.send(embed = e)



		#e = nextcord.Embed(title=messStat, colour=config.col_warning)
		#e.add_field(name="MessageID", value=f"{messID}", inline=True)

def setup(bot: commands.Bot):
	bot.add_cog(auditlog(bot))

#MIT APasz