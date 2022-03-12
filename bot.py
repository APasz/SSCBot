#!/usr/bin/env python3
import os
PID = os.getpid()
print (f"\n***Starting*** PID'{PID}'")
import config
import logging

log = logging.getLogger('discordGeneral')
logMess = logging.getLogger('discordMessages')
if config.logLevel == "DEBUG":
	log.setLevel(logging.DEBUG)
	logMess.setLevel(logging.DEBUG)
else:
	log.setLevel(logging.INFO)
	logMess.setLevel(logging.INFO)

handler = logging.FileHandler(filename='discordGeneral.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(created)f|%(levelname)s:%(module)s; %(message)s'))
log.addHandler(handler)

messHandler = logging.FileHandler(filename='discordMessages.log', encoding='utf-8', mode='a')
messHandler.setFormatter(logging.Formatter('%(asctime)s:%(created)f|%(module)s; %(message)s'))
logMess.addHandler(messHandler)

log.critical(f"\n***Starting*** PID'{PID}'")

import time
import netifaces
def checkNet(host=None):
	if host is None:
		gw = netifaces.gateways()
		if bool(gw['default']) is False: return False
		gate = (gw['default'][netifaces.AF_INET][0])
	else: gate = host
	res = os.system("ping -c 1 " + gate)
	if res == 0: return True
	else: return False
		

while True:
	net = checkNet()
	if net is False:
		print("No Connection")
		log.critical("No Connection")
		time.sleep(2.5)
		pass
	elif net is True:
		print("Connection Found")
		time.sleep(2.5)
		disNet = checkNet("www.discord.com")
		if disNet is False:
			print("No Discord Connection")
			log.critical("No Discord Connection")
			time.sleep(2.5)
			pass
		elif disNet is True:
			print("Discord Connection Found")
			break


import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound

from util.fileUtil import blacklistCheck, readJSON

