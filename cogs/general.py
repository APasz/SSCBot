print ("CogGeneral")
import asyncio
import logging
import random
import time

import nextcord
from nextcord import Embed, Interaction, slash_command
from nextcord.ext import commands
from nextcord.ext.commands.cooldowns import BucketType
import pint

log = logging.getLogger("discordGeneral")
import config
from util.fileUtil import blacklistCheck, readJSON, writeJSON

class general(commands.Cog, name="General"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		log.debug("Ready")

	async def fact(self):
		"""Serves Random facts"""
		try:
			facts = open('randomFact.txt').read().splitlines()
			factfull = random.choice(facts)
			factsplit = factfull.split(';')
			log.debug(factsplit)
			f1 = str(factsplit[0])
			f2 = str(factsplit[1][1:])
			f3 = str(factsplit[2][1:])
			e = nextcord.Embed(title=f1,description=f2,colour=config.col_fact)
			if not f3:
				f3 = "Someone forgot the source."
				e.set_footer(text=f3)
				pass
			elif f3 == "NotPublic":
				pass
			else:
				e.set_footer(text=f3)
			log.debug(f"f1:{f1}, f2:{f2}, f3:{f3}")
		except:
			id = f'<@{config.ownerID}>'
			e = (f"I'm so sorry I lost the fact as I was getting it for you.\n'An error occurred' Alert %s" %id)
		return e

	@commands.command(name="fact", aliases=['randomFact'])
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def factCommand (self, ctx):
		log.debug("factCommand")
		async with ctx.typing():
			fact = await self.fact()
			if isinstance(fact, Embed): await ctx.send(embed=fact)
			else: await ctx.send(fact)
			log.info(f"Fact: {ctx.author.id},{ctx.author.display_name}")
	
	@slash_command(name="fact", guild_ids=config.SlashServers)
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def factSlash(self, interaction: Interaction):
		usr = str(interaction.user.id)
		BL = blacklistCheck(usr, "gen")
		if BL is True: pass
		else:
			await interaction.response.send_message(BL, ephemeral=True)
			log.info(f"Fact: Blacklisted User: {interaction.user.id},{interaction.user.display_name}")
			return
		log.debug("factSlash")
		fact = await self.fact()
		if isinstance(fact, Embed): await interaction.response.send_message(embed=fact)
		else: await interaction.response.send_message(fact)
		log.info(f"Fact: {interaction.user.id},{interaction.user.display_name}")


	@commands.command(name="ping")
	@commands.cooldown(1, 2.5, commands.BucketType.user) 
	async def ping(self, ctx: commands.Context, api=None):
		"""Gives ping to server in Melbounre, Australia"""
		log.debug("pingCommand")
		if api == "api":
			async with ctx.typing():
				せ = time.perf_counter()
				mess = await ctx.send('Ponging...')
				え = time.perf_counter()
				await asyncio.sleep(0.25)
				await mess.edit(content=f"Gateway: {round(self.bot.latency * 1000)}ms\nAPI: {round((え - せ) * 1000)}ms")
		else:
			await ctx.send(f"Ponging at {round(self.bot.latency * 1000)}ms")
		log.info(f"Ping: {ctx.author.id},{ctx.author.display_name}")
		return

	@commands.command(name="info")
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def info(self, ctx: commands.Context, ver=None):
		"""Gives information about the bot"""
		log.debug("infoCommand")
		data = readJSON(f"data")
		mV = data['majorVer']
		sV = data['minorVer']
		pV = data['pointVer']
		Vn = data['verName']
		if ver is None:
			if config.botName == "SSCBot":
				txt1 = "Hi, I'm **SSCBot**"
			else:
				txt1 = f"Hi, I'm **{config.botName}**, formally known as **SSCBot**."
			txt2 = f"""
			Created by **APasz**
			I'm written in Python and my code is freely avaliable on **[GitHub](https://github.com/APasz/SSCBot)**
			My functions include: Reacting to things, Welcoming new users, Giving users the roles they seek, Giving out random facts, and more.
			You can use **{config.BOT_PREFIX}help** to see a list of commands.
			"""
			text=nextcord.Embed(
				description=txt1+txt2,
				colour=config.col_neutDark
			)
			text.set_footer(text=f"Version: {mV}.{sV}")
		else:
			text=nextcord.Embed(
				title="Current version",
				description=f"{mV}.{sV}.{pV}\n{Vn}",
				colour=config.col_neutDark
			)
		await ctx.send(embed=text)
		log.info(f"Info: {ctx.author.id},{ctx.author.display_name}")
		return

	@commands.command(name='MemberCount', aliases=['GuildCount', 'UserCount'])
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def version(self, ctx: commands.Context):
		"""Gives number of members current guild has"""
		log.debug("guildCountCommand")
		await ctx.send(f"**Member Count**: {ctx.guild.member_count}")
		log.info(f"guildCount: {ctx.author.id},{ctx.author.display_name}")
		return


	@commands.command(name="emoji", aliases=['emo'])
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
		try: cont.remove("~emoji")
		except: pass
		try: cont.remove("~e")
		except: pass
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

	@slash_command(guild_ids=config.SlashServers)
	async def convert(self, interaction: Interaction, value:int, fromunit:str, tounit:str):
		log.debug(f"convert: {value} {fromunit} {tounit}")
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

def setup(bot: commands.Bot):
	bot.add_cog(general(bot))

#MIT APasz