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

from config import dataObject as dataObject, genericConfig
from cogs.generalEvent import generalEvent
from util.fileUtil import readJSON, uploadfile, writeJSON
from util.genUtil import (
    blacklistCheck,
    getCol,
    getGuilds,
    getGlobalEventConfig,
    getChan,
    getEventConfig,
)
from util.views import nixroles, nixrolesCOL, tpfroles

from cogs.auditLog import auditLogger


def auditChanGet(guildID):
    log.debug("auditGet")
    audit = genericConfig.auditChan
    if str(guildID) in audit.keys():
        return audit[f"{guildID}"]
    else:
        return genericConfig.ownerAuditChan


class admin(commands.Cog, name="Admin"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guilds = getGuilds()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(tpfroles())
        self.bot.add_view(nixroles())
        self.bot.add_view(nixrolesCOL())
        log.debug("Ready")

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
            dataObject.type = "CommandPurge"
            dataObject.userObject = usr
            dataObject.limit = limit
            dataObject.auditChan = getChan(
                self=self, guild=ctx.guild.id, chan="Audit", admin=True
            )
            await auditLogger.logEmbed(self, dataObject)
            await ctx.channel.purge(limit=limit2)
            return True
        return False

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
        guild_ids=genericConfig.slashServers,
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
        if int(usr) == genericConfig.ownerID:
            await ctx.send("You can't blacklist bot owner.", delete_after=delTime)
        if usr in data:
            reason = data.get(usr)
            await ctx.send(f"User already blacklisted:``` {reason} ```")
        else:
            id = int(usr)
            data[f"{id}"] = reason
            check = writeJSON(data, filename=blklstType, directory=["secrets"])
            if check == True:
                dataObject.type = "BlacklistAdd"
                dataObject.userObject = ctx.author
                dataObject.commandArg1 = await self.bot.fetch_user(id)
                dataObject.reason = reason
                dataObject.category = cat
                dataObject.auditChan = getChan(
                    self=self, guild=ctx.guild.id, chan="Audit", admin=True
                )
                await auditLogger.logEmbed(self, dataObject)
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
                dataObject.type = "BlacklistRemove"
                dataObject.userObject = ctx.author
                dataObject.commandArg1 = await self.bot.fetch_user(id)
                dataObject.category = cat
                dataObject.auditChan = getChan(
                    self=self, guild=ctx.guild.id, chan="Audit", admin=True
                )
                await auditLogger.logEmbed(self, dataObject)
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
            if (
                ("secret" not in filename)
                or ("log" not in filename)
                or (ctx.author.id == genericConfig.ownerID)
            ):
                dataObject.type = "CommandAuditGet"
                dataObject.userObject = ctx.author
                dataObject.filename = filename
                dataObject.auditID = getChan(
                    guild=ctx.guild.id, chan="Audit", admin=True
                )
                await auditLogger.logEmbed(self, dataObject)
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
        guildID = str(ctx.guild.id)
        await ctx.message.delete()
        nix = False
        guilds = getGuilds()
        print(guilds)
        if "TPFGuild" == guilds[guildID]:
            e = nextcord.Embed(
                title="Roles",
                description="""Pick which roles you'd like.
Modder intern gives access to special channels full of useful info.""",
                colour=getCol("neutral_Light"),
            )
            view = tpfroles()
        elif "NIXGuild" == guilds[guildID]:
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

    @slash_command(name="uploadfile", guild_ids=genericConfig.slashServers)
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

    def userFriendlyConfigGroups():
        groups = readJSON(filename="config")
        configList = {}
        for itemKey, itemVal in groups.items():
            if itemKey != itemVal:
                groups.pop(itemKey)
            elif itemKey == itemVal:

                configList[itemKey.replace("_", " ")] = itemKey
        return configList

    @slash_command(
        name="configuration",
        default_member_permissions=Permissions(administrator=True),
        guild_ids=genericConfig.slashServers,
    )
    async def configurationCOMM(
        self,
        interaction: Interaction,
        group: str = SlashOption(
            name="group",
            required=True,
            description="Which group of config do you want to edit?",
        ),
        option: str = SlashOption(
            name="option",
            required=True,
            description="Which option do you want to change?",
        ),
        value: str = SlashOption(
            name="value",
            required=True,
            description="^^^ = Current. What is the new ID/Value you wish to input? int | false",
        ),
    ):
        """Server admins can change bot configuration for their server."""
        guildID = str(interaction.guild_id)
        if value.lower() in ("false", "none"):
            value = None
        elif value.isdigit():
            value = int(value)
        else:
            await interaction.send(f"ValueError")
        configuration = readJSON(filename="config")
        try:
            oldValue = str(configuration[guildID][group][option])
        except KeyError as xcp:
            if group in str(xcp):
                err = group
            elif option in str(xcp):
                err = option
            await interaction.send(f"KeyError: {err}", ephemeral=True)
        configuration[guildID][group][option] = value
        log.info(
            f"ConfigUpdated: {self.guilds[guildID]}, {interaction.user.id}, {group}-{option}:{oldValue} | {value}"
        )
        dataObject.type = "CommandGuildConfiguration"
        dataObject.auditChan = getChan(
            guild=guildID, chan="Audit", admin=True, self=self
        )
        dataObject.categoryGroup = group
        dataObject.category = option
        dataObject.commandArg1 = value
        dataObject.commandArg2 = oldValue
        dataObject.userObject = interaction.user
        await auditLogger.logEmbed(self, auditInfo=dataObject)
        if writeJSON(filename="config", data=configuration):
            await interaction.send(
                f"Config updated: {group}-{option}\n{oldValue} -> {value}"
            )
        else:
            await interaction.send("Config not updated!", ephemeral=True)

    @configurationCOMM.on_autocomplete("group")
    async def configurationGroup(self, interaction: Interaction, group):
        guildID = str(interaction.guild_id)
        groups = readJSON(filename="config")[guildID]
        configList = []
        groupWhiteList = genericConfig.configCommGroupWhitelist
        for itemKey, itemVal in groups.items():
            if "dict" in str(type(itemVal)):
                if str(itemKey) in groupWhiteList:
                    configList.append(itemKey)
        await interaction.response.send_autocomplete(configList)

    @configurationCOMM.on_autocomplete("option")
    async def configurationOption(self, interaction: Interaction, option, group):
        if group is None:
            return
        optionsList = ["undefined"]
        guildID = str(interaction.guild_id)
        configuration = readJSON(filename="config")[guildID][group]
        optionsList = list(configuration.keys())
        finalOptionsList = []
        if not option:
            finalOptionsList = optionsList
        elif option:
            optionArg = option.lower()
            for item in optionsList:
                itemLow = item.lower()
                if optionArg in itemLow:
                    finalOptionsList.append(item)
        if len(finalOptionsList) >= 25:
            finalOptionsList = finalOptionsList[0:25]
            finalOptionsList[0] = "**Options Truncated**"
        await interaction.response.send_autocomplete(finalOptionsList)

    @configurationCOMM.on_autocomplete("value")
    async def configurationValue(self, interaction: Interaction, value, group, option):
        if (group or option) is None:
            return
        print(group, option)
        guildID = str(interaction.guild_id)
        configuration = readJSON(filename="config")[guildID]
        configItem = []
        try:
            item = str(configuration[group][option])
            if item is None:
                item = "Undefined Value"
            configItem.append(item)
        except KeyError:
            configItem.append("Undefined Key")
        if len(configItem) == 0:
            configItem.append("Undefined Error")
        if len(value) >= 1:
            configItem.append(value)
        await interaction.response.send_autocomplete(configItem)


def setup(bot: commands.Bot):
    bot.add_cog(admin(bot))


# MIT APasz