def main():
	intents = nextcord.Intents.default()
	intents.members = True
	intents.messages = True

	
	activity = nextcord.Activity(
		type=nextcord.ActivityType.listening, name=f"{config.BOT_PREFIX}help"
	)

	bot = commands.Bot(
		commands.when_mentioned_or(config.BOT_PREFIX),
		intents=intents,
		activity=activity,
		case_insensitive=True
		)

	for filename in os.listdir("./cogs"):
		if filename.endswith(".py") and filename != "__init__.py":
			bot.load_extension(f'cogs.{filename[:-3]}')


	if not os.path.exists("data.json"):
		log.critical("data.xml missing")
		print("data.xml is missing")
		
	

	@bot.event
	async def on_ready( ):
		log.critical("\n***Started*** 'Hello World, or whatever'")
		print("***Started*** 'Hello World or whatever'")
		data = readJSON(f"data")
		mV = data['majorVer']
		sV = data['minorVer']
		pV = data['pointVer']
		Vn = data['verName']
		txt = f"**v{mV}.{sV}.{pV}	{Vn}**\nReady"
		chanTpF = await bot.fetch_channel(config.chan_TpFbot)
		chanNIX = await bot.fetch_channel(config.chan_NIXbot)
		await chanTpF.send(txt)
		await chanNIX.send(txt)

	@bot.check
	async def blacklistedUser(ctx):		
		if (ctx.command is not None):
			if (ctx.author.id == config.ownerID): return True
			if (ctx.guild is not None) and (ctx.author == ctx.guild.owner): return True
			genBL = blacklistCheck(str(ctx.author.id), "gen")
			if genBL is not True: return False
			else: return True

	@bot.event
	async def on_command_error(ctx, error):
		auth = f"{ctx.author.id}, {ctx.author.display_name}"
		if isinstance(error, (commands.MissingPermissions)):
			await ctx.message.delete()
			await ctx.send("You don't have the correct permission.", delete_after=config.delTime)
			log.error(f"MissingPermission. {auth}")
			print("error:MissingPermission")
		if isinstance(error, (commands.MissingRole)):
			await ctx.message.delete()
			await ctx.send("You don't have the correct role.", delete_after=config.delTime)
			log.error(f"MissingRole. {auth}")
			print("error:MissingRole")
		if isinstance(error, (commands.MissingRequiredArgument)): 
			await ctx.send("Missing Argument/s")
			log.error(f"MissingRole. {auth}")
			print("error:MissingArgument/s")
		if isinstance(error, (commands.CommandNotFound)):
			if ctx.message.content.startswith(f"{config.BOT_PREFIX}{config.BOT_PREFIX}"): return
			await ctx.send(f"Command not found.\nPlease check with {config.BOT_PREFIX}help")
			log.error(f"CommandNotFound. {auth}")
			print("error:CommandNotFound")
		if isinstance(error, (commands.DisabledCommand)):
			await ctx.send(f"Command currently **Disabled**")
			log.error(f"CommandDisabled. {auth}")
			print("error:CommandDisabled")
		if isinstance(error, commands.CommandOnCooldown):
			await ctx.send(f"Command cooldown in effect: {round(error.retry_after, 3)}s")
			log.error(f"CommandCooldown. {auth}")
			print("error:CommandCooldown")
		if isinstance(error, commands.ExtensionNotFound):
			await ctx.send(f"Cog not found.")
			log.error(f"ExtensionNotFound. {auth}")
			print("error:ExtensionNotFound")

	@bot.command(name="toggle")
	@commands.has_permissions(administrator=True)
	async def toggle(ctx, comm=None):
		"""Toggles a command. Must be Admin"""
		log.debug("toggleCommand")
		if comm != None:
			command = bot.get_command(comm)
			log.info(f"C: {command.enabled}")
			if command.enabled == True:
				command.enabled = False
				print(command.enabled)
			elif command.enabled == False:
				command.enabled = True
				print(command.enabled)
			log.info(f"C: {command.enabled}")
			await ctx.send("command toggled")
		else:
			await ctx.send("Command not found")

	@bot.command(name="reload", aliases=['rl'], hidden=True)
	@commands.is_owner()
	async def reload(ctx, extension):
		"""Reloads a specific cog"""
		log.debug("reloadCogCommand")
		try:
			bot.reload_extension(f"cogs.{extension}")
		except:
			await ctx.send(f"**{extension}** can't be reloaded.")
			log.info(f"{extension} can't be reloaded")
			print(f"{extension} can't be reloaded")
		else:
			await ctx.send(f"**{extension}** successfully reloaded.")

	@bot.command(name="load", hidden=True)
	@commands.is_owner()
	async def load(ctx, extension):
		"""Loads a specific cog"""
		log.debug("loadCogCommand")
		try:
			bot.load_extension(f"cogs.{extension}")
		except:
			await ctx.send(f"**{extension}** can't be loaded.")
			log.info(f"{extension} can't be loaded")
			print(f"{extension} can't be loaded")
		else:
			await ctx.send(f"**{extension}** successfully loaded.")

	@bot.command(name="unload", hidden=True)
	@commands.is_owner()
	async def unload(ctx, extension):
		"""Unloads a specific cog"""
		log.debug("unloadCogCommand")
		try:
			bot.unload_extension(f"cogs.{extension}")
		except:
			await ctx.send(f"**{extension}** can't be unloaded.")
			log.info(f"{extension} can't be unloaded")
			print(f"{extension} can't be unloaded")
		else:
			await ctx.send(f"**{extension}** successfully unloaded.")

	@bot.command(name="reloadAll", hidden=True)
	@commands.is_owner()
	async def reloadAll(ctx):
		"""Reloads all cogs"""
		log.debug("reloadAllCogsCommand")
		try:
			for filename in os.listdir("./cogs"):
				if filename.endswith(".py") and filename != "__init__.py":
					bot.reload_extension(f'cogs.{filename[:-3]}')
			log.info("All cogs reloaded")
		except:
			await ctx.send("Cogs can't be reloaded.")
			log.info("Cogs can't be reloaded")
			print("Cogs can't be reloaded")
		else:
			await ctx.send("All cogs successfully reloaded.")

	bot.run(config.TOKEN)

if __name__ == "__main__":
	main()

#MIT APasz
