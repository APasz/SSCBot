print ("CogVK")
import logging

from nextcord.ext import commands

log = logging.getLogger("discordGeneral")

import config
from util.fileUtil import readJSON

configuration = readJSON(filename = "config")
configVK = configuration['VKGuild']

class vk(commands.Cog, name="VK|RU"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		log.debug("Ready")

	@commands.Cog.listener()
	async def on_message(self, ctx):
		"""Check for emoji and add them as reaction"""
		if ctx.channel.id == configVK['Channels']['infoBattles']:
			log.debug("vkListener")
			if config.emoCheck in ctx.content:
				await ctx.add_reaction(config.emoCheck)
				log.info("Checkmark")
			if config.emoTmbUp in ctx.content:
				await ctx.add_reaction(config.emoTmbUp)
				log.info("ThumbsUp")			

def setup(bot: commands.Bot):
	bot.add_cog(vk(bot))

#MIT APasz
