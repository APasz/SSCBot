import asyncio
import logging
import random
import time

from config import genericConfig as gxConfig
from config import screenShotCompConfig as sscConfig
from util.apiUtil import GSheetGet
from util.fileUtil import readJSON, writeJSON
from util.genUtil import blacklistCheck, getChan, getCol, hasRole

print("CogSSC")

log = logging.getLogger("discordGeneral")
try:
    log.debug("TRY SSC IMPORT MODULES")
    import datetime

    import nextcord
    import nextcord.ext.commands  # import Context
    from discord import Permissions
    from nextcord import Interaction, SlashOption, slash_command
    from nextcord.ext import application_checks, commands, tasks
except Exception:
    log.exception("SSC IMPORT MODULES")


async def timestampset() -> bool:
    """Refreshes the timestamps for the SSC"""
    log.debug("timeStampset")
    utc = datetime.datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0)
    monUTC = utc - datetime.timedelta(days=utc.weekday())
    currStamp = int((monUTC - datetime.datetime(1970, 1, 1)).total_seconds())
    nextStamp = int(currStamp) + 604800
    stamp36 = int(currStamp) + 475200
    stamp24 = int(currStamp) + 518400
    remindStamp = int(random.randint(stamp36, stamp24))
    configuration = readJSON(filename="config")
    configSSC = configuration["General"]["SSC_Data"]
    currData = int(configSSC["currStamp"])
    nextData = int(configSSC["nextStamp"])
    rminData = int(configSSC["remindStamp"])
    log.debug(f"{currStamp=}, {nextStamp=}, {stamp36=}, {stamp24=}")
    log.debug(f"{currData=}, {nextData=}, {rminData=}")
    if currStamp == currData:
        pass
    else:
        configSSC["currStamp"] = currStamp
        log.debug("Cwrite")
    if nextStamp == nextData:
        pass
    else:
        configSSC["nextStamp"] = nextStamp
        log.debug("Nwrite")
    if stamp36 <= rminData <= stamp24:
        pass
    else:
        configSSC["remindStamp"] = remindStamp
        log.debug("Rwrite")
    if writeJSON(data=configuration, filename="config"):
        sscConfig.update()
        return True
    else:
        sscConfig.update()
        return False


