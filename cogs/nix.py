print ("CogNIX")
import logging

from nextcord.ext import commands

log = logging.getLogger("discordGeneral")
logMess = logging.getLogger('discordMessages')

import config
from config import userDiction as usrDic

from cogs.auditlog import *

localcf_chan_audit = config.chan_NIXaudit
localcf_guild_id = config.NIXguild

class nix(commands.Cog, name="AUS|NIX"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		log.debug("Ready")

	@commands.Cog.listener()
	async def on_member_join(self, member):
		"""Send welcome message when new user joins"""
		if member.bot:
			return
		guild = member.guild
		if guild.id != localcf_guild_id: return
		log.debug("on_member_join")
		log.info(f"MemberJoin: {member.id}: {member.display_name}")
		audit = localcf_chan_audit
		usrDic = {'type': "U_J",
					'auth': member,
					'chanAudit': audit}
		await auditlog.embed(self, usrDic)

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		"""Check if new user has passed membership, if so give role.
		Also log to autit-log when user nick changes."""
		if after.guild.id != localcf_guild_id: return
		log.debug("on_member_update")
		audit = localcf_chan_audit
		if before.pending and after.pending is True: return
		if before.pending and after.pending is False:
			log.info(f"UserAccept: {after.id}: {after.display_name}")
			guildCount = after.guild.member_count
			usrDic = {'type': "U_A",
						'auth': after,
						'guildExta': guildCount,
						'chanAudit': audit}
			log.info(f"UserAccept: {after.id}: {after.display_name}")
			await auditlog.embed(self, usrDic)

		if before.display_name != after.display_name:
			usrDic = {'type': "U_N_C",
						'auth': before,
						'exta': after,
						'chanAudit': audit}
			log.info(f"UserNameChange: {after.id}: {before.display_name} | {after.display_name}")
			await auditlog.embed(self, usrDic)

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		"""Log to audit-log channel when member leaves."""
		guildID = member.guild.id
		if guildID == localcf_guild_id:
			log.debug("on_member_remove")
			auditID = localcf_chan_audit
			guildData = self.bot.get_guild(guildID)
			await auditlog.userRemove(self, member, auditID, guildData)

	@commands.Cog.listener()
	async def on_member_ban(self, guild, usr):
		"""Log to audit-log channel when member is banned."""
		if guild.id == localcf_guild_id:
			log.debug("on_member_ban")
			auditID = localcf_chan_audit
			await auditlog.checkKickBan(self, usr, auditID, guild)

	@commands.Cog.listener()
	async def on_member_unban(self, guild, usr):
		"""Log to audit-log channel when member is unbanned."""
		if guild.id == localcf_guild_id:
			log.debug("on_member_unban")
			log.info(f"MemberBanRevoke: {usr.id}: {usr.name}")
			audit = localcf_chan_audit
			usrDic = {'type': "U_uB",
						'auth': usr,
						'chanAudit': audit}
			await auditlog.embed(self, usrDic)

	@commands.Cog.listener()
	async def on_raw_message_delete(self, payload):
		if payload.guild_id == localcf_guild_id:			
			log.debug("on_raw_message_delete")
			audit = localcf_chan_audit
			message = payload.cached_message
			if message is not None:
				logMess.info(f"""MessageID: {message.id}:
				Author: {message.author.id}: {message.author.name} | {message.author.display_name};
				\nContent: '' {message.content} ''""")
				usrDic = {'type': "M_D",
							'mess': message,
							'chanAudit': audit}
			else:
				log.info(f"R_M_D; MessageID: {payload.message_id}, ChannelID: {payload.channel_id}")
				usrDic = {'type': "R_M_D",
							'mess': payload.message_id,
							'chan': payload.channel_id,
							'chanAudit': audit}
			await auditlog.embed(self, usrDic)


def setup(bot: commands.Bot):
	bot.add_cog(nix(bot))

#MIT APasz