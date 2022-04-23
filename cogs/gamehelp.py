print ("CogGameHelp")
import logging

from nextcord.ext import commands

log = logging.getLogger("discordGeneral")

import config


class gameHelp(commands.Cog, name="GameHelp"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		log.debug("Ready")

	@commands.command(name="wiki", aliases=['w', 'wik', 'gameinfo'])
	@commands.cooldown(1, 1, commands.BucketType.user) 
	async def wiki(self, ctx, game="2"):
		"""Provides links to Wikis *WIP*"""
		if "2" in game:
			await ctx.send(f"Here's the Wiki for Transport Fever 2.\n{config.Wiki2}")
		elif "1" in game:
			await ctx.send(f"Here's the Wiki for Transport Fever 1.\n{config.Wiki1}")
		elif "tf" in game:
			await ctx.send(f"Here's the Wiki for Train Fever.\n{config.Wiki0}")
		else:
			await ctx.send(f"Unable to figure out which Wiki you want. Defaulting to TpF2\n{config.Wiki2}")

	@commands.command(name="modding", aliases=['m', 'mod'])
	@commands.cooldown(1, 1, commands.BucketType.user) 
	async def modding(self, ctx, type=None):
		"""Provides link TpF mod wiki *WIP*"""
		if type == None:
			await ctx.send(config.Wiki2modInstall)

	@commands.command(name="log", aliases=['c', 'crash', 'stdout', 'gamefiles'])
	@commands.cooldown(1, 1, commands.BucketType.user) 
	async def log(self, ctx, type="gameFiles", game="2"):
		"""Provides link TpF wiki*WIP*"""
		if "2" in game and "gameFiles" in type:
			if "stdout" in ctx.message.content:
				await ctx.send(config.Wiki2gameFiles+"#game_log_files")
			else:
				await ctx.send(config.Wiki2gameFiles+"#folder_locations")

def setup(bot: commands.Bot):
	bot.add_cog(gameHelp(bot))

#MIT APasz