class ssc(commands.Cog, name="SSC"):
    """Class containing commands to run the SSC"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.remindTask.start()

    @commands.Cog.listener()
    async def on_ready(self):
        log.debug(f"{self.__cog_name__} Ready")
        log.debug(
            f"{sscConfig.tpfID=}, {sscConfig.sscChan=}, {sscConfig.sscmanager=}, {gxConfig.ownerGuild=}"
        )

    @tasks.loop(
        minutes=readJSON(filename="config")[
            "General"]["TaskLengths"]["SSC_Remind"]
    )
    async def remindTask(self):
        """Get reminder timestamp from file, check if current time is in within range of remindStamp and nextStamp(-2h), if so invoke SSC minder command"""
        configuration = readJSON(filename="config")
        configSSC = configuration["General"]["SSC_Data"]
        log.debug(f"remindTask_run:rmSent {configSSC['remindSent']}")
        if configSSC["remindSent"] == True:
            log.debug(f"remindYes {configSSC['remindSent']}")
            return
        nex = int(configSSC["nextStamp"])
        rem = int(configSSC["remindStamp"])
        n = nex - 7200
        t = int(time.time())
        if rem <= t <= n:
            alert = configSSC["alertType"]
            configSSC["remindSent"] = True
            writeJSON(data=configuration, filename="config")
            log.debug(f"PT: {alert=}")
            chan = getChan(self=self, guild=sscConfig.tpfID, chan="SSC_Comp")
            try:
                await chan.send(
                    f"Reminder that the competiton ends soon;\n**<t:{nex}:R>**\nGet you images and votes in. 🇻 🇴 🇹 🇪 @{alert}"
                )
            except Exception:
                log.exception(f"SSC Reminder")
            await asyncio.sleep(0.1)
            lastID = chan.last_message_id
            mess = await chan.fetch_message(int(lastID))
            emojis = [gxConfig.emoNotifi]
            for emoji in emojis:
                await mess.add_reaction(emoji)
            log.info(f"SSC Reminder: {alert=}")
        sscConfig.update()

    @remindTask.before_loop
    async def before_remindTask(self):
        await self.bot.wait_until_ready()

    @remindTask.after_loop
    async def on_remindTask_cancel(self):
        log.warning("on_remindTask Cancelled")

    @commands.command(name="timestamp", hidden=True)
    async def timestamp(self, ctx, action="get"):
        """By default returns the timestamps for the SSC. A set argument will refresh them"""
        if not await blacklistCheck(ctx=ctx):
            return
        log.debug(f"{action=}")
        if action == "get":
            configSSC = readJSON(filename="config")["General"]["SSC_Data"]
            curr = configSSC["currStamp"]
            next = configSSC["nextStamp"]
            rmin = configSSC["remindStamp"]
            try:
                await ctx.send(
                    f"Current week's stamp {curr} | <t:{curr}:R>\n"
                    f"Next week's stamp {next} | <t:{next}:R>\n"
                    f"Reminder stamp {rmin} | <t:{rmin}:R>"
                )
            except Exception:
                log.exception(f"Timestamps")
        elif action == "set":
            try:
                if await timestampset():
                    await ctx.send("Stamps updated.")
                else:
                    await ctx.send("Error during stamp update.")
            except Exception:
                log.exception(f"Timestamps Set")
        sscConfig.update()

    @slash_command(
        name="sscomp-start",
        guild_ids=[
            int(gxConfig.ownerGuild),
            int(sscConfig.tpfID),
        ],
    )
    # @application_checks.has_role(sscConfig.sscmanager)
    async def comp(
            self,
            interaction: Interaction,
            banner: nextcord.Attachment = SlashOption(
                name="banner",
                required=True,
                description="The image shown in the competition embed. Name of file is used as theme, - replaced with space.",
            ),
            bannerFull1: nextcord.Attachment = SlashOption(
                name="bannerfull1",
                required=False,
                description="The original image that makes the banner",
            ),
            bannerFull2: nextcord.Attachment = SlashOption(
                name="bannerfull2",
                required=False,
                description="The second image that makes the banner",
            ),
            bannerFull4: nextcord.Attachment = SlashOption(
                name="bannerfull3",
                required=False,
                description="The third image that makes the banner",
            ),
            bannerFull8: nextcord.Attachment = SlashOption(
                name="bannerfull4",
                required=False,
                description="The fourth image that makes the banner",
            ),
            bannerFull1OG: nextcord.Attachment = SlashOption(
                name="bannerfull1-og",
                required=False,
                description="The original image that makes the banner but for othergames channel",
            ),
            bannerFull2OG: nextcord.Attachment = SlashOption(
                name="bannerfull2-og",
                required=False,
                description="The second image that makes the banner but for othergames channel",
            ),
            bannerFull4OG: nextcord.Attachment = SlashOption(
                name="bannerfull3-og",
                required=False,
                description="The third image that makes the banner but for othergames channel",
            ),
            bannerFull8OG: nextcord.Attachment = SlashOption(
                name="bannerfull4-og",
                required=False,
                description="The fourth image that makes the banner but for othergames channel",
            ),
            note: str = SlashOption(
                name="note",
                required=False,
                description="If the theme has any restrictions or tips. Overrides existing.",
            ),
            prize: str = SlashOption(
                name="prize",
                required=False,
                description="If the is a prize round, what is it?",
            ),
            prizeUser: nextcord.Member = SlashOption(
                name="prize-giver",
                required=False,
                description="Who is providing the prize. Format is 'prize' provided by 'prize giver'",
            ),
            ignoreWinner: bool = SlashOption(
                name="ignore-winner",
                required=False,
                default=bool(False),
                description="For special rounds where SSCManager would like everyone to participate.",
            ),
    ):
        """To start the screenshot competition. SSCManager Only"""
        if not await blacklistCheck(ctx=interaction):
            return
        if not hasRole(role=interaction.guild.get_role(int(sscConfig.sscmanager)), userRoles=interaction.user.roles):
            await interaction.send("Must have SSC Manager role", ephemeral=True)
            return
        log.debug(
            f"{interaction.user.id=}, {banner.filename=}, {note=}, {prize=}, {prizeUser=}"
        )
        configuration = readJSON(filename="config")
        configSSC = configuration["General"]["SSC_Data"]
        configSSC["remindSent"] = False
        configSSC["ignoreWinner"] = ignoreWinner
        if not await timestampset():
            try:
                interaction.send("timeStampSet Failed", ephemeral=True)
            except Exception:
                log.exception(f"/Timestamp Set")
            return
        theme = banner.filename.split(".")[0].replace("-", " ")
        configuration["General"]["SSC_Data"]["theme"] = theme
        nextstamp = int(configSSC["nextStamp"])
        strSSC = readJSON(filename="strings")["en"]["SSC"]
        txt_CompStart = strSSC["Start"]
        txt_CompEnd = strSSC["End"]
        txt_CompGift = strSSC["Gift"]
        txt_CompRules = strSSC["Rules"]
        txt_CompTheme = strSSC["Theme"]

        ebed = nextcord.Embed(title=txt_CompStart, colour=getCol("ssc"))
        if prize:
            configuration["General"]["SSC_Data"]["isPrize"] = True
            if prizeUser:
                giver = f" provided by {prizeUser.mention}"
            else:
                giver = ""
            ebed.add_field(name=txt_CompGift,
                           value=f"{prize}{giver}", inline=False)
        else:
            configuration["General"]["SSC_Data"]["isPrize"] = False
        ebed.add_field(name=txt_CompTheme, value=f"{theme}", inline=True)
        ebed.add_field(name=txt_CompEnd,
                       value=f"<t:{nextstamp}:f>", inline=True)
        if note is not None:
            ebed.add_field(name="**Note**",
                           value=f"\n```\n{note}\n```", inline=False)
        elif configSSC["allThemes"][theme] is not None:
            ebed.add_field(
                name="**Note**",
                value=f"\n```\n{configSSC['allThemes'][theme]}\n```",
                inline=False,
            )
        if not writeJSON(data=configuration, filename="config"):
            try:
                await interaction.send("Failed to write to config", ephemeral=True)
            except Exception:
                log.exception(f"Write SSC")
            return
        ebed.set_footer(text=txt_CompRules)
        if banner.content_type.startswith("image"):
            ebed.set_image(url=banner.url)
            try:
                last = await interaction.send(embed=ebed)
            except Exception:
                log.exception(f"Banner")
        else:
            file = nextcord.File("missing.png")
            ebed.set_image(url="attachment://missing.png")
            try:
                last = await interaction.send(file=file, embed=ebed)
            except Exception:
                log.exception(f"Missing.png")
        try:
            last = await last.fetch()
        except Exception:
            log.exception(f"SSC Last")
        emoListA = [gxConfig.emoTmbUp, gxConfig.emoTmbDown]
        for element in emoListA:
            await last.add_reaction(element)
        try:
            if self.remindTask.is_running:
                log.debug("Try remindTask Running")
            else:
                self.remindTask.start()
                log.debug("Try remindTask Started")
        except:
            log.debug("remindTask not already running")
        log.debug("remindTask Triggered")

        def check(m):
            if m.author == interaction.user and m.channel == interaction.channel:
                return True

        alert = await self.bot.wait_for("message", check=check, timeout=30.0)
        if alert:
            configuration = readJSON(filename="config")
            configSSC = configuration["General"]["SSC_Data"]
            cont = alert.content.split(" ")
            for item in cont:
                if "@" in item:
                    configSSC["alertType"] = item.removeprefix("@")
                    break
            if not writeJSON(data=configuration, filename="config"):
                await interaction.send("Failed to write to config", ephemeral=True)
                return
            emoListB = [gxConfig.emoNotifi]
            for element in emoListB:
                await alert.add_reaction(element)
        log.info("Competition Start")
        bannerFullAll = [bannerFull1, bannerFull2, bannerFull4, bannerFull8]
        ssChan = self.bot.get_channel(sscConfig.TPFssChan)

        async def sendSS(chan, ss):
            ebed = nextcord.Embed(title=f"{theme} theme", colour=getCol("ssc"))
            ebed.set_image(url=ss.url)
            await chan.send(embed=ebed)

        for item in bannerFullAll:
            if item is not None:
                await sendSS(ssChan, item)
        bannerFullAllOG = [bannerFull1OG,
                           bannerFull2OG, bannerFull4OG, bannerFull8OG]
        ogChan = self.bot.get_channel(sscConfig.OGssChan)
        for item in bannerFullAllOG:
            if item is not None:
                await sendSS(ogChan, item)
        log.debug("Competition banner images posted")
        k = writeJSON(data=configuration, filename="config")
        log.debug(f"{k=}")
        sscConfig.update()

    @ slash_command(
        name="delete",
        default_member_permissions=Permissions(manage_messages=True),
        guild_ids=[
            int(gxConfig.ownerGuild),
            int(sscConfig.tpfID),
        ],
    )
    async def sscDelete(
            self,
            interaction: Interaction,
            messID: str = SlashOption(
                name="message-id",
                required=True,
                description="The ID of the message to delete.",
            ),
            reason: str = SlashOption(
                name="reason-preset",
                required=False,
                description="Preset reason for deletion",
                choices={
                    "Incorrect Theme": "1",
                    "Reposted": "2",
                    "Edited": "3",
                    "Too many submissions": "4"
                },
            ),
            customReason: str = SlashOption(
                name="reason-custom",
                required=False,
                description="Custom reason for deletion? Note that your nick will be appended.",
            ),
    ):
        """Deletes message informs author of reason."""
        print("sscDelete")
        log.debug(
            f"{interaction.user.id=}, {messID=}, {reason=}|{customReason=}")
        if reason is None and customReason is None:
            interaction.send("A reason must be given.", ephemeral=True)

        SSC_Data = readJSON(filename="config")["General"]["SSC_Data"]
        theme = SSC_Data["theme"]
        try:
            themeNote = SSC_Data["allThemes"][theme]
        except:
            themeNote = None
        txt = ["Your image was deleted;"]
        if reason == "1":
            txt.append(f"It does not fit this week's theme of; **{theme}**")
            if themeNote is not None:
                txt.append(f"```\n{themeNote}\n```")
        elif reason == "2":
            txt.append("It's been posted before,")
        elif reason == "3":
            txt.append("It has been edited.")
        elif reason == "4":
            txt.append(
                "Too many submissions. There is a limit on number of submissions per user.\nPlease refer to rules.")

        cusRea = f"```\n{customReason}\n```\n-{interaction.user.display_name}"
        if reason and customReason:
            txt.append("\n")
        if customReason:
            txt.append(cusRea)
        text = "\n".join(filter(None, txt))
        log.info(f"{interaction.user.id=}, {messID=}, {text=}")
        mess = await interaction.channel.fetch_message(messID)
        usr = await self.bot.fetch_user(mess.author.id)
        if usr.bot:
            await interaction.send("Author is bot, unable to send DM", ephemeral=True)
        elif usr:
            try:
                await usr.send(text)
            except Exception as xcp:
                log.exception("DM User")
                await interaction.send(f"Error!\n{xcp}", ephemeral=True)
        else:
            await interaction.send("User not found", ephemeral=True)
        await mess.delete()
        await interaction.send("Message deleted and DM sent.", ephemeral=True)

    def updateThemesList() -> bool:
        try:
            data = GSheetGet()
        except Exception:
            log.exception("GSheetFailed")
            return False
        themesList = data.get("A5:B")
        newThemesDic = {}
        for element in themesList:
            if len(element) == 1:
                newThemesDic[element[0]] = None
            else:
                newThemesDic[element[0]] = element[1]
        configuration = readJSON(filename="config")
        if configuration["General"]["SSC_Data"]["allThemes"] != newThemesDic:
            configuration["General"]["SSC_Data"]["allThemes"] = newThemesDic
            writeJSON(data=configuration, filename="config")
            sscConfig.update()
            return True
        return True

    @ slash_command(name="themevote")
    async def themeVote(
            self,
            interaction: Interaction,
            update: bool = SlashOption(
                name="update",
                description="Whether to pull from GSheet or not. SSCManager Only.",
                required=False,
                default=bool(False),
            ),
            ops: int = SlashOption(
                name="options",
                description="Number of options to be picked",
                min_value=2,
                max_value=9,
                required=False,
                default=3,
            ),
            themes: str = SlashOption(
                name="themes",
                required=False,
                description="Manually set theme options. Separate with : First item being completion of 'Vote for '",
            ),
    ):
        """Pull a number of themes for community to vote on. Can be used to vote on anything."""
        if not await blacklistCheck(ctx=interaction):
            return
        log.debug(f"{interaction.user.id=} | {update=}")
        # configuration = readJSON(filename="config")
        log.debug(
            f"exp: {interaction.is_expired()} | {interaction.expires_at.timestamp}")
        if update == True:
            await interaction.response.defer()
            role = interaction.guild.get_role(int(sscConfig.sscmanager))
            if not hasRole(role=role, userRoles=interaction.user.roles):
                await interaction.send("You're not SSC Manager.", ephemeral=True)
                return
            try:
                ssc.updateThemesList()
            except Exception:
                log.exception("Updating Themes")
                await interaction.send("Error updating themes", ephemeral=True)
                return
        if themes == None:
            themes = list((sscConfig.themesDict).keys())
        if isinstance(themes, list):
            log.debug("is list")
            while True:
                options = random.sample(themes, k=ops)
                if str(sscConfig.curTheme) in options:
                    print("theme in options")
                    pass
                else:
                    break
            txt = ["Vote for next week's theme."]
        else:
            log.debug("is str")
            opSplit = themes.split(":")
            txt = [f"Vote for {opSplit[0]}"]
            options = opSplit[1:]
        log.debug(f"{options=}")
        numb = {
            1: gxConfig.emo1,
            2: gxConfig.emo2,
            3: gxConfig.emo3,
            4: gxConfig.emo4,
            5: gxConfig.emo5,
            6: gxConfig.emo6,
            7: gxConfig.emo7,
            8: gxConfig.emo8,
            9: gxConfig.emo9,
        }
        emo = []
        for idx, element in enumerate(options):
            emo.append(numb[idx + 1])
            txt.append(f"{numb[idx+1]} {element}")
        log.debug(f"{emo=} | {txt=}")
        try:
            await interaction.send("\n".join(txt))
        except Exception:
            log.exception(f"/Themevote Last Send")
            await interaction.send("Failed!", ephemeral=True)
            return
        else:
            if update == True:
                log.debug(f"expSend: {interaction.is_expired()}")
            try:
                last = await interaction.original_message()
            except Exception:
                log.exception(f"/Themevote original")
        if update == True:
            log.debug(f"expFinal: {interaction.is_expired()}")
        for element in emo:
            try:
                await last.add_reaction(element)
            except Exception:
                log.exception(f"Themevote Send")

    @ commands.Cog.listener()
    async def on_message(self, ctx: nextcord.ext.commands.Context):
        """Check if message has attachment or link, if 1 add reaction, if not 1 delete and inform user, set/check prize round state, ignore SSCmanager,"""
        if ctx.content.startswith(f"{gxConfig.BOT_PREFIX}"):
            return
        log.debug(
            f"SSC listener {int(ctx.channel.id)} | {int(sscConfig.sscChan)}")
        if int(ctx.channel.id) != int(sscConfig.sscChan):
            return
        if ctx.author.bot:
            if int(ctx.author.id) == int(gxConfig.botID):
                return
            else:
                log.info("A bot did something")
                return
        if not await blacklistCheck(ctx=ctx, blklstType="ssc"):
            return
        if ctx.author.get_role(int(sscConfig.sscmanager)):
            if "upload" in ctx.content:
                try:
                    await ctx.add_reaction(gxConfig.emoStar)
                except Exception:
                    log.exception(f"SSC Manager add_reaction")
                log.info("Manager Submission")
                return
            else:
                log.info("Manager did something")
            return
        cont = str(ctx.content)
        if cont.startswith("http"):
            h = "y"
        else:
            h = "n"
        log.debug(f"{cont=}, {h=}")

        async def delete(ctx, delay: int | float = 0) -> bool:
            """Try to delete message."""
            await asyncio.sleep(delay)
            try:
                await ctx.delete()
                return True
            except Exception:
                log.exception("SSC Bad Submission")
                return False
        idName = f"{ctx.author.id},{ctx.author.display_name}"
        delTime = sscConfig.delTime
        if len(ctx.attachments) == 0 and h == "n":
            content = f"""Either no image or link detected. Please submit an image.
            \n{delTime}sec *self-destruct*"""
            try:
                await ctx.reply(content, delete_after=delTime)
                log.info(
                    f"Deletion_noImg: {idName}")
                await delete(ctx=ctx, delay=delTime)
            except Exception:
                log.exception(f"SSC on_message")
        if len(ctx.attachments) != 1 and h == "n":
            content = f"""Multiple images detected. Please resubmit one image at a time.\n{delTime}sec *self-destruct*"""
            try:
                await ctx.reply(content, delete_after=delTime)
                log.info(
                    f"Deletion_multiImg: {idName}")
                await delete(ctx=ctx, delay=delTime)
            except Exception:
                log.exception(f"SSC on_message")
        if len(ctx.attachments) == 1 or h == "y":
            if sscConfig.ignoreWinner == True:
                try:
                    await ctx.add_reaction(gxConfig.emoStar)
                except Exception:
                    log.exception(f"SSC add_reaction")
                return
            if sscConfig.isPrize == True:
                if ctx.author.get_role(int(sscConfig.winnerPrize)):
                    content = f"""You're a SSC Prize Winner, so can't participate in this round.\n{delTime}sec *self-destruct*"""
                    try:
                        await ctx.reply(content, delete_after=delTime)
                        log.info(
                            f"Deletion_PrizeWinner: {idName}"
                        )
                        await delete(ctx=ctx, delay=delTime)
                    except Exception:
                        log.exception(f"SSC on_message")
                else:
                    try:
                        await ctx.add_reaction(gxConfig.emoStar)
                        log.info(
                            f"SubmissionPrize: {idName}"
                        )
                    except Exception:
                        log.exception(f"SSC add_reaction")
                    return
            elif sscConfig.isPrize == False:
                if ctx.author.get_role(int(sscConfig.winner)) or ctx.author.get_role(
                        int(sscConfig.runnerUp)
                ):
                    log.debug("w")
                    hasRole(role=ctx.author.roles)
                    content = f"""You're a SSC Winner/Runner Up, so can't participate in this round.\n{delTime}sec *self-destruct*"""
                    try:
                        await ctx.reply(content, delete_after=delTime)
                        log.info(
                            f"Deletion_WinnerRunnerUp: {idName}"
                        )
                        await delete(ctx=ctx, delay=delTime)
                    except Exception:
                        log.exception(f"SSC on_message")
                else:
                    try:
                        await ctx.add_reaction(gxConfig.emoStar)
                        log.info(
                            f"Submission: {idName}")
                    except Exception:
                        log.exception(f"SSC add_reaction")
                    return
            else:
                log.warning(
                    f"Star: Mhmm: {idName}")
        else:
            log.debug("HUH")


def setup(bot: commands.Bot):
    bot.add_cog(ssc(bot))


# MIT APasz
