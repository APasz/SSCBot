import asyncio
import logging
import os

from cogs.auditLog import auditLogger
from config import generalEventConfig as geConfig
from config import genericConfig as gxConfig
from config import localeConfig as lcConfig
from util.fileUtil import readJSON, writeJSON
from util.genUtil import blacklistCheck, getChan, getChannelID, getCol, sortReactions
import util.views as views

_ = lcConfig.getLC
print("CogAdmin")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY ADMIN IMPORT MODULES")
    import nextcord
    from discord import Permissions
    from nextcord import Interaction, SlashOption, slash_command
    from nextcord.ext import commands
except Exception:
    logSys.exception("ADMIN IMPORT MODULES")


def auditChanGet(guildID) -> int:
    """With the ID of a guild, returns either it's auditlog channel
    or if it has none specified, the owner guild auditlog channel"""
    log.debug("auditGet")
    audit = gxConfig.auditChan
    if str(guildID) in audit.keys():
        return int(audit[f"{guildID}"])
    else:
        return int(gxConfig.ownerAuditChan)


class admin(commands.Cog, name="Admin"):
    """Class containing commands and functions related to administration of guilds (not bot config)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(views.tpfroles())
        self.bot.add_view(views.sscroles())
        self.bot.add_view(views.nixroles())
        self.bot.add_view(views.nixrolesCOL())
        logSys.debug(f"{self.__cog_name__} Ready")

    async def purge(self, ctx: commands.Context, limit: int) -> bool:
        """Purges a number of messages from the channel the command was invoked from"""
        if not await blacklistCheck(ctx=ctx):
            return False
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
            from config import dataObject

            dataObject.TYPE = "CommandPurge"
            dataObject.userObject = usr
            dataObject.limit = limit
            dataObject.auditChan = getChan(
                self=self, guild=ctx.guild.id, chan="Audit", admin=True
            )
            dataObject.channelID = int(getChannelID(ctx))
            await auditLogger.logEmbed(self, dataObject)
            await ctx.channel.purge(limit=limit2)
            del dataObject
            return True
        return False

    @commands.command(name="purge")
    @commands.cooldown(2, 7.5, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def purgeComm(self, ctx: commands.Context, limit: int):
        """Purges a number of messages (has max to advoid user client desync). Manage Messages Only."""
        if not await self.purge(ctx=ctx, limit=limit):
            await ctx.message.delete()
            delTime = readJSON(filename="config")["General"]["delTime"]
            try:
                await ctx.send(
                    f"{limit} is more than {max}.\n{delTime}sec *self-destruct*",
                    delete_after=delTime,
                )
            except Exception:
                log.exception(f"Purge Command {ctx.author.id=}")

    @slash_command(
        name="purge",
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
        try:
            if await self.purge(ctx=interaction, limit=limit):
                await interaction.send(f"Messages purged.", ephemeral=True)
            else:
                await interaction.send(f"{limit} is more than {max}.", ephemeral=True)
        except Exception:
            log.exception(f"Purge /Command {interaction.user.id=}")

    @commands.command(name="blacklist", aliases=["SSCblacklist"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    async def blacklist(
        self, ctx: commands.Context, usr: str, reason: str = "No reason given"
    ):
        await self.bot.wait_until_ready()
        """"Blacklist users from certain parts of the bot."""
        if not await blacklistCheck(ctx=ctx):
            return
        delTime = readJSON(filename="config")["General"]["delTime"]
        if str(ctx.author.id) in usr:
            try:
                await ctx.send("You can't blacklist yourself.", delete_after=delTime)
            except Exception:
                log.exception(f"Blacklist Self {ctx.author.id=}")
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
            try:
                if joined is None:
                    await ctx.send("The blacklist is empty")
                else:
                    await ctx.send(f"Here are all ID's in the blacklist:\n{joined}")
                return
            except Exception:
                log.exception(f"Blacklist Add")
        elif "read" == usr:
            usr = reason
            reason = data.get(usr)
            try:
                await ctx.send(f"User: {usr}\n``` {reason} ```")
            except Exception:
                log.exception(f"Blacklist Read")
            return
        if ctx.message.mentions:
            usr = str(ctx.message.mentions[0].id)
        else:
            usr = str(usr)
        if int(usr) == gxConfig.ownerID:
            try:
                await ctx.send("You can't blacklist bot owner.", delete_after=delTime)
            except Exception:
                log.exception(f"Blacklist Bot Owner")
        if usr in data:
            reason = data.get(usr)
            try:
                await ctx.send(f"User already blacklisted:``` {reason} ```")
            except Exception:
                log.exception(f"Blacklist Already")
        else:
            id = int(usr)
            data[f"{id}"] = reason
            check = writeJSON(data, filename=blklstType, directory=["secrets"])
            if check:
                from config import dataObject

                dataObject.TYPE = "BlacklistAdd"
                dataObject.userObject = ctx.author
                dataObject.commandArg1 = await self.bot.fetch_user(id)
                dataObject.reason = reason
                dataObject.category = cat
                dataObject.auditChan = getChan(
                    self=self, guild=ctx.guild.id, chan="Audit", admin=True
                )
                await auditLogger.logEmbed(self, dataObject)
                try:
                    await ctx.send(f"{usr.id} has been added")
                except Exception:
                    log.exception(f"Blacklisted User")
                del dataObject
            else:
                try:
                    await ctx.send("Error occured during write", delete_after=delTime)
                except Exception:
                    log.exception(f"Write Error")

    @commands.command(name="blacklistRemove", aliases=["SSCblacklistRemove"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    async def blacklistRemove(self, ctx: commands.Context, usr: str):
        """Remove a user from one of the bot's blacklists"""
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
            if check:
                id = int(usr)
                from config import dataObject

                dataObject.TYPE = "BlacklistRemove"
                dataObject.userObject = ctx.author
                dataObject.commandArg1 = await self.bot.fetch_user(id)
                dataObject.category = cat
                dataObject.auditChan = getChan(
                    self=self, guild=ctx.guild.id, chan="Audit", admin=True
                )
                await auditLogger.logEmbed(self, dataObject)
                try:
                    await ctx.send(f"{usr.id}: User removed from blacklist.")
                except Exception:
                    log.exception(f"Blackedlisted Removed")
                del dataObject
            else:
                delTime = readJSON(filename="config")["General"]["delTime"]
                try:
                    await ctx.send("Error occured during write", delete_after=delTime)
                except Exception:
                    log.exception(f"Write Error")
        else:
            try:
                await ctx.send("User not in blacklist.")
            except Exception:
                log.exception(f"Blacklist Not")

    @commands.command(
        name="listFile", aliases=["auditList", "fileList", "listFolder", "folderList"]
    )
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def auditList(self, ctx: commands.Context, foldername=None):
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
        try:
            for filename in os.listdir(f"{folder}"):
                if filename.endswith(exts):
                    fileList.add(f"{filename}")
                elif os.path.isdir(filename) and not (
                    filename.startswith("__") or filename.startswith(".")
                ):
                    foldList.add(f"{filename}")
                else:
                    continue
        except Exception:
            log.exception(f"compile filenames {filename=}")
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
        try:
            await ctx.send(embed=e)
        except Exception:
            log.exception(f"AuditList")

    @commands.command(name="getFile", aliases=["auditGet", "fileGet"])
    @commands.cooldown(1, 30, commands.BucketType.default)
    async def auditGet(self, ctx: commands.Context, filename: str):
        """For auditing: Gets a file and uploads it."""
        if not await blacklistCheck(ctx=ctx):
            return
        log.info(f"auditGet: {filename}")
        fName = f"./{filename}"
        if os.path.exists(fName) and not os.path.isdir(fName):
            ignoreFiles = any(ign in filename for ign in ["secret", "log", "dump"])
            if (not ignoreFiles) or (ctx.author.id == gxConfig.ownerID):
                from config import dataObject

                dataObject.TYPE = "CommandAuditGet"
                dataObject.userObject = ctx.author
                dataObject.filename = filename
                dataObject.auditID = int(
                    getChan(guild=ctx.guild.id, chan="Audit", admin=True)
                )
                log.debug("send auditlog")
                await auditLogger.logEmbed(self, dataObject)
                log.debug("make file")
                file = nextcord.File(fName)
                log.debug(f"send file {fName=}")
                try:
                    await ctx.send(file=file)
                except Exception:
                    log.exception(f"AuditGet {fName=}")
                del dataObject
            else:
                try:
                    await ctx.send("File contains sensitive infomation.")
                except Exception:
                    log.exception(f"AuditGet Sensitive")

        else:
            try:
                await ctx.send(
                    """File not found. Please include the extension.
If in a folder please include the foldername followed by a slash. eg [ foldername/filename ]"""
                )
            except Exception:
                log.exception(f"AuditGet No File")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def rolebuttons(self, ctx: commands.Context, viewArg: str):
        """Trigger the role button messages for the guild the command was invoked from."""
        if not await blacklistCheck(ctx=ctx):
            return
        guildID = int(ctx.guild.id)
        log.debug(f"{guildID=} | usr={ctx.author.id} | {viewArg=}")
        await ctx.message.delete()
        viewsDict = {
            "tpfroles": views.tpfroles(),
            "sscroles": views.sscroles(),
            "nixroles": views.nixroles(),
            "nixcols": views.nixrolesCOL(),
        }
        descDict = {
            "tpfroles": "Pick which roles you'd like.\nModder intern gives access to special channels full of useful info.",
            "sscroles": "Opt in/out of the SSC notifications",
            "nixroles": "Pick which roles you'd like.",
        }
        if viewArg not in viewsDict:
            raise commands.ArgumentParsingError
        if viewArg in descDict:
            desc = descDict[viewArg]
            e = nextcord.Embed(
                title="Roles",
                description=desc,
                colour=getCol("neutral_Light"),
            )
        try:
            if e:
                await ctx.send(embed=e, view=viewsDict[viewArg])
            else:
                await ctx.send(view=viewsDict[viewArg])
        except Exception:
            chan = ctx.channel
            log.exception(f"View {viewArg} | {guildID=} | chan={chan.id}:{chan.name}")

    @slash_command(
        name=_("COMM_CONFIG_BASE_NAME", gxConfig.defaultLang),
        name_localizations=_("COMM_CONFIG_BASE_NAME"),
        default_member_permissions=Permissions(administrator=True),
        guild_ids=gxConfig.slashServers,
    )
    async def configurationBASE(self, interaction: Interaction):
        log.debug(f"configurationBASE {interaction.user.id}")

    @configurationBASE.subcommand(
        name=_("COMM_CONFIG_GUILD_NAME", gxConfig.defaultLang),
        name_localizations=_("COMM_CONFIG_GUILD_NAME"),
        description=_("COMM_CONFIG_GUILD_DESC", gxConfig.defaultLang),
        description_localizations=_("COMM_CONFIG_GUILD_DESC"),
    )
    async def configurationCOMM(
        self,
        interaction: Interaction,
        group: str = SlashOption(
            name=_("COMM_CONFIG_GUILD_GROUP_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_CONFIG_GUILD_GROUP_NAME"),
            description=_("COMM_CONFIG_GUILD_GROUP_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_CONFIG_GUILD_GROUP_DESC"),
            required=True,
        ),
        option: str = SlashOption(
            name=_("COMM_CONFIG_GUILD_OPTION_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_CONFIG_GUILD_OPTION_NAME"),
            description=_("COMM_CONFIG_GUILD_OPTION_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_CONFIG_GUILD_OPTION_DESC"),
            required=True,
        ),
        value: str = SlashOption(
            name=_("COMM_CONFIG_GUILD_VALUE_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_CONFIG_GUILD_VALUE_NAME"),
            description=_("COMM_CONFIG_GUILD_VALUE_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_CONFIG_GUILD_VALUE_DESC"),
            required=True,
        ),
    ):
        """Guild admins can change bot configuration for their guild."""
        guildID = int(interaction.guild_id)
        if value.lower() in ("false", "none"):
            value = None
        elif value.isdigit():
            value = int(value)
        # else:
        #    try:
        #        await interaction.send(f"ValueError")
        #    except Exception:
        #        log.exception(f"config /command ValueError")
        configuration = readJSON(filename="config")
        try:
            oldValue = str(configuration[str(guildID)][group][option])
        except KeyError as xcp:
            if group in str(xcp):
                err = group
            elif option in str(xcp):
                err = option
            await interaction.send(f"KeyError: {err}", ephemeral=True)
        except Exception:
            log.exception("Config /Command")
        configuration[str(guildID)][group][option] = value
        guildName = geConfig.guildListID[guildID]
        log.info(
            f"ConfigUpdated: {guildName}, {interaction.user.id}, {group}-{option}:{oldValue} | {value}"
        )
        from config import dataObject

        dataObject.TYPE = "CommandGuildConfiguration"
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
            try:
                geConfig.update()
                await interaction.send(
                    f"Config updated: {group}-{option}\n{oldValue} -> {value}"
                )
            except Exception:
                log.exception(f"Config Update")
        else:
            try:
                await interaction.send("Config not updated!", ephemeral=True)
            except Exception:
                log.exception(f"No Config Change")
        del dataObject

    @configurationCOMM.on_autocomplete("group")
    async def configurationGroup(self, interaction: Interaction, group):
        """Autocomplete function for use with the configuration command 'group' arg"""
        guildID = int(interaction.guild_id)
        groups = readJSON(filename="config")[str(guildID)]
        configList = []
        groupWhiteList = gxConfig.configCommGroupWhitelist
        for itemKey, itemVal in groups.items():
            if isinstance(itemVal, dict):
                if str(itemKey) in groupWhiteList:
                    configList.append(itemKey)
        await interaction.response.send_autocomplete(configList)

    @configurationCOMM.on_autocomplete("option")
    async def configurationOption(self, interaction: Interaction, option, group):
        """Autocomplete function for use with the configuration command 'option' and 'group' args"""
        if group is None:
            return
        optionsList = ["undefined"]
        guildID = int(interaction.guild_id)
        configuration = readJSON(filename="config")[str(guildID)][group]
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
        """Autocomplete function for use with the configuration command 'value', 'group', and 'option' args"""
        if group is None or option is None:
            return
        print(group, option)
        guildID = int(interaction.guild_id)
        configuration = readJSON(filename="config")[str(guildID)]
        configItem = []
        try:
            item = str(configuration[group][option])
            if item is None:
                item = "***Undefined Value***"
            configItem.append(item)
        except KeyError:
            configItem.append("***Undefined Key***")
        except Exception:
            log.exception("Config Command Autocomplete")
        if len(configItem) == 0:
            configItem.append("***Undefined Error***")
        if len(value) >= 1:
            configItem.append(value)
        await interaction.response.send_autocomplete(configItem)

    @configurationBASE.subcommand(
        name=_("COMM_CONFIG_AUTOREACT_NAME", gxConfig.defaultLang),
        name_localizations=_("COMM_CONFIG_AUTOREACT_NAME"),
        description=_("COMM_CONFIG_AUTOREACT_DESC", gxConfig.defaultLang),
        description_localizations=_("COMM_CONFIG_AUTOREACT_DESC"),
    )
    async def configurationAutoReact(
        self,
        interaction: Interaction,
        reactor: str = SlashOption(
            required=True,
            name=_("COMM_CONFIG_AUTOREACT_REACTOR_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_CONFIG_AUTOREACT_REACTOR_NAME"),
            description=_("COMM_CONFIG_AUTOREACT_REACTOR_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_CONFIG_AUTOREACT_REACTOR_DESC"),
        ),
        messageID: str = SlashOption(
            required=False,
            name=_("COMM_CONFIG_AUTOREACT_MESSAGEID_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_CONFIG_AUTOREACT_MESSAGEID_NAME"),
            description=_("COMM_CONFIG_AUTOREACT_MESSAGEID_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_CONFIG_AUTOREACT_MESSAGEID_DESC"),
        ),
        strictMatch: bool = SlashOption(
            required=False,
            name=_("COMM_CONFIG_AUTOREACT_STRICTMATCH_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_CONFIG_AUTOREACT_STRICTMATCH_NAME"),
            description=_(
                "COMM_CONFIG_AUTOREACT_STRICTMATCH_DESC", gxConfig.defaultLang
            ),
            description_localizations=_("COMM_CONFIG_AUTOREACT_STRICTMATCH_DESC"),
        ),
        extraChannel: nextcord.TextChannel = SlashOption(
            required=False,
            name=_("COMM_CONFIG_AUTOREACT_EXTRACHANNEL_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_CONFIG_AUTOREACT_EXTRACHANNEL_NAME"),
            description=_(
                "COMM_CONFIG_AUTOREACT_EXTRACHANNEL_DESC", gxConfig.defaultLang
            ),
            description_localizations=_("COMM_CONFIG_AUTOREACT_EXTRACHANNEL_DESC"),
        ),
        deleteAR: bool = SlashOption(
            required=False,
            name=_("COMM_CONFIG_AUTOREACT_DELETE_NAME", gxConfig.defaultLang),
            name_localizations=_("COMM_CONFIG_AUTOREACT_DELETE_NAME"),
            description=_("COMM_CONFIG_AUTOREACT_DELETE_DESC", gxConfig.defaultLang),
            description_localizations=_("COMM_CONFIG_AUTOREACT_DELETE_DESC"),
        ),
    ):
        guildID = int(interaction.guild_id)
        log.debug(f"Subcommand {reactor=} {guildID=}")
        setReactor = bool(messageID)
        if setReactor:
            if (messageID.startswith("https")) and ("discord" in messageID):
                url, urlChan, urlMess = messageID.rsplit("/", 2)
                channelID = int(urlChan)
                messageID = int(urlMess)
            else:
                channelID = int(interaction.channel.id)
                messageID = int(messageID)
        deleteAR = bool(deleteAR)

        logSys.debug(
            f"{guildID=} | {setReactor=} | {messageID=} | {strictMatch=} | {extraChannel=} | {deleteAR=}"
        )
        from config import dataObject as data

        data.auditChan = getChan(self=self, guild=guildID, chan="Audit", admin=True)
        data.userObject = interaction.user

        def reduceList(obj: list | tuple, nameOnly: bool = False):
            logSys.debug(f"{obj=} | {nameOnly=}")
            objList = []
            if isinstance(obj, str | int):
                return str(obj)
            elif isinstance(obj, list | tuple):
                for item in obj:
                    logSys.debug(f"{type(item)=}")
                    if isinstance(item, list | tuple):
                        if nameOnly or (len(item) == 1):
                            objList.append(f"{item[0]}")
                        else:
                            objList.append(f"{item[0]} ({item[1]})")
                    else:
                        objList.append(item)
            return objList

        if guildID in list(geConfig.autoReacts):
            if reactor in list(geConfig.autoReacts[guildID]):
                try:
                    oldReactorDict = geConfig.autoReacts[guildID][reactor]
                except Exception:
                    log.exception(f"Get Current AutoReact")
                    oldReactorDict = False
                else:
                    if deleteAR:
                        data.TYPE = "CommandAutoReact_Delete"
                        data.channelList = ", ".join(
                            reduceList(oldReactorDict["Channel"])
                        )
                        data.messageContent = ", ".join(oldReactorDict["Contains"])
                        data.emojiList = ", ".join(reduceList(oldReactorDict["Emoji"]))
                        data.flagA = oldReactorDict["isExactMatch"]
                        try:
                            await auditLogger.logEmbed(self, auditInfo=data)
                        except Exception:
                            log.exception(f"Send Audit")
                        configuration = readJSON("config")
                        del configuration[str(guildID)]["AutoReact"][reactor]
                        if writeJSON(configuration, "config"):
                            txt = "AutoReact reactor deleted!"
                            geConfig.update()
                        else:
                            txt = "Failed to delete AutoReact reactor"
                        try:
                            await interaction.send(txt)
                        except Exception:
                            log.exception(f"Del AutoReact Message")
                        try:
                            del configuration
                        except Exception:
                            log.exception(f"Del AutoReact Config")
                        return
        else:
            oldReactorDict = False

        if setReactor:
            if channelID != interaction.channel.id:
                chan = self.bot.get_channel(channelID)
            else:
                chan = interaction.channel
            try:

                mess = await chan.fetch_message(int(messageID))
            except nextcord.NotFound:
                logSys.exception(f"Message Not Found")
                await interaction.send("Message Not Found", ephemeral=True)
                return
            except nextcord.Forbidden:
                logSys.exception("Message Forbidden")
                await interaction.send("Message Not Accessible", ephemeral=True)
                return
            except Exception:
                logSys.exception(f"Fetch Message Channel")
                await interaction.send("Unknown Exception", ephemeral=True)
                return
            messContent = (mess.content).split(" ")
            messReac = mess.reactions
            if len(messReac) == 0:
                await interaction.send(
                    "This message does have any reactions", ephemeral=True
                )
                return
            reactsAll = sortReactions(messReac)
            if len(reactsAll.Bad) > 0:
                await interaction.send(f"These emoji can't be used.\n{reactsAll.Bad}")
                return
            if len(reactsAll.Unk) > 0:
                await interaction.send(f"Unknown issue;\n{reactsAll.Unk}")
                return
            chanID = [(chan.name, chan.id)]
            if extraChannel:
                chanID.append((extraChannel.name, extraChannel.id))
            reactorDict = {}
            reactorDict["Channel"] = chanID
            reactorDict["Contains"] = messContent
            reactorDict["Emoji"] = reactsAll.Str + reactsAll.Obj
            reactorDict["isExactMatch"] = bool(strictMatch)

            data.channelList = ", ".join(reduceList(chanID))
            data.messageContent = ", ".join(messContent)
            data.emojiList = ", ".join(reduceList((reactsAll.Str + reactsAll.Obj)))
            data.flagA = bool(strictMatch)

            configuration = readJSON("config")
            configuration[str(guildID)]["AutoReact"][reactor] = {}
            configuration[str(guildID)]["AutoReact"][reactor] = reactorDict

            if writeJSON(data=configuration, filename="config"):
                await interaction.send("Reactor updating! Check auditlog for details")
        else:
            if oldReactorDict:
                await interaction.send(f"{' '.join(oldReactorDict['Contains'])}")
                temp = interaction.channel.last_message
                for emo in oldReactorDict["Emoji"]:
                    if isinstance(emo, tuple | list):
                        emo = self.bot.get_emoji(geConfig.getNameID(emo, name=False))
                    if emo:
                        await temp.add_reaction(emo)
                await interaction.send(
                    f"The channels this reactor watches\n{reduceList(oldReactorDict['Channel'])}"
                )
            else:
                await interaction("Failed to retrieve Reactor")
        if setReactor:
            data.TYPE = "CommandAutoReact"
            await auditLogger.logEmbed(self, auditInfo=data)
            del data
            geConfig.update()

    @configurationAutoReact.on_autocomplete("reactor")
    async def configurationARGetReactor(self, interaction: Interaction, reactor):
        guildID = int(interaction.guild_id)
        reactors = geConfig.autoReacts[guildID]
        reactorList = []
        for itemKey, itemVal in reactors.items():
            if isinstance(itemVal, dict):
                reactorList.append(itemKey)
        if len(reactor) >= 1:
            reactorList.append(reactor)
        await interaction.response.send_autocomplete(reactorList)

    @commands.command(name="react", aliases=["emoji"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def react(self, ctx: commands.Context):
        """Takes message IDs and emoji and reacts to the messages with the emoji"""
        print(ctx.message.content)
        rawItems = ctx.message.content.split(" ")[1:]
        messIDs = []
        emojiSet = set()
        for item in rawItems:
            if item[0].isdigit():
                messIDs.append(int(item))
            elif item[0].startswith("<"):
                emojiSet.add(item)
            else:
                emojiSet.add(item)
        messOBJs = []
        print(messIDs)
        print(emojiSet)
        for item in messIDs:
            messOBJs.append(await ctx.fetch_message(int(item)))
        if len(emojiSet) == 0:
            emojiSet = ["⭐"]
        badEmoji = set()
        for item in messOBJs:
            for element in emojiSet:
                try:
                    await item.add_reaction(element)
                except Exception as xcp:
                    log.exception("Unknown Emoji")
                    if "Unknown Emoji" in str(xcp):
                        badEmoji.add(element)
        if len(badEmoji) != 0:
            try:
                await ctx.send(f"Some emoji aren't accessible: {', '.join(badEmoji)}")
            except Exception:
                log.exception(f"Inaccessible Emoji {badEmoji=}")
        log.info(f"{messIDs}, {emojiSet}")
        await ctx.message.delete()


def setup(bot: commands.Bot):
    bot.add_cog(admin(bot))


# MIT APasz
