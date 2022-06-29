print("CogAdmin")
import asyncio
import logging
import os
from sre_parse import State

import nextcord
from discord import Permissions, SlashApplicationSubcommand
from nextcord import Embed, Interaction, SlashOption, slash_command
from nextcord.ext import application_checks, commands
from nextcord.ext.commands.bot import Bot
from nextcord.ext.commands.cooldowns import BucketType

log = logging.getLogger("discordGeneral")

import config
from config import userDiction as usrDic
from cogs.generalEvent import setupEventList
from util.fileUtil import configUpdate, parentDir, readJSON, uploadfile, writeJSON
from util.genUtil import blacklistCheck, getCol, getGuilds, getGlobalEventConfig
from util.views import nixroles, nixrolesCOL, tpfroles

from cogs.auditLog import auditLogger


def auditChanGet(guildID):
    log.debug("auditGet")
    audit = config.auditChan
    if str(guildID) in audit.keys():
        return audit[f"{guildID}"]
    else:
        return config.ownerAuditChan


class admin(commands.Cog, name="Admin"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def purge(self, ctx, limit: int):
        if not await blacklistCheck(ctx=ctx):
            return
        if hasattr(ctx, "author"):
            usr = ctx.author
            limit2 = limit + 1
        else:
            usr = ctx.user
            limit2 = limit
        log.info(f"{limit}: {usr.id},{usr.display_name}")
        max = readJSON(filename="config")["General"]["purgeLimit"]
        if limit <= max:
            await asyncio.sleep(0.5)
            audit = auditChanGet(guildID=ctx.guild.id)
            usrDic = {"type": "P_C", "auth": usr, "exta": limit, "chanAudit": audit}
            await auditLogger.logEmbed(self, usrDic)
            await ctx.channel.purge(limit=limit2)
            return True
        return False

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(tpfroles())
        self.bot.add_view(nixroles())
        self.bot.add_view(nixrolesCOL())
        log.debug("Ready")

    @commands.command(name="purge")
    @commands.cooldown(2, 7.5, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def purgeComm(self, ctx, limit: int):
        """Purges a number of messages. Manage Messages Only."""
        if not await self.purge(ctx=ctx, limit=limit):
            await ctx.message.delete()
            delTime = readJSON(filename="config")["General"]["delTime"]
            await ctx.send(
                f"{limit} is more than {max}.\n{delTime}sec *self-destruct*",
                delete_after=delTime,
            )

    @slash_command(
        name="purge",
        guild_ids=config.SlashServers,
        default_member_permissions=Permissions(manage_messages=True),
    )
    async def purgeSlash(
        self,
        interaction: Interaction,
        limit: int = SlashOption(
            name="limit",
            description="How many messages to delete",
            required=True,
            max_value=readJSON(filename="config")["General"]["purgeLimit"],
        ),
    ):
        """Purges a number of messages. Manage Messages Only."""
        if await self.purge(ctx=interaction, limit=limit):
            await interaction.send(f"Messages purged.", ephemeral=True)
        else:
            await interaction.send(f"{limit} is more than {max}.", ephemeral=True)

    @commands.command(name="blacklist", aliases=["SSCblacklist"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    async def blacklist(self, ctx, usr, reason="No reason given"):
        await self.bot.wait_until_ready()
        """"Blacklist users from certain parts or all of the bot."""
        if not await blacklistCheck(ctx=ctx):
            return
        delTime = readJSON(filename="config")["General"]["delTime"]
        if str(ctx.author.id) in usr:
            await ctx.send("You can't blacklist yourself.", delete_after=delTime)
        if "sscblacklist" in ctx.invoked_with:
            blklstType = "SSCBlacklist"
            cat = "SSC"
        else:
            blklstType = "GeneralBlacklist"
            cat = "General"
        log.info(
            f"{blklstType} command: usr {usr}: reason {reason}\nAuthor: {ctx.author.id},{ctx.author.display_name}"
        )
        data = readJSON(filename=blklstType, directory=["secrets"])
        if "readall" in usr:
            keyList = list()
            joined = None
            for k in data.keys():
                keyList.append(k)
                joined = "\n".join([str(e) for e in keyList])
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
        if ctx.message.mentions:
            usr = str(ctx.message.mentions[0].id)
        else:
            usr = str(usr)
        if int(usr) == config.ownerID:
            await ctx.send("You can't blacklist bot owner.", delete_after=delTime)
        if usr in data:
            reason = data.get(usr)
            await ctx.send(f"User already blacklisted:``` {reason} ```")
        else:
            id = int(usr)
            data[f"{id}"] = reason
            check = writeJSON(data, filename=blklstType, directory=["secrets"])
            if check == 1:
                usr = await self.bot.fetch_user(id)
                audit = auditChanGet(guildID=ctx.guild.id)
                usrDic = {
                    "type": "Bl_A",
                    "auth": ctx.author,
                    "usr": usr,
                    "reason": reason,
                    "cat": cat,
                    "chanAudit": audit,
                }
                await auditLogger.logEmbed(self, usrDic)
                await ctx.send(f"{usr.id} has been added")
            else:
                await ctx.send("Error occured during write", delete_after=delTime)

    @commands.command(name="blacklistRemove", aliases=["SSCblacklistRemove"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    async def blacklistRemove(self, ctx, usr):
        await self.bot.wait_until_ready()
        if not await blacklistCheck(ctx=ctx):
            return
        if "sscblacklistremove" in ctx.invoked_with:
            blklstType = "SSCBlacklist"
            cat = "SSC"
        else:
            blklstType = "GeneralBlacklist"
            cat = "General"
        log.info(
            f"{blklstType} command: usr {usr}. Author: {ctx.author.id},{ctx.author.display_name}"
        )
        data = readJSON(filename=blklstType, directory=["secrets"])
        if usr in data:
            del data[f"{usr}"]
            check = writeJSON(data, filename=blklstType, directory=["secrets"])
            if check == True:
                usr = await self.bot.fetch_user(usr)
                audit = auditChanGet(guildID=ctx.guild.id)
                usrDic = {
                    "type": "Bl_R",
                    "auth": ctx.author,
                    "usr": usr,
                    "cat": cat,
                    "chanAudit": audit,
                }
                await auditLogger.logEmbed(self, usrDic)
                await ctx.send(f"{usr.id}: User removed from blacklist.")
            else:
                delTime = readJSON(filename="config")["General"]["delTime"]
                await ctx.send("Error occured during write", delete_after=delTime)
        else:
            await ctx.send("User not in blacklist.")

    @commands.command(
        name="listFile", aliases=["auditList", "fileList", "listFolder", "folderList"]
    )
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def auditList(self, ctx, foldername=None):
        """For auditing: Lists files and folders in root directory of bot."""
        if not await blacklistCheck(ctx=ctx):
            return
        log.info(f"auditList: {foldername}")
        fileList = set()
        foldList = set()
        if foldername is None:
            folder = "./"
        else:
            folder = f"./{foldername}"
        exts = (".py", ".json", ".txt")
        for filename in os.listdir(f"{folder}"):
            if filename.endswith(exts):
                fileList.add(f"{filename}")
            elif os.path.isdir(filename) and not (
                filename.startswith("__") or filename.startswith(".")
            ):
                foldList.add(f"{filename}")
            else:
                continue
        fileList = "\n".join(fileList)
        foldList = "\n".join(foldList)
        print(len(foldList))
        e = nextcord.Embed(
            title=f"All py/json/txt files in **{folder}**", colour=getCol("neutral_Mid")
        )
        if len(fileList) > 0:
            e.add_field(name="Files", value=f"{fileList}", inline=True)
        if len(foldList) > 0:
            e.add_field(name="Folders", value=f"{foldList}", inline=True)
        await ctx.send(embed=e)

    @commands.command(name="getFile", aliases=["auditGet", "fileGet"])
    @commands.cooldown(1, 30, commands.BucketType.default)
    async def auditGet(self, ctx, filename: str):
        """For auditing: Gets a file and uploads it."""
        if not await blacklistCheck(ctx=ctx):
            return
        log.info(f"auditGet: {filename}")
        fName = f"./{filename}"
        if os.path.exists(fName) and not os.path.isdir(fName):
            if ("secrets" not in filename) or (ctx.author.id == config.ownerID):
                audit = None  # this section will be redone
                audit = auditChanGet(guildID=ctx.guild.id)
                usrDic = {
                    "type": "A_G",
                    "auth": ctx.author,
                    "exta": filename,
                    "chanAudit": audit,
                }
                await auditLogger.logEmbed(self, usrDic)
                file = nextcord.File(fName)
                await ctx.send(file=file)
            else:
                await ctx.send("File contains sensitive infomation.")

        else:
            await ctx.send(
                """File not found. Please include the extension.
If in a folder please include the foldername followed by a slash. eg [ foldername/filename ]"""
            )

    ## Roll into a more modular file management thing.
    # @commands.command(name="getLog", aliases=["logGet"])
    # @commands.has_permissions(administrator=True)
    # async def getLog(self, ctx, log:str="list"):
    # 	"""Gets the bot logs. Administrator Only."""
    # 	log = log.casefold()
    # 	botDir = parentDir()
    # 	botLogFold = os.path.join(botDir, "logs")
    # 	print(botLogFold)
    # 	if not os.path.exists(botLogFold):
    # 		print("not")
    # 		return
    # 	else: print("yes")
    # 	triggerFold = os.path.abspath(os.path.join(botDir, os.pardir))
    # 	logList = {}
    # 	print("getLog")
    # 	for directory in [botLogFold, triggerFold]:
    # 		if os.path.exists(directory): print("yes", directory)
    # 		else: continue
    # 		for filename in os.listdir(directory):
    # 			if os.path.exists(filename): print("yes2", filename)
    # 			else: continue
    # 			if filename.endswith('log'):
    # 				print("yes3", "Log")
    # 				logList[filename] = directory
    # 	files = logList.keys()
    # 	print(files)
    # 	if "list" in log:
    # 		await ctx.send(', '.join(files))
    # 		return
    # 	if len(files) > 0:
    # 		for item in files:
    # 			print(log, item.casefold())
    # 			if log in item.casefold():
    # 				filePath = os.path.join(logList[item], item)
    # 				print(filePath)
    # 				fileDir=nextcord.File("./logs/discordGeneral.log")
    # 				if fileDir is not None:
    # 					print(fileDir, type(fileDir))
    # 					await ctx.send(file=fileDir)
    # 				else:
    # 					log.error("File Empty")
    # 				return
    # 	await ctx.send("Can't find the log.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def rolebuttons(self, ctx):
        if not await blacklistCheck(ctx=ctx):
            return
        await ctx.message.delete()
        nix = False
        if ctx.guild.id == readJSON(filename="config")["TPFGuild"]["ID"]:
            e = nextcord.Embed(
                title="Roles",
                description="""Pick which roles you'd like.
Modder intern gives access to special channels full of useful info.""",
                colour=getCol("neutral_Light"),
            )
            view = tpfroles()
        elif ctx.guild.id == readJSON(filename="config")["NIXGuild"]["ID"]:
            nix = True
            e = nextcord.Embed(
                title="Roles",
                description="""Pick which roles you'd like.""",
                colour=getCol("neutral_Light"),
            )
            view = nixroles()
            view2 = nixrolesCOL()
        else:
            ctx.send("This guild does not have any buttons.")
            return
        await ctx.send(embed=e, view=view)
        if nix == True:
            await ctx.send(view=view2)
        await view.wait()

    @slash_command(name="uploadfile", guild_ids=config.SlashServers)
    @application_checks.is_owner()
    async def uploadfileCOMM(
        self,
        interaction: Interaction,
        newfile: nextcord.Attachment = SlashOption(
            name="newfile",
            required=True,
            description="A file, ensure filename is correct.",
        ),
        filepath: str = SlashOption(
            name="filepath",
            required=False,
            description="Path of file, subfolders separated by spaces",
        ),
    ):
        log.info(interaction.user.id)
        if filepath is not None:
            filepath = filepath.split(" ")
        if await uploadfile(directory=filepath, newfile=newfile, bak=True):
            await interaction.send("Done!", ephemeral=True)
        else:
            await interaction.send("Error!", ephemeral=True)

    def userFriendlyGuildList():
        guildList = getGuilds()
        newGuildList = {}
        for itemKey, itemVal in guildList.items():
            newKey = f"{itemVal}: {itemKey}"
            newGuildList[newKey] = itemVal
        newGuildList["Global"] = "General"
        return newGuildList

    @slash_command(
        name="toggleevents",
        default_member_permissions=Permissions(administrator=True),
        guild_ids=config.SlashServers,
    )
    # @application_checks.is_owner()
    async def toggleevents(
        self,
        interaction: Interaction,
        event: str = SlashOption(
            name="event", required=True, description="Which event you want to toggle?"
        ),
        guild: str = SlashOption(
            name="guild",
            required=True,
            description="Which guild do you want to edit? or global?",
            choices=userFriendlyGuildList(),
        ),
        newState: bool = SlashOption(
            name="state",
            required=True,
            description="Whether to allow or disallow the event.",
            default=True,
        ),
    ):
        """Finds and changes specified config value"""
        guildsDic = getGuilds(includeGlobal=True)
        for itemKey, itemVal in guildsDic.items():
            if itemVal == guild:
                guildID = itemKey
        configuraton = readJSON("config")
        oldState = configuraton[guild]["Events"][event]
        configuraton[guild]["Events"][event] = newState
        audit = auditChanGet(guildID=interaction.guild_id)
        auditDic = {
            "type": "ToggleEvent",
            "auth": interaction.user,
            "chanAudit": audit,
            "cat": event,
            "exta": (oldState, newState),
            "guild": guild,
            "guildID": guildID,
        }
        await auditLogger.logEmbed(self, data=auditDic)
        log.warning(f"{event}, {guildID}, {oldState}|{newState}")
        writeJSON(data=configuraton, filename="config")
        if setupEventList():
            await interaction.send(
                f"**Event**: {event} for {guild} ({guildID}) set to **{newState}**"
            )

    @toggleevents.on_autocomplete("event")
    async def eventList(self, interaction: Interaction, event: str):
        globalEvents = list(
            getGlobalEventConfig(configuration=readJSON("config"), listAll=True)
        )
        if not event:
            await interaction.response.send_autocomplete(globalEvents)
            return
        get_near_event = [
            typ for typ in globalEvents if typ.lower.startswith(event.lower())
        ]
        await interaction.response.send_autocomplete(get_near_event)


def setup(bot: commands.Bot):
    bot.add_cog(admin(bot))


# MIT APasz
