print ("CogSSCTime")
import logging

from nextcord.ext import commands

log = logging.getLogger("discordGeneral")
import datetime
import random

from util.fileUtil import readJSON, writeJSON

configuration = readJSON(filename = "config")
configSSC = configuration['General']['SSC_Data']

class ssctime(commands.Cog, name="SSCTime"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command(name="timestampset", hidden=True)
	async def timestampset(self):
		await self.bot.wait_until_ready()
		log.debug("timeStampset")
		utc = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
		monUTC = utc - datetime.timedelta(days=utc.weekday())
		currStamp = int((monUTC-datetime.datetime(1970,1,1)).total_seconds())
		nextStamp = int(currStamp) + 604800
		stamp36 = int(currStamp) + 475200
		stamp24 = int(currStamp) + 518400
		remindStamp = int(random.randint(stamp36,stamp24))
		currData = int(configSSC['currStamp'])
		nextData = int(configSSC['nextStamp'])
		rminData = int(configSSC['remindStamp'])
		if currStamp == currData: pass
		else:
			configSSC['currStamp'] = currStamp
			log.debug("Cwrite")
		if nextStamp == nextData: pass
		else:
			configSSC['nextStamp'] = nextStamp
			log.debug("Nwrite")
		if stamp36 <= rminData <= stamp24: pass
		else:
			configSSC['remindStamp'] = remindStamp
			log.debug("Rwrite")
		if writeJSON(data=configuration, filename="config"): return True
		else: return False

	@commands.command(name="timestamp", hidden=True)
	async def timestamp(self, ctx, action="get"):
		if action == "get":
			log.debug("timeStampget")
			curr = int(configSSC['currStamp'])
			next = int(configSSC['nextStamp'])
			rmin = int(configSSC['remindStamp'])
			await ctx.send(
				f"Current week's stamp {curr} | <t:{curr}:R>\n"
				f"Next week's stamp {next} | <t:{next}:R>\n"
				f"Reminder stamp {rmin} | <t:{rmin}:R>"
			)
		elif action == "set":
			if self.timestampset():
				await ctx.send("Stamps updated.")
			else: await ctx.send("Error during stamp update.")

def setup(bot: commands.Bot):
	bot.add_cog(ssctime(bot))

#MIT APasz
