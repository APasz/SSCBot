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
		log.debug(interaction.user.id)
		BL = await blacklistCheck(ctx=interaction, blklstType="gen")
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
		log.debug(ctx.author.id)
		configGen = readJSON(filename = "config")['General']
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
		log.info(f"{ctx.author.id},{ctx.author.display_name}")
		await ctx.send(f"**Member Count**: {ctx.guild.member_count}")		

	@slash_command(name="membercount", guild_ids=config.SlashServers)
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def memberCountSlash(self, interaction: Interaction):
		"""Gives number of members current guild has"""
		log.info(f"{interaction.user.id},{interaction.user.display_name}")
		if not await blacklistCheck(ctx=interaction, blklstType="gen"): return
		await interaction.send(interaction.user.guild.member_count)		

	@commands.command(name="react", aliases=['emoji'])
	@commands.cooldown(1, 1, commands.BucketType.user)
	@commands.has_permissions(manage_messages=True)
	async def react(self, ctx):
		print(ctx.message.content)
		rawItems = ctx.message.content.split(' ')[1:]
		messIDs = []
		emojiSet = set()
		for item in rawItems:
			if item[0].isdigit():
				messIDs.append(int(item))
			elif item[0].startswith('<'):
				emojiSet.add(item)
			else:
				emojiSet.add(item)
		messOBJs = []
		print(messIDs)
		print(emojiSet)
		for item in messIDs:
			messOBJs.append(await ctx.fetch_message(item))
		if len(emojiSet) == 0: emojiSet = ['⭐']
		badEmoji = set()
		for item in messOBJs:
			for element in emojiSet:
				try: 
					await item.add_reaction(element)
				except Exception as xcp:
					print(xcp)
					if "Unknown Emoji" in str(xcp): badEmoji.add(element)
		if len(badEmoji) != 0:
			await ctx.send(f"Some emoji aren't accessible: {', '.join(badEmoji)}")
		log.info(f"{messIDs}, {emojiSet}")
		await ctx.message.delete()

	@slash_command(name= "convert", guild_ids=config.SlashServers)
	async def convert(self, interaction: Interaction,
	value:float = SlashOption(name="value",
		description="What is it we are converting?",
		required=True),
	fromMetric:str = SlashOption(name="original-metric",
		description="What Metric unit are we converting from?",
		required=False,
		choices = {
					'Micrometre':'micrometre',
					'Millimetre':"millimetre",
					'Centimetre':"centimetre",
					'Metre':"metre",
					'Kilometre':"kilometre",
					'Microgram':'microgram',
					'Miligram':'miligram',
					'Gram':'gram',
					'Kilogram':'kilogram',
					'Tonne':'tonne',
			},),
	fromImperialUS:str = SlashOption(name="original-imperial-us",
		description="What Imperial/US unit are we converting from?",
		required=False,
		choices = {
					'Inch':"inch",
					'Feet':"feet",
					'Yard':'yard',
					'Mile':"mile",
					'Teaspoon':'teaspoon',
					'Tablespoon':'tablespoon',
					'Fluid ounce':'fluid ounce',
					'Cup':'cup',
					'Pint':'pint',
					'Quart':'quart',
					'Gallon':'gallon',
					'Ounce':'ounce',
					'Pound':'pound',
					'Ton':'ton',
			},),
	fromTime:str = SlashOption(name="original-time",
		description="If a original-unit is also given, original-unit/original-time",
		required=False,
		choices = {
					'Seconds':"seconds",
					'Minute':"minute",
					'Hour':"hour",
					'Day':"day",
					'Week':'week',
					'Year':'year'
			},),
	toMetric:str = SlashOption(name="new-metric",
		description="What unit are we converting to?",
		required=False,
		choices = {
					'Micrometre':'micrometre',
					'Millimetre':"millimetre",
					'Centimetre':"centimetre",
					'Metre':"metre",
					'Kilometre':"kilometre",
					'Microgram':'microgram',
					'Miligram':'miligram',
					'Gram':'gram',
					'Kilogram':'kilogram',
					'Tonne':'tonne',
			},),
	toImperialUS:str = SlashOption(name="new-imperial-us",
		description="What unit are we converting to?",
		required=False,
		choices = {
					'Inch':"inch",
					'Feet':"feet",
					'Yard':'yard',
					'Mile':"mile",
					'Teaspoon':'teaspoon',
					'Tablespoon':'tablespoon',
					'Fluid ounce':'fluid ounce',
					'Cup':'cup',
					'Pint':'pint',
					'Quart':'quart',
					'Gallon':'gallon',
					'Ounce':'ounce',
					'Pound':'pound',
					'Ton':'ton',
			},),
	toTime:str = SlashOption(name="new-time",
		description="If a new-unit is also given, new-unit/original-time",
		required=False,
		choices = {
					'Seconds':"seconds",
					'Minute':"minute",
					'Hour':"hour",
					'Day':"day",
					'Week':'week',
					'Year':'year'
			},)):
		"""Converts between units using pint."""
		if not await blacklistCheck(ctx=interaction): return
		if fromMetric and fromImperialUS:
			await interaction.send(f"Conflicting `originalUnit` arguments. {fromMetric.title()} {fromImperialUS.title()}", ephemeral=True)
			return
		if toMetric and toImperialUS:
			await interaction.send(f"Conflicting `toUnit` arguments. {toMetric.title()} {toImperialUS.title()}", ephemeral=True)
			return
		if (fromTime is not None and toTime is None) or (toTime is not None and fromTime is None):
			await interaction.send("Must have both `original` and `to` time units.", ephemeral=True)
			return
		fromUnit = ''.join(filter(None, [fromMetric, fromImperialUS]))
		toUnit = ''.join(filter(None, [toMetric, toImperialUS]))
		if fromUnit and fromTime is not None:
			fromTime = '/' + fromTime
		if toUnit and toTime is not None:
			toTime = '/' + toTime
		u = pint.UnitRegistry()
		Q = u.Quantity
		try:
			orig = Q(value, (''.join(filter(None, [fromUnit, fromTime]))))
			new = round(orig.to(''.join(filter(None, [toUnit, toTime]))), 5)
		except Exception as xcp:
			if "cannot convert" in str(xcp).casefold():
				await interaction.send(f"Conflicting units: {fromUnit.title()} {toUnit.title()}", ephemeral=True)
			else:
				await interaction.send(xcp)
			return
		ebed = nextcord.Embed(title="Conversion", colour=getCol('neutral_Light'),
		description=f"{str(orig).replace('meter', 'metre')}\n{str(new).replace('meter', 'metre')}")
		await interaction.send(embed=ebed)

	@slash_command(name = "changelog", guild_ids = config.SlashServers)
	async def changelog(self, interaction: Interaction,
	ver = SlashOption(
		name = "version", required = False,
		description = "If looking for specific version; x.x.x or list")):
		"""Provides the changelog"""
		BL = await blacklistCheck(ctx=interaction, blklstType="gen")
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
		if ver is None: ver = list(data)[-1] #default to last ver in changelog
		async def sendMess(version:str, content:str):
			await interaction.response.send_message(f"Version {version}```\n{content}\n```")
		txt = "Undefinded"
		if "list" in ver.casefold():
			txt = ' | '.join(list(keys))
			await sendMess(version=ver, content=txt)
			return
		elif ver not in keys:
			txt = "Version not in changelog."
			await sendMess(version=ver, content=txt)
			return
		else:
			verNameDate = str(data[f'{ver}'][0]).split('::')
			changeList = data[f'{ver}'][1:]	
		version = f"{ver} | {verNameDate[0]}\nDate: {verNameDate[1]}"
		def chunkList(maxChars:int, txtList:list):
			logLength = 0
			entryList = []
			for i, item in enumerate(txtList):
				logLength += len(item)
				if logLength <= maxChars:
					entryList.append(i)
				else:
					yield entryList
					entryList = [i]
					logLength = len(item)
			yield(entryList)
		chunks = list(chunkList(maxChars=1900, txtList=changeList))
		for item in chunks:
			eles = [changeList[i] for i in item]
			txt = '\n'.join(eles)
			toSend = "Undefined"
			if interaction.response.is_done():
				log.debug("Followup")
				toSend = f"... continued ... \n```\n{txt}\n```"
			else:
				log.debug("Response")
				toSend = f"Version {version}      Items: {len(changeList)} ```\n{txt}\n```"
			await interaction.send(content=toSend)	

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
					log.debug("admin")
					permsList2 = ["Administrator"]
					break
				else: #check if any of the noteable perms partially match each element of the permissions list.
					for note in notePerms:
						if note in element:
							log.debug("else")
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
