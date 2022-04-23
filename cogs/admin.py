print ("CogAdmin")
import asyncio
import logging
import os

import nextcord
from nextcord.ext import commands
from nextcord.ext.commands.bot import Bot
from nextcord.ext.commands.cooldowns import BucketType

log = logging.getLogger("discordGeneral")

import config
from config import userDiction as usrDic
from util.fileUtil import readJSON, writeJSON
from util.genUtil import getCol, blacklistCheck
from util.views import nixroles, nixrolesCOL, tpfroles

from cogs.auditlog import *

configuration = readJSON(filename = "config")
configGen = configuration['General']
configTPF = configuration['TPFGuild']
configNIX = configuration['NIXGuild']
delTime = configGen['delTime']

class admin(commands.Cog, name="Admin"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	def auditChanGet(self, guildID):
		log.debug("auditGet")
		audit = config.auditChan
		if str(guildID) in audit.keys(): return audit[f'{guildID}']
		else: return config.ownerAuditChan

	@commands.Cog.listener()
	async def on_ready(self):
		self.bot.add_view(tpfroles())
		self.bot.add_view(nixroles())
		self.bot.add_view(nixrolesCOL())
		log.debug("Ready")

	@commands.command(name="purge")
	@commands.cooldown(1, 1, commands.BucketType.user)
	@commands.has_permissions(manage_messages=True)
	async def purge(self, ctx, limit: int):
		log.info(f"Purge command:{limit}: {ctx.author.id},{ctx.author.display_name}")
		max = configGen['purgeLimit']
		if limit <= max:
			async with ctx.typing():
				await ctx.message.delete()
				await asyncio.sleep(0.5)
				audit = self.auditChanGet(ctx.guild.id)
				usrDic = {'type': "P_C",
							'auth': ctx.author,
							'exta': limit,
							'chanAudit': audit}
				await auditlog.embed(self, usrDic)
				await ctx.channel.purge(limit=limit)
		else:
			await ctx.message.delete()
			await ctx.send(f"{limit} is more than {max}.\n{delTime}sec *self-destruct*", delete_after=delTime)



	@commands.command(name="blacklist", aliases=["SSCblacklist"])
	@commands.cooldown(1, 1, commands.BucketType.user)
	@commands.has_permissions(ban_members=True)
	async def blacklist(self, ctx, usr, reason="No reason given"):
		await self.bot.wait_until_ready()
		""""Blacklist users from certain parts or all of the bot."""
		
		if str(ctx.author.id) in usr:
			await ctx.send("You can't blacklist yourself.", delete_after=delTime)
		if "sscblacklist" in ctx.invoked_with:
			blklstType = "SSCBlacklist"
			cat = "SSC"
		else:
			blklstType = "GeneralBlacklist"
			cat = "General"
		log.info(f"{blklstType} command: usr {usr}: reason {reason}\nAuthor: {ctx.author.id},{ctx.author.display_name}")
		data = readJSON(filename = blklstType, directory = ["secrets"])
		if "readall" in usr:
			keyList = list()
			joined = None
			for k in data.keys():
				keyList.append(k)
				joined = '\n'.join([str(e) for e in keyList])
			if joined is None:
				await ctx.send("The blacklist is empty")
			else:
				await ctx.send(f"Here are all ID's in the blacklist:\n{joined}")
			return
		elif "read" == usr:
			usr = reason
			reason = data.get(usr)
			await ctx.send(f"User: {usr}\n``` {reason} ```")
			return
		if ctx.message.mentions: usr = str(ctx.message.mentions[0].id)
		else: usr = str(usr)
		if int(usr) == config.ownerID:
			await ctx.send("You can't blacklist bot owner.", delete_after=delTime)		
		if usr in data:
			reason = data.get(usr)
			await ctx.send(f"User already blacklisted:``` {reason} ```")
		else:
			id = int(usr)
			data[f'{id}'] = reason
			check = writeJSON(data, filename = blklstType, directory = ["secrets"])
			if check == 1:
				usr = await self.bot.fetch_user(id)
				audit = self.auditChanGet(ctx.guild.id)
				usrDic = {'type': "Bl_A",
							'auth': ctx.author,
							'usr': usr,
							'reason': reason,
							'cat': cat,
							'chanAudit': audit}
				await auditlog.embed(self, usrDic)
				await ctx.send(f"{usr.id} has been added")
			else:
				await ctx.send("Error occured during write", delete_after=delTime)

	@commands.command(name="blacklistRemove", aliases=["SSCblacklistRemove"])
	@commands.cooldown(1, 1, commands.BucketType.user)
	@commands.has_permissions(ban_members=True)
	async def blacklistRemove(self, ctx, usr):
		await self.bot.wait_until_ready()
		if "sscblacklistremove" in ctx.invoked_with:
			blklstType = "SSCBlacklist"
			cat = "SSC"
		else:
			blklstType = "GeneralBlacklist"
			cat = "General"
		log.info(f"{blklstType} command: usr {usr}. Author: {ctx.author.id},{ctx.author.display_name}")
		data = readJSON(filename = blklstType, directory = ["secrets"])
		if usr in data:
			del data[f'{usr}']
			check = writeJSON(data, filename = blklstType, directory = ["secrets"])
			if check == True:
				usr = await self.bot.fetch_user(usr)
				audit = self.auditChanGet(ctx.guild.id)
				usrDic = {'type': "Bl_R",
							'auth': ctx.author,
							'usr': usr,
							'cat': cat,
							'chanAudit': audit}
				await auditlog.embed(self, usrDic)
				await ctx.send(f"{usr.id}: User removed from blacklist.")
			else:
				await ctx.send("Error occured during write", delete_after=delTime)
		else: await ctx.send("User not in blacklist.")

	@commands.command(name="listFile", aliases=["auditList", "fileList", "listFolder", "folderList"])
	@commands.cooldown(1, 10, commands.BucketType.default)
	async def auditList(self, ctx, foldername=None):
		"""For auditing: Lists files and folders in root directory of bot."""
		log.info(f"auditList: {foldername}")
		fileList = set()
		foldList = set()
		if foldername is None: folder = './'
		else: folder = f'./{foldername}'
		exts = ('.py', '.json', '.txt')
		for filename in os.listdir(f'{folder}'):
			if filename.endswith(exts):
				fileList.add(f"{filename}")
			elif os.path.isdir(filename) and not (filename.startswith('__') or filename.startswith('.')):
				foldList.add(f"{filename}")
			else: continue
		fileList = '\n'.join(fileList)
		foldList = '\n'.join(foldList)
		# print(f"Foldername: {folder}")
		# print(f"Files: {fileList}")
		# print(f"Folders: {foldList}")
		e = nextcord.Embed(title=f"All py/json/txt files in **{folder}**", colour=getCol('neutral_Mid'))
		e.add_field(name="Files", value=f"{fileList}", inline=True)
		if foldList: e.add_field(name="Folders", value=f"{foldList}", inline=True)
		await ctx.send(embed=e)

	@commands.command(name="getFile", aliases=["auditGet", "fileGet"])
	@commands.cooldown(1, 30, commands.BucketType.default)
	async def auditGet(self, ctx, filename:str):
		"""For auditing: Gets a file and uploads it."""
		log.info(f"auditGet: {filename}")
		fName = f"./{filename}"
		if os.path.exists(fName) and not os.path.isdir(fName):
			if ("secrets" not in filename) or (ctx.author.id == config.ownerID):
				guild = ctx.guild.id
				audit = None #this section will be redone
				audit = await self.auditChanGet(self, guild)
				usrDic = {'type': "A_G",
							'auth': ctx.author,
							'exta': filename,
							'chanAudit': audit}
				await auditlog.embed(self, usrDic)
				file=nextcord.File(fName)
				await ctx.send(file=file)
			else:
				await ctx.send("File contains sensitive infomation.")
					
		else:
			await ctx.send("""File not found. Please include the extension.
If in a folder please include the foldername followed by a slash. eg [ foldername/filename ]""")

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	async def rolebuttons(self, ctx):
		await ctx.message.delete()
		nix = False
		if ctx.guild.id == configTPF['ID']:
			e = nextcord.Embed(title="Roles",
			description="""Pick which roles you'd like.
Modder intern gives access to special channels full of useful info.""",
			colour=getCol('neutral_Light'))
			view = tpfroles()
		elif ctx.guild.id == configNIX['ID']:
			nix = True
			e = nextcord.Embed(title="Roles",
			description="""Pick which roles you'd like.""",
			colour=getCol('neutral_Light'))
			view = nixroles()
			view2 = nixrolesCOL()
		else:
			ctx.send("This guild does not have any buttons.")
			return
		await ctx.send(embed=e, view=view)
		if nix == True: await ctx.send(view=view2)
		await view.wait()

def setup(bot: commands.Bot):
	bot.add_cog(admin(bot))

#MIT APasz
