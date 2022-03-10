print ("CogSSCTime")
import logging

from nextcord.ext import commands

log = logging.getLogger("discordGeneral")
import datetime
import random

from util.fileUtil import readJSON, writeJSON


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
		data = readJSON(f"data")
		currData = int(data['currStamp'])
		nextData = int(data['nextStamp'])
		rminData = int(data['remindStamp'])
		if currStamp == currData: pass
		else:
			data['currStamp'] = currStamp
			log.debug("Cwrite")
		if nextStamp == nextData: pass
		else:
			data['nextStamp'] = nextStamp
			log.debug("Nwrite")
		if stamp36 <= rminData <= stamp24: pass
		else:
			data['remindStamp'] = remindStamp
			log.debug("Rwrite")
		check = writeJSON(data, "data")
		return check

def setup(bot: commands.Bot):
	bot.add_cog(ssctime(bot))

#MIT APasz