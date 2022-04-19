print ("CogTpF")
import logging
import re
import textwrap

import nextcord
import nextcord.ext
from nextcord import Embed, Interaction, slash_command, SlashOption
from nextcord.ext import commands
from nextcord.ext.commands.cooldowns import BucketType

log = logging.getLogger("discordGeneral")
logMess = logging.getLogger('discordMessages')

import config
from config import userDiction as usrDic

from cogs.auditlog import *
from util.fileUtil import blacklistCheck
from util.apiUtil import *


localcf_chan_audit = config.chan_TpFaudit
localcf_guild_id = config.TpFguild
localcf_chan_nmr = config.chan_TpFnmr
localcf_chan_nmp = config.chan_TpFnmp

class tpf(commands.Cog, name="TpF server"):
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
		log.info(f"MemberJoin: {member.id},{member.display_name}")
		audit = localcf_chan_audit
		guildCount = member.guild.member_count
		usrDic = {'type': "U_J",
					'auth': member,
					'guildExta': guildCount,
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
			role = nextcord.utils.get(before.guild.roles, name=config.roles_TpFvri)
			await after.add_roles(role,atomic=True)
			log.info(f"UserAccept: {after.id}: {after.display_name}")
			await auditlog.embed(self, usrDic)

			guild = after.guild
			if guild.system_channel is None: return
			toSend = f'{after.mention}, Welcome to {after.guild.name}'+config.txt_TpFwelcome
			if guild.system_channel:
				await guild.system_channel.send(toSend)
			else:
				log.error("Unable to find system channel")
				chan = self.bot.get_channel(config.chan_TpFwel)
				await chan.send(toSend)
		
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

	async def modPreview(self, dets, chan, platform):
		log.debug("modPreview")
		NSFW = False
		auth = None
		authURL = None
		authIcon = None
		desc = None
		createdAt = None
		updatedAt = None
		modThumb = None
		tags = []
		if platform == "steam":
			createdAt = dets['time_created']
			updatedAt = dets['time_updated']
			modName = dets['title']
			auth = dets['personaname']
			authIcon = dets['avatarmedium']
			authURL = dets['profileurl']
			desc = dets['description']
			desc = textwrap.shorten(desc, width=250, placeholder='...')
			markTags = ["[h1]", "[/h1]", "[h2]", "[/h2]", "[b]", "[/b]", "[i]", "[/i]", "[strike]", "[/strike]", "[spoiler]", "[/spoiler]", "[noparse]", "[/noparse]", "[hr]", "[/hr]", "[list]", "[/list]", "[*]", "[code]", "[/code]"]
			for t in markTags:
				desc = desc.replace(t, '')
			desc = f"```\n{desc}\n```"
			modThumb = dets['preview_url']
			url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={dets['publishedfileid']}"
			tagList = dets['tags']
			for t in tagList:
				d = t['tag']
				tags.append(d)
			if tags is not None: tags = ', '.join(tags)
			e = nextcord.Embed(title=f"Workshop Mod Published;\n{modName}",
			colour=config.col_steam,
			url=url)
				
		elif platform == "nexus":
			createdAt = dets['created_timestamp']
			updatedAt = dets['updated_timestamp']
			modName = dets['name']
			auth = dets['author']
			authIcon = None
			authURL = dets['uploaded_users_profile_url']
			desc = dets['summary']
			tagRM = re.compile(r'<[^>]+>')
			desc = tagRM.sub('', desc)
			desc = f"```\n{desc}\n```"
			modThumb = dets['picture_url']
			url = f"https://www.nexusmods.com/{dets['domain_name']}/mods/{dets['mod_id']}"
			e = nextcord.Embed(title=f"NexusMods Mod Published;\n{modName}",
			colour=config.col_nexusmods,
			url=url)
			NSFW = dets['contains_adult_content']
			if NSFW is True:
				e.insert_field_at(1, name="NSFW", value="**`TRUE`**", inline=False)
		
		elif platform == "tpfnet":
			modid = dets['ID']
			name = dets['name']
			name = name.replace('-', ' ')
			name = name.removesuffix('/')
			url = f"https://www.transportfever.net/filebase/index.php?entry/{modid}"
			desc = "TpF|Net not currently supported but here is an embed anyway :)"
			e = nextcord.Embed(title=f"TPF|NET Mod Published;\n{name}",
			colour=config.col_tpfnet,
			url=url)
		
		else:
			e = nextcord.Embed(title="Mod Published",
			colour=config.config.col_neutLight,
			url=None)
		if auth and authURL and authIcon:
			e.set_author(name=auth, url=authURL, icon_url=authIcon)
		elif (auth and authURL) and not authIcon:
			e.set_author(name=auth, url=authURL)
		elif auth and not (authURL or authIcon):
			e.set_author(name=auth)
		
		#e.add_field(name="Name", value=f"{modName}", inline=True)
		if desc is not None: e.add_field(name="Description", value=desc, inline=False)
		if createdAt is not None:
			e.add_field(name="Published", value=f"<t:{createdAt}:R>", inline=True)
			if not createdAt <= updatedAt <= (createdAt + 3600):
				e.add_field(name="Updated", value=f"<t:{updatedAt}:R>", inline=True)
		if len(tags) != 0: e.add_field(name="Tags", value=tags, inline=False)
		if (NSFW is False) and (modThumb is not None): e.set_image(url=modThumb)
		await chan.send(embed = e)

	@commands.Cog.listener()
	async def on_message(self, ctx):
		"""Check for Author in message and adds heart reaction. Restricted to artwork channel in TpF server."""
		if ctx.channel.id == config.chan_TpFaw:
			log.debug("AW listener")
			if 'author' in ctx.content.lower():
				await ctx.add_reaction(config.emoHeart)
				log.info("AW Reaction")
				return
			else: log.debug("AW")
		if (ctx.channel.id == localcf_chan_nmr) and (ctx.author.bot is False):
			print("NMR listener")
			cont = ctx.content
			mess = cont.split("\n")
			chan = await self.bot.fetch_channel(localcf_chan_nmp)
			for l in mess:
				#print(f"L: {l}")
				if re.search(r'https:', l):
					#l = l.replace(' ','')
					urlDic = parseURL(l)
					ID = urlDic['ID']
					game = urlDic['game']
					plat = urlDic['platform']
					err = "There was an error. "
					if plat == "steam":
						dets = steamWSGet(ID)
						if isinstance(dets, int):
							err = err+str(dets)
							log.error(f"steamWS | {dets}")
							await ctx.channel.send(err)
							return
						usrID = int(dets['creator'])
						author = steamUsrGet(usrID)
						if isinstance(author, int):
							err = err+str(author)
							log.error(f"steamUsr | {dets}")
							await ctx.channel.send(err)
							return
						dets = dets | author
						await self.modPreview(dets, chan, plat)
					if plat == "nexus":
						dets = nexusModGet(game, ID)
						if isinstance(dets, int):
							err = err+str(dets)
							log.error(f"nexus | {dets}")
							await ctx.channel.send(err)
							return
						await self.modPreview(dets, chan, plat)
					if plat == "tpfnet": #not supported at present.
						if not re.search(r'filebase', cont): continue
						dets = tpfnetModGet(ID)
						# if isinstance(dets, int):
						# 	err = err+str(dets)
						# 	log.error(f"tpfnet | {dets}")
						# 	await ctx.channel.send(err)
						# 	return
						dets = {
							'ID':ID,
							'name':game
						}
						await self.modPreview(dets, chan, plat)
					await asyncio.sleep(0.1)
			print("NMR Done")

			
			
			
			
			
			
			
			# if "transportfever" in mess:
			# 	num = re.findall(r'\d+', mess)
			# 	print(num)
			# 	dets = tpfnetModGet()
			# if "steamcommunity" in mess:
			# 	chan = await self.bot.fetch_channel(localcf_chan_nmp)
			# 	num = re.findall(r'\d+', mess)
			# 	IDs = []
			# 	for n in num:
			# 		if int(n) > 763167186: #First TpF1 ws item is 763167187
			# 			IDs.append(n)
			# 	for s in IDs:
			# 		dets = steamWSGet(s)
			# 		usrID = int(dets['creator'])
			# 		author = steamUsrGet(usrID)
			# 		await self.modPreview(dets, author, chan, "steam")
			# 		await asyncio.sleep(0.5)
			# if "nexusmods" in mess:
			# 	chan = await self.bot.fetch_channel(localcf_chan_nmp)
			# 	num = re.findall(r'\d+', mess)
			# 	dets = nexusModGet("transportfever2", int(num[0]))
			# 	await self.modPreview(dets, author, chan, "nexus")

				#print(len(num))
			#wsID = int(ctx.content)
			#data = steamGet(IDs)
			#print(data)
			#chan = await self.bot.fetch_channel(localcf_chan_nmp)
			#await chan.send(data)

def setup(bot: commands.Bot):
	bot.add_cog(tpf(bot))

#MIT APasz