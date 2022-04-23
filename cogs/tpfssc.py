print ("CogTpFssc")
import asyncio
import logging
import os
import random
import time

import nextcord
import nextcord.ext
from nextcord.ext import commands, tasks
from nextcord.ext.commands.bot import Bot

log = logging.getLogger("discordGeneral")

import config
from util.fileUtil import readJSON, writeJSON
from util.genUtil import getCol, blacklistCheck

from cogs.ssctime import *

configuration = readJSON(filename = "config")
configSSC = configuration['General']['SSC_Data']
configTPF = configuration['TPFGuild']
configGen = configuration['General']
delTime = configGen['delTime']




class tpfssc(commands.Cog, name="TpFSSC"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.remindTask.start()

	@commands.Cog.listener()
	async def on_ready(self):
		if not os.path.exists("missing.png"):
			log.critical("ThemeFile; missing.png is missing")
			print("ThemeFile; missing.png is missing")			
		if not os.path.exists("themes.txt"): 
			log.critical("Themes file is missing")
			print("Themes file is missing")
		if not os.path.exists("randomFact.txt"):
			log.critical("randomFact.txt file is missing")
			print("randomFact.txt file is missing")
		log.debug("Ready")

	@tasks.loop(minutes=configuration['General']['TaskLengths']['SSC_Remind'])
	async def remindTask(self):
		"""Get reminder timestamp from file, check if current time is in within range of remindStamp and nextStamp(-2h), if so invoke SSC minder command"""
		log.debug("remindTask_run")
		print("remindTask: run")
		if configSSC['isPrize'] == True:
			log.debug("remindYes")
			return
		nex = int(configSSC['nextStamp'])
		rem = int(configSSC['remindStamp'])
		n = nex - 7200
		t = int(time.time())
		if rem <= t <= n:
			pri = configSSC['isPrize']
			configSSC['remindSent'] = True
			writeJSON(data=configuration, filename="config")
			if pri == True:
				pt = "everyone"
			elif pri == False:
				pt = "here"
			else: 
				pt = pri
				pass
			log.debug(f"PT: {pt}")
			chan = self.bot.get_channel(configTPF['Channels']['SSC_Remind'])
			await chan.send(f"Reminder that the competiton ends soon;\n**<t:{nex}:R>**\nGet you images and votes in. 🇻 🇴 🇹 🇪 @{pt}")
			await asyncio.sleep(0.1)
			lastID = chan.last_message_id
			mess = await chan.fetch_message(int(lastID))
			emojis=[config.emoNotifi]
			for emoji in emojis:
				await mess.add_reaction(emoji)
			log.info(f"SSC Reminder: {pt}")

	@remindTask.before_loop
	async def before_remindTask(self):
		await self.bot.wait_until_ready()

	@remindTask.after_loop
	async def on_remindTask_cancel(self):
		print("on_remindTask Cancelled")
		log.debug("on_remindTask Cancelled")

	@commands.command(name="comp")
	@commands.has_role(configTPF['Roles']['SSC_Manager'])
	async def comp(self, ctx, alert="no", note="no", prize=None, prizeUser=None):
		"""Start competition. Gets theme from filename of attached image. Changes text based on alert type. Passes note if present."""
		log.debug("compCommand")
		async with ctx.typing():
			note1 = note.casefold()
			check = await ssctime.timestampset(ctx=ctx)
			log.info("timeStampSetCommandInvoked")
			print("invoke")
			if check != 1: ctx.send("timeStampSet Command Error")
			oldTheme = configSSC['theme']
			log.debug(f"oldTheme: {oldTheme}")
			if len(ctx.message.attachments):
				oldTheme = oldTheme.replace(" ","-")
				print("comp: Attach")
				if not os.path.exists("./sscContent"): os.makedirs("./sscContent")
				if os.path.exists(f"./sscContent/{oldTheme}.jpg"):
					os.remove(f"./sscContent/{oldTheme}.jpg")
				else:
					log.error("Theme File Not Found")
					pass
				image_types = ["jpg"]
				for attachment in ctx.message.attachments:
					if any(attachment.filename.lower().endswith(image) for image in image_types):
						filename = f"./sscContent/{attachment.filename}"
						await attachment.save(filename)
				attachment = ctx.message.attachments[0]
				themeFile = attachment.filename[:-4]
				log.debug(f"themeFile: {themeFile}")
				theme = themeFile.replace("-"," ")
				configSSC['theme'] = theme
			else: 
				theme = oldTheme
				themeFile = oldTheme.replace(" ","-")
				print(theme)
				print(themeFile)
			nextstamp = int(configSSC['nextStamp'])
			
			compTxt = []
			if prize:
				configSSC['isPrize'] = True
				if prizeUser:
					compTxt.append(f"{config.txt_CompGift}\n**{prize}** provided by {prizeUser}")
				else:
					compTxt.append(f"{config.txt_CompGift}\n**{prize}**")
				print(f"compTxt: {compTxt}")
			elif alert == "here":
				configSSC['isPrize'] = False
			print(compTxt)
			compTxt.append(f"{config.txt_CompEnd} **<t:{nextstamp}:f>**\n{config.txt_CompTheme} **{theme}**")
			if note1 != "no":
				compTxt.append(f"**Note**: {note}")
			compTxt = '\n'.join(compTxt)
			e = nextcord.Embed(title=config.txt_CompStart,
			description=compTxt,
			colour= getCol('ssc') )
			file=nextcord.File("missing.png")
			e.set_image(url=f"attachment://missing.png")
			if os.path.exists(f"./sscContent/{themeFile}.jpg"):
				file=nextcord.File(f"./sscContent/{themeFile}.jpg")
				e.set_image(url=f"attachment://{themeFile}.jpg")
			e.set_footer(text=config.txt_CompRules)
			await ctx.send(file=file, embed=e)
			await asyncio.sleep(0.1)
			last = ctx.channel.last_message_id
			mess = await ctx.channel.fetch_message(int(last))
			emojis=[config.emoNotifi,config.emoTmbUp,config.emoTmbDown]
			for emoji in emojis:
				await mess.add_reaction(emoji)
			await mess.pin()
			await asyncio.sleep(0.1)
			last = ctx.channel.last_message_id
			mess = await ctx.channel.fetch_message(int(last))
			await mess.delete()
			await asyncio.sleep(0.25)
			if alert != "no": pass
				#await ctx.send(f"@{alert}")
				#if alert == "here":
			try:
				if self.remindTask.is_running:
					log.debug("Try remindTask Running")
					pass
				else:
					self.remindTask.start()
					log.debug("Try remindTask Start")
			except:
				log.debug("remindTask not already running")
				pass
			log.debug("remindTask Triggered")
			configSSC['remindSent'] = False
			if writeJSON(data=configuration, filename="config"): pass
			if check != 0:
				await asyncio.sleep(0.1)
				await ctx.message.delete()
			log.info("Competition Start")
			return

	@commands.command(name="delete")
	@commands.has_permissions(manage_messages=True)
	async def delete(self, ctx: commands.Context, messID, reason, reason1=None):
		"""Deletes message and informs user. Message ID, User ID, Reason(theme/edit/repost), Reason(optional) 'passed'
		Depending on reason arg, informs user why their submission was delete. Theme message includes the theme.
		Please provide a link for repost arg."""
		log.debug("deleteCommand")
		theme = configSSC['theme']
		log.debug(f"t,{theme}")
		log.debug(f"reason,{reason}")
		log.debug(f"reason1,{reason1}")
		res0 = "Your image was deleted "
		res1 = res0+f"as it does not fit this weeks theme of;\n**`{theme}`**{config.txt_CompDMresub}"#config.txt_CompDMr1+(f"\n**`{t}`**")+config.txt_CompDMresub #Does not match theme
		res2 = res0+f"due to it being edited.{config.txt_CompDMtss}"
		res3 = res0+f"because it's been posted before,\n{reason1}"
		if "theme" in reason:
			r = res1
		elif "edit" in reason:
			r = res2
		elif "repost" in reason:
			if reason1:
				r = res3
				pass
			else:
				await ctx.send('"Text in double quotes" or a link must be provided as 3rd argument')
				return
		else:
			if reason:
				r = reason
				pass
			else:
				await ctx.send('"Text in double quotes" must be provided as 2nd argument')
				return
		mess = await ctx.fetch_message(messID)
		usrID = mess.author.id
		usr = await self.bot.fetch_user(usrID)
		log.debug(f"m,{messID}: u,{usrID}: reason,{r}")
		log.debug(f"r1,{reason1}")
		if usr.bot:
			await ctx.send("Author is bot, unable to send DM")
		elif usr:
			await usr.send(r)
			log.info(f"DMsent: {usr}, {reason}: {ctx.author.id},{ctx.author.display_name}")
		else:
			await ctx.send('user not found')
			log.info(f"DM-userNotFound: {usr}, {reason}")
		await asyncio.sleep(1)
		await ctx.channel.delete_messages([nextcord.Object(id=messID)])
		await ctx.message.delete()

	@commands.command(name="themeVote")
	@commands.has_role(configTPF['Roles']['SSC_Manager'])
	async def themeVote(self, ctx: commands.Context):
		"""Pull 3 themes for community to vote on"""
		log.debug("themeVoteCommand")
		ops = open('themes.txt').read().splitlines()
		op0 = random.sample(ops, k=3)
		op1, op2, op3 = op0
		await ctx.send(f"Vote for next week's theme.\n{config.emo1} {op1}\n{config.emo2} {op2}\n{config.emo3} {op3}")
		last = ctx.channel.last_message_id
		message = await ctx.channel.fetch_message(int(last))
		emojis=[config.emo1,config.emo2,config.emo3]
		for emoji in emojis:
			await message.add_reaction(emoji)
		await ctx.message.delete()
		log.info("themeVote")

	@commands.Cog.listener()
	async def on_message(self, ctx):
		"""Check if message has attachment or link, if 1 add reaction, if not 1 delete and inform user, set/check prize round state, ignore SSCmanager, """
		if ctx.content.startswith(f"{config.BOT_PREFIX}"):
			return
		if ctx.channel.id != configTPF['Channels']['SSC_Comp']: return
		log.debug("SSC listener")
		if ctx.author.bot:
			if ctx.author.id == config.botID: return
			else:
				log.info("A bot did something")
				return
		usrID = str(ctx.author.id)
		sscMan = configTPF['Roles']['SSC_Manager']
		if not await blacklistCheck(ctx=ctx, blklstType="ssc"): return
		if ctx.author.get_role(sscMan):
			if 'upload' in ctx.content:
				await ctx.add_reaction(config.emoStar)
				log.info("Manager Submission")
				return
			else:
				log.info("Manager did something")
			return
		cont = str(ctx.content)
		if cont.startswith("http"):
			h = 'y'
		else:
			h = 'n'
		log.debug(cont)
		log.debug(h)
		if len(ctx.attachments) == 0 and h == 'n':
			content=(f"""Either no image or link detected. Please submit an image.
			\n{delTime}sec *self-destruct*""")
			await ctx.reply(content, delete_after=delTime)
			log.info(f"Deletion_noImg: {ctx.author.id},{ctx.author.display_name}")
			await asyncio.sleep(delTime)
			try:
				await ctx.delete()
			except: pass
			return
		if len(ctx.attachments) != 1 and h == 'n':
			content=(f"""Multiple images detected. Please resubmit one image at a time.
			\n{delTime}sec *self-destruct*""")
			await ctx.reply(content, delete_after=delTime)
			log.info(f"Deletion_multiImg: {ctx.author.id},{ctx.author.display_name}")
			await asyncio.sleep(delTime)
			try:
				await ctx.delete()
			except:	pass
			return
		sscWin = configTPF['Roles']['SSC_Winner']
		sscRun = configTPF['Roles']['SSC_Runnerup']
		sscPri = configTPF['Roles']['SSC_WinnerPrize']
		if len(ctx.attachments) == 1 or h == 'y':
			prize = configSSC['isPrize']
			if prize is True:
				if ctx.author.get_role(int(sscPri)):
					content=(f"""You're a SSC Prize Winner, so can't participate in this round.
					\n{delTime}sec *self-destruct*""")
					await ctx.reply(content, delete_after=delTime)
					log.info(f"Deletion_PrizeWinner: {ctx.author.id},{ctx.author.display_name}")
					await asyncio.sleep(delTime)
					try:
						await ctx.delete()
					except:
						pass
					pass
				else:
					await ctx.add_reaction(config.emoStar)
					log.info(f"SubmissionPrize: {ctx.author.id},{ctx.author.display_name}")
					return
			elif prize is False:
				if ctx.author.get_role(int(sscWin)) or ctx.author.get_role(int(sscRun)):
					log.debug("w")
					content=(f"""You're a SSC Winner/Runner Up, so can't participate in this round.
					\n{delTime}sec *self-destruct*""")
					await ctx.reply(content, delete_after=delTime)
					log.info(f"Deletion_WinnerRunnerUp: {ctx.author.id},{ctx.author.display_name}")
					await asyncio.sleep(delTime)
					try:
						await ctx.delete()
					except:
						pass
				else:
					await ctx.add_reaction(config.emoStar)
					log.info(f"Submission: {ctx.author.id},{ctx.author.display_name}")
					return
			else:
				log.warning(f"Star: Mhmm: {ctx.author.id},{ctx.author.display_name}")
		else:
			print("HUH")
			log.debug("HUH")

def setup(bot: commands.Bot):
	bot.add_cog(tpfssc(bot))

#MIT APasz
