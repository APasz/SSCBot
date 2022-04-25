#!/usr/bin/env python3
import os
import sys
from nextcord import ext

PID = os.getpid()
print (f"\n***Starting*** PID'{PID}'")
critFiles = ["config.json", "config.py"]
configErr = False
for element in critFiles:
	if not os.path.exists(element):
		print(f"{element} missing")
		configErr = True

from util.fileUtil import configUpdate, newFile, readFile, readJSON, writeJSON

configuration = readJSON(filename = "config")
configGen = configuration['General']

import logging

log = logging.getLogger('discordGeneral')
logMess = logging.getLogger('discordMessages')
if configGen['logLevel'] == "DEBUG":
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

if configErr:
	log.critical(f"config missing")
	sys.exit

import asyncio
import time

import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound

import config
from util.genUtil import blacklistCheck


def main():
	intents = nextcord.Intents.default()
	intents.members = True
	intents.messages = True

	
	activity = nextcord.Activity(
		type=nextcord.ActivityType.listening, name=f"{config.BOT_PREFIX}help")

	bot = commands.Bot(
		commands.when_mentioned_or(config.BOT_PREFIX),
		intents=intents,
		activity=activity,
		case_insensitive=True)
	curDir = os.path.dirname(os.path.realpath(__file__))
	cogsDir = os.path.join(curDir, "cogs")
	for filename in os.listdir(cogsDir):
		if filename.endswith(".py") and filename != "__init__.py":
			bot.load_extension(f'cogs.{filename[:-3]}')


	@bot.event
	async def on_ready( ):
		log.critical("\n***Started*** 'Hello World, or whatever'")
		print("***Started*** 'Hello World or whatever'")
		if configGen['readyMessage'] is True:			
			data = readJSON(filename="changelog")
			ver = list(data.keys())[-1]
			verMajor, VerMinor, verPoint = ver.split('.')			
			verName = list(data[f'{ver}'])[0]
			txt = f"**v{verMajor}.{VerMinor}.{verPoint} | {verName}**\n**Ready**\nUse /changelog to see changes"
			config = readJSON(filename="config")
			config['General']['verMajor'] = verMajor
			config['General']['VerMinor'] = VerMinor
			config['General']['verPoint'] = verPoint
			config['General']['verName'] = verName
			writeJSON(data=config, filename="config")
			sendReady = {
				configuration['TPFGuild']['Channels']['Botstuff']:configuration['TPFGuild']['readyMessage'],
				configuration['NIXGuild']['Channels']['Botstuff']:configuration['NIXGuild']['readyMessage']
			}
			for element in sendReady:
				if sendReady[element]:
					chan = await bot.fetch_channel(element)
					await chan.send(txt)
			messFile = os.path.join(curDir, "messID.txt")
			if os.path.exists(messFile):
				messIDs = readFile(directory=curDir, filename="messID")
				os.remove(os.path.join(curDir, "messID.txt"))
				print(messIDs)
				if len(messIDs) <= 2: return
				log.debug(messIDs)
				messID, chanID = messIDs.split('|')
				chan = await bot.fetch_channel(int(chanID))
				mess = await chan.fetch_message(int(messID))
				await mess.edit(content="Reboot Successful!")


	@bot.check
	async def blacklistedUser(ctx):		
		if (ctx.command is not None):
			log.debug("blacklistedUserCheck")
			if await blacklistCheck(ctx=ctx, blklstType="gen") is True: return True
			else:
				raise ext.commands.MissingPermissions([''])

	@bot.event
	async def on_command_error(ctx, error):
		auth = f"{ctx.author.id}, {ctx.author.display_name}"
		if isinstance(error, (commands.MissingPermissions)):
			await ctx.message.delete()
			await ctx.send("You don't have the correct permissions.",
			delete_after=configuration['General']['delTime'])
			log.error(f"MissingPermission. {auth}")
			print("error:MissingPermission")
		if isinstance(error, (commands.MissingRole)):
			await ctx.message.delete()
			await ctx.send("You don't have the correct role.",
			delete_after=configuration['General']['delTime'])
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
		if isinstance(error, asyncio.TimeoutError):
			await ctx.send(f"asyncio 408. Response not received in time.")
			log.error(f"asyncio 408 {auth}")
			print("error:asyncio 408")

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
			await ctx.send("Command not found") #this should probably check the list of commands...

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
			for filename in os.listdir(cogsDir):
				if filename.endswith(".py") and filename != "__init__.py":
					bot.reload_extension(f'cogs.{filename[:-3]}')
			log.info("All cogs reloaded")
		except:
			await ctx.send("Cogs can't be reloaded.")
			log.info("Cogs can't be reloaded")
			print("Cogs can't be reloaded")
		else:
			await ctx.send("All cogs successfully reloaded.")

	@bot.command(name="memory", hidden=True)
	@commands.is_owner()
	async def memory(ctx):
		"""Fetches the current amount of memory used by the bot process"""
		import platform
		import resource
		memKB = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
		memMB = int(memKB) / 10**3
		totalMemoryMB, usedMemoryMB, freeMemoryMB = map(
			int, os.popen('free -t -m').readlines()[-1].split()[1:])
		percent = round((usedMemoryMB/totalMemoryMB) * 100, 2)
		if usedMemoryMB > 4096:
			usedMemory = f"{int(usedMemoryMB) / 10**3}GB"
		else: usedMemory = f"{usedMemoryMB}MB"
		await ctx.send(f"{platform.node()}\nProcess: {memMB}MB\nSystem: {usedMemory} {percent}%")

	async def botRestartCheck(ctx, curDir:str):
		mess = await ctx.send("Commencing restart squence...")
		def check(m):
			if (m.author == ctx.author and m.channel == ctx.channel): return True
		try:
			reply = await bot.wait_for('message', check=check, timeout=10.0)
		except asyncio.TimeoutError as e:
			await mess.edit(content="Timeout. Restart Aborted")
			print("timeout", e)
			return False
		except Exception as xcp:
			await mess.edit(content=f"xcp: {xcp}")
		await reply.delete()
		await mess.edit(content="Confirmed. Restartig momentarily")
		IDs = f"{mess.id}|{mess.channel.id}"
		file = os.path.join(curDir, "messID.txt")
		if os.path.exists(file):
			print("File found")
			os.remove(file)
		if not newFile(IDs, directory=curDir, filename="messID"):
			ctx.send("Restart Halted: Error noting message ID\nContinue anyway?")
			if not await bot.wait_for('message', check=check, timeout=5.0):
				return False
		return True

	@bot.command(name="configUpdateCOMM", hidden=True)
	@commands.is_owner()
	async def configUpdateCOMM(ctx):
		"""Merge new config.json into existing one."""
		tmpDir = os.path.join(os.sep, "tmp")
		attachCF = ctx.attachments[0]
		if configUpdate(tmpDir, curDir, attachCF):
			await ctx.send("Config merged!")
		else:
			await ctx.send("Error during config merge.")


	def systemRestart(system:bool):
		log.critical(f"Rebooting | System: {system}")
		print(f"Rebooting | System: {system}")
		if system is True:
			sys.exit(194)
		else:
			sys.exit(0)

	@bot.command(name="botRestart", hidden=True)
	@commands.is_owner()
	async def botRestart(ctx, system=True):
		"""Exits the Discord Bot script. By default server automatically restarts"""
		if await botRestartCheck(ctx, curDir) is False: return
		systemRestart(system)

	bot.run(config.DISTOKEN)

if __name__ == "__main__":
	main()

#MIT APasz
