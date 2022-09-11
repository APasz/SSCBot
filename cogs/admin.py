import asyncio
import logging
import os

from config import generalEventConfig as geConfig
from config import genericConfig as gxConfig
from util.fileUtil import readJSON, writeJSON
from util.genUtil import blacklistCheck, getChan, getCol
from util.views import nixroles, nixrolesCOL, tpfroles

from cogs.auditLog import auditLogger

print("CogAdmin")

log = logging.getLogger("discordGeneral")
try:
    log.debug("TRY ADMIN IMPORT MODULES")
    import nextcord
    from discord import Permissions
    from nextcord import Interaction, SlashOption, slash_command
    from nextcord.ext import commands
except Exception:
    log.exception("ADMIN IMPORT MODULES")


def auditChanGet(guildID) -> int:
    """With the ID of a server, returns either it's auditlog channel or if it has none specified, the owner server auditlog channel"""
    log.debug("auditGet")
    audit = gxConfig.auditChan
    if str(guildID) in audit.keys():
        return int(audit[f"{guildID}"])
    else:
        return int(gxConfig.ownerAuditChan)


class admin(commands.Cog, name="Admin"):
    """Class containing commands and functions related to administration of servers (not bot config)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(tpfroles())
        self.bot.add_view(nixroles())
        self.bot.add_view(nixrolesCOL())
        log.debug(f"{self.__cog_name__} Ready")

    async def purge(self, ctx, limit: int) -> bool:
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
            await auditLogger.logEmbed(self, dataObject)
            await ctx.channel.purge(limit=limit2)
            del dataObject
            return True
        return False

    @commands.command(name="purge")
    @commands.cooldown(2, 7.5, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def purgeComm(self, ctx, limit: int):
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
    async def blacklist(self, ctx, usr: str, reason: str = "No reason given"):
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
            if check == True:
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
    async def blacklistRemove(self, ctx, usr: str):
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
            if check == True:
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
                or ("dump" not in filename)
                or (ctx.author.id == gxConfig.ownerID)
            ):
                from config import dataObject
                dataObject.TYPE = "CommandAuditGet"
                dataObject.userObject = ctx.author
                dataObject.filename = filename
                dataObject.auditID = int(getChan(
                    guild=ctx.guild.id, chan="Audit", admin=True
                ))
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
    async def rolebuttons(self, ctx):
        """Trigger the role button messages for the server the command was invoked from."""
        if not await blacklistCheck(ctx=ctx):
            return
        guildID = str(ctx.guild.id)
        await ctx.message.delete()
        nix = False
        guilds = geConfig.guildListID
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
        try:
            await ctx.send(embed=e, view=view)
            if nix == True:
                await ctx.send(view=view2)
            await view.wait()
        except Exception:
            log.exception(f"Views {ctx.guild.id}")

    @slash_command(
        name="configuration",
        default_member_permissions=Permissions(administrator=True),
        guild_ids=gxConfig.slashServers,
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
            try:
                await interaction.send(f"ValueError")
            except Exception:
                log.exception(f"config /command ValueError")
        configuration = readJSON(filename="config")
        try:
            oldValue = str(configuration[guildID][group][option])
        except KeyError as xcp:
            if group in str(xcp):
                err = group
            elif option in str(xcp):
                err = option
            await interaction.send(f"KeyError: {err}", ephemeral=True)
        except Exception:
            log.exception("Config /Command")
        configuration[guildID][group][option] = value
        log.info(
            f"ConfigUpdated: {geConfig.guildListID[guildID]}, {interaction.user.id}, {group}-{option}:{oldValue} | {value}"
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
        guildID = str(interaction.guild_id)
        groups = readJSON(filename="config")[guildID]
        configList = []
        groupWhiteList = gxConfig.configCommGroupWhitelist
        for itemKey, itemVal in groups.items():
            if "dict" in str(type(itemVal)):
                if str(itemKey) in groupWhiteList:
                    configList.append(itemKey)
        await interaction.response.send_autocomplete(configList)

    @configurationCOMM.on_autocomplete("option")
    async def configurationOption(self, interaction: Interaction, option, group):
        """Autocomplete function for use with the configuration command 'option' and 'group' args"""
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
        """Autocomplete function for use with the configuration command 'value', 'group', and 'option' args"""
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
        except Exception:
            log.exception("Config Command Autocomplete")
        if len(configItem) == 0:
            configItem.append("Undefined Error")
        if len(value) >= 1:
            configItem.append(value)
        await interaction.response.send_autocomplete(configItem)

    @commands.command(name="react", aliases=["emoji"])
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def react(self, ctx):
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
            messOBJs.append(await ctx.fetch_message(item))
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
