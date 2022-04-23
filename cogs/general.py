print ("CogGeneral")
import asyncio
import logging
import random
import time
import config

import nextcord
import pint
from nextcord import Embed, Interaction, SlashOption, slash_command
from nextcord.ext import application_checks, commands
from nextcord.ext.commands.cooldowns import BucketType

log = logging.getLogger("discordGeneral")
from util.fileUtil import readJSON
from util.genUtil import getCol, blacklistCheck

configuration = readJSON(filename = "config")
configGen = configuration['General']

class general(commands.Cog, name="General"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		log.debug("Ready")

	async def fact(self):
		e = (f"""I'm sorry, I lost the fact I was getting for you.
'An error occurred' Alert <@{config.ownerID}>""")
		try:
			facts = open('randomFact.txt').read().splitlines()
			if len(facts) == 0: return e
			factfull = random.choice(facts)
			factsplit = factfull.split(';')
			log.debug(f"factSplit {len(factsplit)}")
			index = str(factsplit[0])
			fact = str(factsplit[1].removeprefix(' '))
			source = str(factsplit[2].removeprefix(' '))
			if not source:
				source = "Someone forgot the source."
			if (source == "NotPublic") or (source == "Someone forgot the source."):
				e = nextcord.Embed(title=index, description=fact, colour=getCol('fact'))
			else:
				e = nextcord.Embed(title=index, description=fact, colour=getCol('fact'), url=source)
			e.set_footer(text=source)
			log.debug(f"f1:{index}, f2:{fact}, f3:{source}")
		except: pass
		return e

	@commands.command(name="fact", aliases=['randomFact'])
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def factCommand (self, ctx):
		"""Serves Random facts"""
		log.debug("factCommand")
		async with ctx.typing():
			fact = await self.fact()
			if isinstance(fact, Embed): await ctx.send(embed=fact)
			else: await ctx.send(fact)
			log.info(f"Fact: {ctx.author.id},{ctx.author.display_name}")
	
	@slash_command(name="fact", guild_ids=config.SlashServers)
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def factSlash(self, interaction: Interaction):
		"""Serves Random facts"""
		if not await blacklistCheck(ctx=interaction, blklstType="gen"): return
		log.debug("factSlash")
		fact = await self.fact()
		if isinstance(fact, Embed): await interaction.response.send_message(embed=fact)
		else: await interaction.response.send_message(fact)
		log.info(f"Fact: {interaction.user.id},{interaction.user.display_name}")


	@commands.command(name="ping")
	@commands.cooldown(1, 2.5, commands.BucketType.user) 
	async def ping(self, ctx: commands.Context, api:str=None):
		"""Gives ping to server in Melbourne, Australia"""
		log.debug("pingCommand")
		if api is not None:
			async with ctx.typing():
				せ = time.perf_counter()
				mess = await ctx.send('Ponging...')
				え = time.perf_counter()
				await asyncio.sleep(0.25)
				await mess.edit(content=f"Gateway: {round(self.bot.latency * 1000)}ms\nAPI: {round((え - せ) * 1000)}ms")
		else:
			await ctx.send(f"Ponging at {round(self.bot.latency * 1000)}ms")
		log.info(f"Ping: {ctx.author.id},{ctx.author.display_name}")

	@slash_command(name="ping", guild_ids=config.SlashServers)
	async def pingSlash(self, interaction:Interaction, api:str = SlashOption(
			name="api", description="Do you want to check API ping?", required=False)):
		"""Gives ping to server in Melbourne, Australia"""
		log.debug("pingSlash")
		BL = await blacklistCheck(ctx=interaction, blklstType="gen")
		print(BL)
		if BL is False: return
		if api is not None:
			せ = time.perf_counter()
			await interaction.response.send_message('Ponging...')
			え = time.perf_counter()
			await asyncio.sleep(0.25)
			await interaction.edit_original_message(content=f"Gateway: {round(self.bot.latency * 1000)}ms\nAPI: {round((え - せ) * 1000)}ms")
		else:
			await interaction.response.send_message(f"Ponging at {round(self.bot.latency * 1000)}ms")
		log.info(f"Ping: {interaction.user.id},{interaction.user.display_name}")

	@commands.command(name="info")
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def info(self, ctx: commands.Context, ver=None):
		"""Gives information about the bot"""
		log.debug("infoCommand")
		mV = configGen['verMajor']
		sV = configGen['VerMinor']
		pV = configGen['verPoint']
		Vn = configGen['verName']
		if ver is None:
			if config.botName == "SSCBot":
				txt1 = "Hi, I'm **SSCBot**"
			else:
				txt1 = f"Hi, I'm **{config.botName}**, formally known as **SSCBot**."
			txt2 = f"""
			Created by **APasz**
			I'm written in Python and my code is freely avaliable on **[GitHub](https://github.com/APasz/SSCBot)**
			My functions include: Reacting to things, Welcoming new users, Giving users the roles, random facts, and conversions they seek, logging, and more.
			You can use **{config.BOT_PREFIX}help** to see a list of commands.
			A select few commands are also avaliable as slash commands.
			"""
			text=nextcord.Embed(
				description=txt1+txt2,
				colour=getCol('neutral_Dark')
			)
			text.set_footer(text=f"Version: {mV}.{sV}")
		else:
			text=nextcord.Embed(
				title="Current version",
				description=f"{mV}.{sV}.{pV}\n{Vn}",
				colour=getCol('neutral_Dark')
			)
		await ctx.send(embed=text)
		log.info(f"Info: {ctx.author.id},{ctx.author.display_name}")
		return

	@commands.command(name='MemberCount', aliases=['GuildCount', 'UserCount'])
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def memberCount(self, ctx: commands.Context):
		"""Gives number of members current guild has"""
		log.debug("guildCountCommand")
		await ctx.send(f"**Member Count**: {ctx.guild.member_count}")
		log.info(f"guildCountCommand: {ctx.author.id},{ctx.author.display_name}")

	@slash_command(name="membercount", guild_ids=config.SlashServers)
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def memberCountSlash(self, interaction: Interaction):
		"""Gives number of members current guild has"""
		log.debug("guildCountSlash")
		if not await blacklistCheck(ctx=interaction, blklstType="gen"): return
		await interaction.response.send_message(interaction.user.guild.member_count)
		log.info(f"guildCountSlash: {interaction.user.id},{interaction.user.display_name}")

	@commands.command(name="emoji", aliases=['emo']) #make better one day
	@commands.cooldown(1, 1, commands.BucketType.user)
	@commands.has_permissions(manage_messages=True)
	async def emoji(self, ctx, messid1, messid2=None, messid3=None):
		"""When given up to 3 message IDs, will add first 10 reactions, if no emoji passed, will add star.
		Locked to those who have 'Manage Messages' permssions"""
		log.debug("emojiCommand")
		mess1 = await ctx.fetch_message(messid1)
		mess2 = None
		mess3 = None
		if messid2:
			if messid2.isdigit(): mess2 = await ctx.fetch_message(messid2)
		else:
			messid2 = None
		if messid3:
			if messid3.isdigit(): mess3 = await ctx.fetch_message(messid3)
		else:
			messid3 = None
			mess3 = None
		cont = ctx.message.content
		cont = cont.split(' ')
		print(cont)
		cont = cont.removeprefix("~e")
		cont = cont.removeprefix("moji")
		cont.remove(messid1)
		if messid2 != None:
			if messid2.isdigit(): cont.remove(messid2)
		if messid3 != None:
			if messid3.isdigit(): cont.remove(messid3)
		print(cont)
		cont = cont[:10]
		if cont: pass
		else:
			cont = config.emoStar
		messids = [messid1, messid2, messid3]
		print(messids)
		for emoji in cont:
			await mess1.add_reaction(emoji)
			if mess2 != None: await mess2.add_reaction(emoji)
			if mess3 != None: await mess3.add_reaction(emoji)
		await ctx.message.delete()
		log.info(f"emojiCommand: {messids}: {cont}: {ctx.author.id},{ctx.author.display_name}")

	@slash_command(guild_ids=config.SlashServers) #make better one day
	async def convert(self, interaction: Interaction,
	value:int = SlashOption(name="value", description="What is it we are converting?", required=True),
	fromunit:str = SlashOption(name="original", description="What unit are we converting from?", required=True),
	tounit:str = SlashOption(name="new", description="What unit are we converting to?", required=True)):
		"""Converts between units using pint."""
		if not await blacklistCheck(ctx=interaction, blklstType="gen"): return
		log.debug(f"convert: {value} {fromunit} {tounit} | {interaction.user.id},{interaction.user.display_name}")
		if "/s" in fromunit:
			fromunit = fromunit.replace("/s", "/seconds")
		if "/s" in tounit:
			tounit = tounit.replace("/s", "/seconds")
		if "/h" in fromunit:
			fromunit = fromunit.replace("/h", "/hour")
		if "/h" in tounit:
			tounit = tounit.replace("/h", "/hour")
		u = pint.UnitRegistry()
		Q = u.Quantity
		val = Q(value, fromunit)
		txt = round(val.to(tounit), 3)
		await interaction.response.send_message(f"{val} is {txt}")
		log.info(f"convertSlash")

	@slash_command(name = "changelog", guild_ids = config.SlashServers)
	async def changelog(self, interaction: Interaction,
	ver = SlashOption(
		name = "version",
		description = "If looking for specific version; x.x.x or list",
		required = False)):
		"""Provides the changelog"""
		BL = await blacklistCheck(ctx=interaction, blklstType="gen")
		print("BL:", BL)
		if BL is False: return
		log.debug(f"changelog: {ver} | {interaction.user.id},{interaction.user.display_name}")
		data = readJSON(filename="changelog")
		keys = data.keys()
		if ver is not None:
			if 'list' not in ver:
				ver2 = ver.split('.')
				print(len(ver2))
				if len(ver2) == 2:
					ver = ver + '.0'
				elif len(ver2) == 1:
					ver = ver + '.0.0'
			else:
				ver = "List"
		print(ver)
		if ver is None: ver = list(data)[-1] #default to last ver in changelog
		if "list" in ver.casefold():
			txt = ' | '.join(list(keys))
		elif ver not in keys:
			txt = "Version not in changelog."
		else:
			verName = str(data[f'{ver}'][0])
			txtList = data[f'{ver}'][1:]
			txt = '\n'.join(txtList)
			ver = ver + ' | ' + verName

		await interaction.response.send_message(f"Version {ver}```\n{txt}\n```")

	@slash_command(name = "profile", guild_ids = config.SlashServers)
	async def profile(self, interaction: Interaction,
	usr:nextcord.Member = SlashOption(
		name = "member",
		description = "If looking for member",
		required = False)):
		"""Provides an embed with information about a user."""
		if not await blacklistCheck(ctx=interaction, blklstType="gen"): return
		log.debug(f"profile: {usr} | {interaction.user.id},{interaction.user.display_name}")
		if usr is None:
			usr = interaction.user
		fetched = await self.bot.fetch_user(usr.id) #cause Discord is stupid.
		if fetched.accent_colour is not None: usrCol = fetched.accent_colour #18191c
		else: usrCol = usr.colour
		e = nextcord.Embed(
			description = f"Mention: <@{usr.id}>\nAccount: {usr.name}{usr.discriminator}\nID: {usr.id}",
			colour = usrCol)
		if fetched.banner is not None:
			e.set_image(url = fetched.banner.url)
		e.set_author(name = usr.display_name, icon_url = usr.display_avatar.url)
		created = int(round(usr.created_at.timestamp()))
		e.add_field(name = "Registered;", value = f"<t:{created}:R>", inline=True)
		roles = []
		permsList2 = []
		if "member" in str(type(usr)):
			joined = int(round(usr.joined_at.timestamp()))
			e.add_field(name = "Last Joined;", value = f"<t:{joined}:R>", inline=True)
			if usr.premium_since is not None:
				premium = int(round(usr.premium_since.timestamp()))
				e.add_field(name = "Booster Since;", value = f"<t:{premium}:R>", inline=True)
			roleList = usr.roles
			roleList.pop(0)
			roleList.reverse()			
			for r in roleList:
				r = f"<@&{r.id}>"
				roles.append(r)
			roles = ''.join(roles)
			roleNum = len(roleList)
			e.add_field(name = f"Roles: {roleNum}", value = roles, inline=False)
			permsList = []
			notePerms = ["manage", "moderate", "kick", "ban", "mute", "move", "deafen", "everyone", "audit"]
			for perm in usr.guild_permissions: #put all permissions into a list only if the user has it.
				alpha, bravo = perm
				if bravo is True:
					permsList.append(alpha.lower())			
			for element in permsList: #If admin skip the rest.
				element = element.lower()
				if "admin" in element:
					print("admin")
					permsList2 = ["Administrator"]
					break
				else: #check if any of the noteable perms partially match each element of the permissions list.
					for note in notePerms:
						if note in element:
							print("else")
							element = element.replace('_', ' ')
							permsList2.append(element.title())
							#there must be a better way to do this?
		flags = usr.public_flags.all()
		flagsList = []
		for f in flags:
			f = f.name
			f = f.replace('_', ' ')
			flagsList.append(f.title())
		attris = flagsList + permsList2
		attris = ', '.join(attris)
		if len(attris) > 0: e.add_field(name = "Attributes", value = attris)
		if usr.bot is True: e.set_footer(text = "Is Bot")
		await interaction.send(embed = e)

def setup(bot: commands.Bot):
	bot.add_cog(general(bot))

#MIT APasz
