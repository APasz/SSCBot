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
from util.fileUtil import blacklistCheck, readJSON, writeJSON
from util.views import tpfroles, nixroles, nixrolesCOL

from cogs.auditlog import *


class admin(commands.Cog, name="Admin"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

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
		if limit <= 45:
			async with ctx.typing():
				await ctx.message.delete()
				await asyncio.sleep(0.5)
				await ctx.channel.purge(limit=limit)
		else:
			await ctx.message.delete()
			await ctx.send(f"{limit} is more than 45.\n{config.delTime}sec *self-destruct*", delete_after=config.delTime)



	@commands.command(name="blacklist", aliases=["SSCblacklist"])
	@commands.cooldown(1, 1, commands.BucketType.user)
	@commands.has_permissions(ban_members=True)
	async def blacklist(self, ctx, usr, reason="No reason given"):
		await self.bot.wait_until_ready()
		""""Blacklist users from certain parts or all of the bot."""
		
		if str(ctx.author.id) in usr:
			await ctx.send("You can't blacklist yourself.", delete_after=config.delTime)
		if "sscblacklist" in ctx.invoked_with: blklstType = "SSCBlacklist"
		else: blklstType = "GeneralBlacklist"
		log.info(f"{blklstType} command: usr {usr}: reason {reason}\nAuthor: {ctx.author.id},{ctx.author.display_name}")
		data = readJSON(f"secrets/{blklstType}")
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
			await ctx.send("You can't blacklist bot owner.", delete_after=config.delTime)		
		if usr in data:
			reason = data.get(usr)
			await ctx.send(f"User already blacklisted:``` {reason} ```")
		else:
			id = int(usr)
			data[f'{id}'] = reason
			check = writeJSON(data, f"secrets/{blklstType}")
			if check == 1:
				await ctx.send("Added")
			else:
				await ctx.send("Error occured during write", delete_after=config.delTime)

	@commands.command(name="blacklistRemove", aliases=["SSCblacklistRemove"])
	@commands.cooldown(1, 1, commands.BucketType.user)
	@commands.has_permissions(ban_members=True)
	async def blacklistRemove(self, ctx, usr):
		await self.bot.wait_until_ready()
		if "sscblacklistremove" in ctx.invoked_with: blklstType = "SSCBlacklist"
		else: blklstType = "GeneralBlacklist"
		log.info(f"{blklstType} command: usr {usr}. Author: {ctx.author.id},{ctx.author.display_name}")
		data = readJSON(f"secrets/{blklstType}")
		if usr in data:
			del data[f'{usr}']
			check = writeJSON(data, f"secrets/{blklstType}")
			if check == 1:
				await ctx.send(f"{usr}: User removed from blacklist.")
			else:
				await ctx.send("Error occured during write", delete_after=config.delTime)
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
		for filename in os.listdir(f'{folder}'):
			if filename.endswith('.py'):
				fileList.add(f"{filename}")
			elif filename.endswith('.json'):
				fileList.add(f"{filename}")
			elif filename.endswith('.txt'):
				fileList.add(f"{filename}")
			elif os.path.isdir(filename) and not (filename.startswith('__') or filename.startswith('.')):
				foldList.add(f"{filename}")
			else: continue
		fileList = '\n'.join(fileList)
		foldList = '\n'.join(foldList)
		# print(f"Foldername: {folder}")
		# print(f"Files: {fileList}")
		# print(f"Folders: {foldList}")
		e = nextcord.Embed(title=f"All .py/.json/.txt files in **{folder}**", colour=config.col_neutMid)
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
				if guild == config.TpFguild:
					audit = config.chan_TpFaudit
				elif guild == config.NIXguild:
					audit = config.chan_NIXaudit
				else: audit = 935677246482546748 #personal server. I like knowing stuff.
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
		nix = 0
		if ctx.guild.id == config.TpFguild:
			e = nextcord.Embed(title="Roles",
			description="""Pick which roles you'd like.
Modder intern gives access to special channels full of useful info.""",
			colour=config.col_neutLight)
			view = tpfroles()
		elif ctx.guild.id == config.NIXguild:
			nix = 1
			e = nextcord.Embed(title="Roles",
			description="""Pick which roles you'd like.""",
			colour=config.col_neutLight)
			view = nixroles()
			view2 = nixrolesCOL()
		else:
			ctx.send("This guild does not have any buttons.")
			return
		await ctx.send(embed=e, view=view)
		if nix == 1: await ctx.send(view=view2)
		await view.wait()


def setup(bot: commands.Bot):
	bot.add_cog(admin(bot))

#MIT APasz