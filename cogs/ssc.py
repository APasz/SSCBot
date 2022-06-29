print("CogSSC")
import asyncio
import datetime
import logging
import os
import random
import time

import nextcord
import nextcord.ext
from discord import Permissions
from nextcord import Interaction, SlashOption, slash_command
from nextcord.ext import application_checks, commands, tasks

log = logging.getLogger("discordGeneral")

import config
from util.apiUtil import GSheetGet
from util.fileUtil import readJSON, writeJSON
from util.genUtil import blacklistCheck, getCol, hasRole


async def timestampset():
    log.debug("timeStampset")
    utc = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
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
    log.debug(f"{currStamp}, {nextStamp}, {stamp36}, {stamp24}")
    log.debug(f"{currData}, {nextData}, {rminData}")
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
        return True
    else:
        return False


class ssc(commands.Cog, name="TpFSSC"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.remindTask.start()

    @commands.Cog.listener()
    async def on_ready(self):
        if not os.path.exists("missing.png"):
            log.critical("ThemeFile; missing.png is missing")
        if not os.path.exists("randomFact.txt"):
            log.critical("randomFact.txt file is missing")
        log.debug("Ready")

    @tasks.loop(
        minutes=readJSON(filename="config")["General"]["TaskLengths"]["SSC_Remind"]
    )
    async def remindTask(self):
        """Get reminder timestamp from file, check if current time is in within range of remindStamp and nextStamp(-2h), if so invoke SSC minder command"""
        configuration = readJSON(filename="config")
        configSSC = configuration["General"]["SSC_Data"]
        log.debug(f"remindTask_run: {configSSC['remindSent']}")
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
            log.debug(f"PT: {alert}")
            chan = self.bot.get_channel(
                readJSON(filename="config")["TPFGuild"]["Channels"]["SSC_Remind"]
            )
            await chan.send(
                f"Reminder that the competiton ends soon;\n**<t:{nex}:R>**\nGet you images and votes in. 🇻 🇴 🇹 🇪 @{alert}"
            )
            await asyncio.sleep(0.1)
            lastID = chan.last_message_id
            mess = await chan.fetch_message(int(lastID))
            emojis = [config.emoNotifi]
            for emoji in emojis:
                await mess.add_reaction(emoji)
            log.info(f"SSC Reminder: {alert}")

    @remindTask.before_loop
    async def before_remindTask(self):
        await self.bot.wait_until_ready()

    @remindTask.after_loop
    async def on_remindTask_cancel(self):
        log.warning("on_remindTask Cancelled")

    @commands.command(name="timestamp", hidden=True)
    async def timestamp(self, ctx, action="get"):
        if not await blacklistCheck(ctx=ctx):
            return
        log.debug(action)
        if action == "get":
            configSSC = readJSON(filename="config")["General"]["SSC_Data"]
            curr = configSSC["currStamp"]
            next = configSSC["nextStamp"]
            rmin = configSSC["remindStamp"]
            await ctx.send(
                f"Current week's stamp {curr} | <t:{curr}:R>\n"
                f"Next week's stamp {next} | <t:{next}:R>\n"
                f"Reminder stamp {rmin} | <t:{rmin}:R>"
            )
        elif action == "set":
            if await timestampset():
                await ctx.send("Stamps updated.")
            else:
                await ctx.send("Error during stamp update.")

    @slash_command(
        name="sscomp-start",
        guild_ids=[
            int(readJSON(filename="config")["TPFGuild"]["ID"]),
            config.ownerGuild,
        ],
    )
    @application_checks.has_role(
        readJSON(filename="config")["TPFGuild"]["Roles"]["SSC_Manager"]
    )
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
            name="bannerfull4",
            required=False,
            description="The third image that makes the banner",
        ),
        bannerFull8: nextcord.Attachment = SlashOption(
            name="bannerfull8",
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
            name="bannerfull4-og",
            required=False,
            description="The third image that makes the banner but for othergames channel",
        ),
        bannerFull8OG: nextcord.Attachment = SlashOption(
            name="bannerfull8-og",
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
            default=False,
            description="For special rounds where SSCManager would like everyone to participate.",
        ),
    ):
        """To start the screenshot competition. SSCManager Only"""
        if not await blacklistCheck(ctx=interaction):
            return
        log.debug(
            f"{interaction.user.id}, {banner.filename}, {note}, {prize}, {prizeUser}"
        )
        configuration = readJSON(filename="config")
        configSSC = configuration["General"]["SSC_Data"]
        configSSC["remindSent"] = False
        configSSC["ignoreWinner"] = ignoreWinner
        if not await timestampset():
            interaction.send("timeStampSet Failed", ephemeral=True)
            return
        theme = banner.filename.split(".")[0].replace("-", " ")
        configSSC["theme"] = theme
        nextstamp = int(configSSC["nextStamp"])
        ebed = nextcord.Embed(title=config.txt_CompStart, colour=getCol("ssc"))
        if prize:
            configSSC["isPrize"] = True
            if prizeUser:
                giver = f" provided by {prizeUser.mention}"
            else:
                giver = ""
            ebed.add_field(
                name=config.txt_CompGift, value=f"{prize}{giver}", inline=False
            )
        else:
            configSSC["isPrize"] = False
        ebed.add_field(name=config.txt_CompTheme, value=f"{theme}", inline=True)
        ebed.add_field(name=config.txt_CompEnd, value=f"<t:{nextstamp}:f>", inline=True)
        if note is not None:
            ebed.add_field(name="**Note**", value=f"\n```\n{note}\n```", inline=False)
        elif configSSC["allThemes"][theme] is not None:
            ebed.add_field(
                name="**Note**",
                value=f"\n```\n{configSSC['allThemes'][theme]}\n```",
                inline=False,
            )
        if not writeJSON(data=configuration, filename="config"):
            await interaction.send("Failed to write to config", ephemeral=True)
            return
        ebed.set_footer(text=config.txt_CompRules)
        if banner.content_type.startswith("image"):
            ebed.set_image(url=banner.url)
            last = await interaction.send(embed=ebed)
        else:
            file = nextcord.File("missing.png")
            ebed.set_image(url="attachment://missing.png")
            last = await interaction.send(file=file, embed=ebed)
        last = await last.fetch()
        emoListA = [config.emoTmbUp, config.emoTmbDown]
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
            emoListB = [config.emoNotifi]
            for element in emoListB:
                await alert.add_reaction(element)
        log.info("Competition Start")
        bannerFullAll = [bannerFull1, bannerFull2, bannerFull4, bannerFull8]
        ssChan = self.bot.get_channel(
            configuration["TPFGuild"]["Channels"]["ScreenshotsTPF"]
        )

        async def sendSS(chan, ss):
            ebed = nextcord.Embed(title=f"{theme} theme", colour=getCol("ssc"))
            ebed.set_image(url=ss.url)
            await chan.send(embed=ebed)

        for item in bannerFullAll:
            if item is not None:
                await sendSS(ssChan, item)
        bannerFullAllOG = [bannerFull1OG, bannerFull2OG, bannerFull4OG, bannerFull8OG]
        ogChan = self.bot.get_channel(
            configuration["TPFGuild"]["Channels"]["ScreenshotsGames"]
        )
        for item in bannerFullAllOG:
            if item is not None:
                await sendSS(ogChan, item)
        log.debug("Competition banner images posted")

    @slash_command(
        name="delete",
        default_member_permissions=Permissions(manage_messages=True),
        guild_ids=[
            int(readJSON(filename="config")["TPFGuild"]["ID"]),
            config.ownerGuild,
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
                "Reposted": "1",
                "Edited": "It has been edited.",
            },
        ),
        customReason: str = SlashOption(
            name="reason-custom",
            required=False,
            description="Custom reason for deletion? Note that your nick will be appended.",
        ),
    ):
        """Deletes message informs author of reason. For custom reason, {} will be replaced with the relavent info."""
        print("sscDelete")
        log.debug(f"{interaction.user.id}, {messID}, {reason}|{customReason}")
        if reason is None and customReason is None:
            interaction.send("A reason must be given.", ephemeral=True)
        theme = readJSON(filename="config")["General"]["SSC_Data"]["theme"]
        try:
            themeNote = readJSON(filename="config")["General"]["SSC_Data"]["allThemes"][
                theme
            ]
        except:
            themeNote = None
        txt = ["Your image was deleted;"]
        if reason == "1":
            txt.append(f"It does not fit this week's theme of; **{theme}**")
            if themeNote is not None:
                txt.append(f"```\n{themeNote}\n```")
        elif reason == "2":
            txt.append("It's been posted before,")

        if reason and customReason:
            txt.append("\n")
        if customReason:
            txt.append(f"```\n{customReason}\n```\n-{interaction.user.display_name}")
        text = "\n".join(filter(None, txt))
        log.info(f"{interaction.user.id}, {messID}, {text}")
        mess = await interaction.channel.fetch_message(messID)
        usr = await self.bot.fetch_user(mess.author.id)
        if usr.bot:
            await interaction.send("Author is bot, unable to send DM", ephemeral=True)
        elif usr:
            await usr.send(text)
        else:
            await interaction.send("User not found", ephemeral=True)
        await mess.delete()
        await interaction.send("Message deleted and DM sent.", ephemeral=True)

    def updateThemesList(configuration):
        try:
            data = GSheetGet()
        except:
            return "GSheetFailed"
        themesList = data.get("A5:B")
        themesDic = {}
        for element in themesList:
            if len(element) == 1:
                themesDic[element[0]] = None
            else:
                themesDic[element[0]] = element[1]
        if configuration["General"]["SSC_Data"]["allThemes"] != themesDic:
            configuration["General"]["SSC_Data"]["allThemes"] = themesDic
            return writeJSON(data=configuration, filename="config")
        return True

    @slash_command(name="themevote", guild_ids=config.SlashServers)
    async def themeVote(
        self,
        interaction: Interaction,
        update: bool = SlashOption(
            name="update",
            description="Whether to pull from GSheet or not. SSCManager Only.",
            required=False,
            default=False,
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
        """Pull a number of themes for community to vote on"""
        if not await blacklistCheck(ctx=interaction):
            return
        log.debug(f"{Interaction.user}")
        configuration = readJSON(filename="config")
        if update is True:
            role = interaction.guild.get_role(
                readJSON(filename="config")["TPFGuild"]["Roles"]["SSC_Manager"]
            )
            if not hasRole(role=role, roles=interaction.user.roles):
                await interaction.send("You're not SSC Manager.", ephemeral=True)
                return
            try:
                self.updateThemesList(configuration)
            except:
                interaction.send("Error updating themes", ephemeral=True)
            configuration = readJSON(filename="config")
        themesDic = configuration["General"]["SSC_Data"]["allThemes"]
        if not themes:
            while True:
                options = random.sample((themesDic.keys()), k=ops)
                if configuration["General"]["SSC_Data"]["theme"] in options:
                    print("theme in options")
                    pass
                else:
                    break
            txt = ["Vote for next week's theme."]
        else:
            opSplit = themes.split(":")
            txt = [f"Vote for {opSplit[0]}"]
            options = opSplit[1:]
        numb = {
            1: config.emo1,
            2: config.emo2,
            3: config.emo3,
            4: config.emo4,
            5: config.emo5,
            6: config.emo6,
            7: config.emo7,
            8: config.emo8,
            9: config.emo9,
        }
        emo = []
        for idx, element in enumerate(options):
            emo.append(numb[idx + 1])
            txt.append(f"{numb[idx+1]} {element}")
        last = await interaction.send("\n".join(txt))
        last = await last.fetch()
        for element in emo:
            await last.add_reaction(element)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        """Check if message has attachment or link, if 1 add reaction, if not 1 delete and inform user, set/check prize round state, ignore SSCmanager,"""
        configuration = readJSON(filename="config")
        configSSC = configuration["General"]["SSC_Data"]
        configTPF = configuration["TPFGuild"]
        delTime = configuration["General"]["delTime"]
        if ctx.content.startswith(f"{config.BOT_PREFIX}"):
            return
        if ctx.channel.id != configTPF["Channels"]["SSC_Comp"]:
            return
        log.debug("SSC listener")
        if ctx.author.bot:
            if ctx.author.id == config.botID:
                return
            else:
                log.info("A bot did something")
                return
        usrID = str(ctx.author.id)
        sscMan = configTPF["Roles"]["SSC_Manager"]
        if not await blacklistCheck(ctx=ctx, blklstType="ssc"):
            return
        if ctx.author.get_role(sscMan):
            if "upload" in ctx.content:
                await ctx.add_reaction(config.emoStar)
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
        log.debug(cont)
        log.debug(h)
        if len(ctx.attachments) == 0 and h == "n":
            content = f"""Either no image or link detected. Please submit an image.
			\n{delTime}sec *self-destruct*"""
            await ctx.reply(content, delete_after=delTime)
            log.info(f"Deletion_noImg: {ctx.author.id},{ctx.author.display_name}")
            await asyncio.sleep(delTime)
            try:
                await ctx.delete()
            except:
                pass
            return
        if len(ctx.attachments) != 1 and h == "n":
            content = f"""Multiple images detected. Please resubmit one image at a time.
			\n{delTime}sec *self-destruct*"""
            await ctx.reply(content, delete_after=delTime)
            log.info(f"Deletion_multiImg: {ctx.author.id},{ctx.author.display_name}")
            await asyncio.sleep(delTime)
            try:
                await ctx.delete()
            except:
                pass
            return
        sscWin = configTPF["Roles"]["SSC_Winner"]
        sscRun = configTPF["Roles"]["SSC_Runnerup"]
        sscPri = configTPF["Roles"]["SSC_WinnerPrize"]
        if len(ctx.attachments) == 1 or h == "y":
            if configSSC["ignoreWinner"]:
                await ctx.add_reaction(config.emoStar)
                return
            prize = configSSC["isPrize"]
            if prize is True:
                if ctx.author.get_role(int(sscPri)):
                    content = f"""You're a SSC Prize Winner, so can't participate in this round.
					\n{delTime}sec *self-destruct*"""
                    await ctx.reply(content, delete_after=delTime)
                    log.info(
                        f"Deletion_PrizeWinner: {ctx.author.id},{ctx.author.display_name}"
                    )
                    await asyncio.sleep(delTime)
                    try:
                        await ctx.delete()
                    except:
                        pass
                    pass
                else:
                    await ctx.add_reaction(config.emoStar)
                    log.info(
                        f"SubmissionPrize: {ctx.author.id},{ctx.author.display_name}"
                    )
                    return
            elif prize is False:
                if ctx.author.get_role(int(sscWin)) or ctx.author.get_role(int(sscRun)):
                    log.debug("w")
                    content = f"""You're a SSC Winner/Runner Up, so can't participate in this round.
					\n{delTime}sec *self-destruct*"""
                    await ctx.reply(content, delete_after=delTime)
                    log.info(
                        f"Deletion_WinnerRunnerUp: {ctx.author.id},{ctx.author.display_name}"
                    )
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
            log.debug("HUH")


def setup(bot: commands.Bot):
    bot.add_cog(ssc(bot))


# MIT APasz
