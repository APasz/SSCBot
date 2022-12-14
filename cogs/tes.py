try:
    import asyncio
    import logging
    from pprint import pprint
    import requests

    import gspread
    import nextcord
    import pint
    from config import dataObject
    from config import genericConfig as gxConfig
    from discord import Attachment
    from nextcord import (
        Embed,
        Interaction,
        Member,
        SlashOption,
        slash_command,
        user_command,
        Emoji,
        PartialEmoji,
    )
    from nextcord.ext import application_checks, commands
    from util.fileUtil import cacheWrite, parentDir, readJSON, writeJSON
    from util.genUtil import hasRole, sortReactions

    # import modding
except Exception:
    print(f"TesLoad")

print("CogTES")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
# from cogs.auditLog import *

hashes = {}
# , value:int, fromunit:str, tounit:str


txt0 = "Nothing"
txt1 = "Aa"
txt2 = "Bb"
txt3 = "Cc"
txt4 = "Dd"


def sscCheck(chan):
    ssc = readJSON(filename="config.json")["TPFGuild"]["Channels"]["SSC_Comp"]
    return ssc == chan


def sscusrCheck(usr):
    return usr == gxConfig.botID


def checkrole(interaction: Interaction):
    configTPF = readJSON(filename="config")["TPFGuild"]["Roles"]
    roly = interaction.guild.get_role(int(configTPF["SSC_Manager"]))
    return hasRole(role=roly, roles=interaction.user.roles)


class mod(nextcord.ui.Modal):
    "tesMod"

    def __init__(self, title="futanari"):
        super().__init__(title)

        self.input = nextcord.ui.TextInput(label="input")
        self.add_item(self.input)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.send(f"Sending The Fucking Data!")
        self.stop()


def getWS(wsID) -> int | dict:
    log.debug("WSsteam")
    # params = {"itemcount": 1, "publishedfileids[0]": wsID}
    url = "https://api.steampowered.com/IPublishedFileService/GetDetails/v1/"
    url1 = [
        "https://api.steampowered.com/IPublishedFileService/GetDetails/v1/",
        "?key=83F844AE7FE7451511E77E989C6DE102",
        f"&publishedfileids[0]={wsID}",
        "?language=french",
    ]
    params = {
        "key": "83F844AE7FE7451511E77E989C6DE102",
        "language": 1,
        "publishedfileids[0]": wsID,
    }
    # "&strip_description_bbcode=true",
    try:
        res = requests.get(url=url, params=params)
    except Exception:
        log.exception(f"steamWSGet | {res.status_code=}")
    log.info(f"steamWSGet | {res.status_code=}")
    if res:
        data = res.json()
        writeJSON(data, "steam")
        return data["response"]["publishedfiledetails"][0]
    else:
        return res.status_code


def WSGet(wsID) -> int | dict:
    log.debug("steamWS")
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
    params = {"itemcount": 1, "publishedfileids[0]": wsID}
    try:
        res = requests.post(url, data=params)
    except Exception:
        log.exception(f"steamWSGet | {res.status_code=}")
    log.info(f"steamWSGet | {res.status_code=}")
    if res:
        data = res.json()
        writeJSON(data, "steam")
        return data["response"]["publishedfiledetails"][0]
    else:
        return res.status_code


class tes(commands.Cog, name="TES"):
    def __init__(self, bot):
        self.bot = bot
        self.name = "AName"

    @commands.command(name="s", hidden=True)
    @commands.is_owner()
    async def s(self, ctx: commands.Context):  # , ID: int
        print("Sierra")
        # print(ID, type(ID))
        # getWS(ID)
        import modding

        k = modding.mods.mr()

        print(k)

    @slash_command(name="x", guild_ids=gxConfig.slashServers)
    # @application_checks.check(checkrole)
    async def x(
        self,
        interaction: Interaction,
        messageID=SlashOption(
            name="template-message-id",
            required=True,
            description="Which message to use as the template",
        ),
    ):
        print("xulu", messageID)
        try:
            mess = await interaction.channel.fetch_message(int(messageID))
        except nextcord.NotFound:
            logSys.exception(f"Message Not Found")
            await interaction.send("Message Not Found")
        except nextcord.Forbidden:
            logSys.exception("Message Forbidden")
            await interaction.send("Message Not Accessible")
        except Exception:
            logSys.exception(f"Fetch Message Channel")
        messCont = (mess.content).split(" ")
        messReac = mess.reactions
        if len(messReac) == 0:
            await interaction.send(f"This message does have any reactions")

        reactsAll = sortReactions(messReac)
        reacts = reactsAll.Obj + reactsAll.Str
        reactsBad = reactsAll.Bad
        reactsUnk = reactsAll.Unk

        # if item.is_custom_emoji():
        #    print("emoCusName", item.emoji.name)
        #    print("emoCusID", item.emoji.id)
        #    if hasattr(item.emoji, "is_unicode_emoji"):
        #        print("emoCusUni", item.emoji.is_unicode_emoji())
        #    if hasattr(item.emoji, "is_usable"):
        #        print("emoCusUse", item.emoji.is_usable())
        #        if item.emoji.is_usable():
        #            reacts.append(
        #                [str(item.emoji.name), int(item.emoji.id)])
        # else:
        #    print("emo", item.emoji)
        #    reacts.append(item.emoji)

        # print("emoUse", item.emoji.is_usable)
        # pe = item.emoji.from_str()
        # print("pe", pe)
        # reacts.append(str(item.emoji))
        # reac = isCustomEmoji(conx, item.emoji.id)
        # if isinstance(reac, str):
        #    reacts.append(item)
        # elif isinstance(reac, [nextcord.Emoji, nextcord.PartialEmoji]):
        #    reacts.append(item)

        txt = []
        if len(reactsBad) == 0 and len(reactsUnk) == 0:
            txt.append("AutoReact Updating! Check auditlog for details.")
        await interaction.send(f"{messCont=}\n{reacts=}\n{reactsBad=}\n{reactsUnk=}")

        # print(interaction.guild_locale)
        # print(interaction.locale)
        # reactorDict = {
        #    "Channel": [3],
        #    "Contains": ["hi"],
        #    "Emoji": ["👋"],
        #    "isExactMatch": False
        # }
        # reactModal = reactorModal(
        #    reactor="reactor", reactorDict=reactorDict)
        # await interaction.response.send_modal(reactModal)
        # log.debug("AutoReact Config Modal Sent")
        # await reactModal.wait()
        # emoji = reactModal.emojiText.value
        # print("emoji", type(emoji), emoji)
        # emoList = emoji.split(' ')

        # class conx():
        #    guild = interaction.guild

        #    class bot():
        #        emojis = self.bot.emojis

        # pprint(conx.__dict__)
        # pprint(conx.bot.__dict__)
        # for item in emoList:
        #    print("item", item)
        #    convEmo = await isCustomEmoji(conx, item)
        #    print("convEmo", convEmo)
        #    print()

        # modal = mod()
        # await interaction.response.send_modal(modal=modal)
        # await modal.wait()
        # op = (modal.input.value).split(' ')
        # for item in op:
        #    if len(item) > 0:
        #        k = isEmojiCustom(item, interaction.guild.emojis)
        #        print("K", type(k), k)

        # data = "Not"
        # data = GSheetGet()
        # themesList = data.get("A5:B")
        # themesDic = {}
        # for element in themesList:
        #    if len(element) == 1:
        #        themesDic[element[0]] = None
        #    else:
        #        themesDic[element[0]] = element[1]
        # conf = readJSON(filename="config")
        # if conf["General"]["SSC_Data"]["allThemes"] != themesDic:
        #    conf["General"]["SSC_Data"]["allThemes"] = themesDic
        #    writeJSON(data=conf, filename="config")
        # await interaction.response.send_message(f"{str(next(iter(themesDic)))}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("tesReady")
        log.debug(f"{self.__cog_name__} Ready")

    # @slash_command(guild_ids=gxConfig.slashServers)
    # async def alpha(self, interaction: Interaction, st:str):
    # 	await interaction.response.send_message(f"Alpha: {st}")

    @commands.command(name="b", hidden=True)
    @commands.is_owner()
    async def b(self, ctx: commands.Context, *k2):
        print("Bravo")
        print(type(k2), len(k2))

        # data = readJSON(filename="changelog")
        # ver = list(data.keys())[-1]
        # print(ver)
        # verName = str(list(data[f"{ver}"])[0])
        # print(verName)
        # await ctx.send(f"{ver} | {verName}")

    @commands.command(name="a", hidden=True)
    @commands.is_owner()
    async def a(self, ctx: commands.Context, op=None):
        print("Alpha")
        ver = "2.2.1"
        changelog = readJSON(filename="changelog")
        version = changelog[ver][0]
        print(version)
        changeList = changelog[ver][1:]
        txt = "Undefinded"

        def chunkList(maxChars: int, txtList: list):
            logLength = 0
            entryList = []
            for i, item in enumerate(txtList):
                logLength += len(item)
                if logLength <= maxChars:
                    entryList.append(i)
                else:
                    yield entryList
                    entryList = [i]
                    logLength = len(item)
            yield (entryList)

        chunks = list(chunkList(maxChars=2000, txtList=changeList))
        for item in chunks:
            eles = [changeList[i] for i in item]
            txt = "\n".join(eles)
            await ctx.send(txt)

        # for item in chunks:
        # 	print(item)
        # 	first = int(chunks.index(0))
        # 	last = int(chunks.index(-1))
        # 	print("F,L", first, last)
        # 	for element in chunks[int(item)]:
        # 		print("E", element)
        # 		txt = '\n'.join(changeList)[first:last]
        # 	await ctx.send(txt)

        # print(type(txt))
        # print(txt)

        # while True:
        # 	print("While")
        # 	logLength = 0
        # 	entryList = []
        # 	for line in changeList:
        # 		lineLength = len(str(line))
        # 		logLength = logLength + lineLength
        # 		print(logLength, lineLength, line)
        # 		if logLength > 2000:
        # 			txtList = entryList
        # 			entryList = []
        # 			logLength = 0
        # 			continue
        # 		else:
        # 			print("else")
        # 			entryList.append(line)
        # 			changeList.remove(line)
        # 	txt = '\n'.join(txtList)
        # 	print("Text: ", txt)
        # 	print()
        # 	if len(changeList) == 0:
        # 		print("**Break**")
        # 		break

        # for line in changeList:
        # 	lineLength = len(str(line))
        # 	print(logLength, lineLength)
        # 	logLength = logLength + lineLength
        # 	if logLength < 2000:
        # 		entryList.append(line)
        # 		continue
        # 	txt = '\n'.join(entryList)
        # 	await ctx.send(f"{ver}\n{txt}")
        # 	entryList = []
        # return

        # print(len(txt))

    # @commands.Cog.listener()
    # async def on_message(self, ctx):
    # 	if not sscCheck(ctx.channel.id): return
    # 	if ctx.author.bot: return
    # 	print(ctx.author.id)
    # 	from util.views import sscVote
    # 	view = sscVote()
    # 	await ctx.send(f"{ctx.id}", ephemeral=True)

    # @commands.command(name="d", hidden=True)
    # @commands.is_owner()
    # async def d(self, ctx: commands.Context):
    #    print("Delta1")
    #    res = await ctx.send("Config Please")
    #    # chan = ctx.channel

    #    def check(m):
    #        if (
    #            m.author == ctx.author
    #            and m.channel == ctx.channel
    #            and len(m.attachments) == 1
    #        ):
    #            return True

    #    try:
    #        mess = await self.bot.wait_for("message", check=check, timeout=30.0)
    #    except asyncio.TimeoutError:
    #        await res.edit(content="timeout")
    #        print("timeout")
    #        return
    #    att = mess.attachments
    #    print(len(att))
    #    print(att[0].filename)
    #    print(att[0].content_type)
    #    await res.edit(content="recieved")
    #    # await ctx.send(delta)
    #    print("Delta2")

    # @commands.Cog.listener()
    # async def on_message(self, ctx):
    # 	if ctx.channel.id not in config.chan_TpFssc: return
    # 	if len(ctx.attachments) != 0:
    # 		has = hash(ctx.attachments[0])
    # 		now = int(time.time())
    # 		hashes[f"{has}"] = now
    # 		await ctx.reply(hashes)

    # @commands.Cog.listener()
    # async def on_message(self, ctx):
    # 	stdoutChans = [config.chan_TpFtpf1, config.chan_TpFtpf2, config.chan_TpFgen\
    # config.chan_NIXtpf, config.chan_NIXgen]
    # 	if ctx.channel.id not in stdoutChans: return
    # 	if not ctx.attachments: return
    # 	attach = ctx.attachments[0]
    # 	if not attach.filename.endswith('txt'): return
    # 	log.debug("stdoutChecking")
    # 	filename = f"/tmp/{attach.filename}"
    # 	await attach.save(filename)
    # 	print(filename)
    # 	while True:
    # 		await asyncio.sleep(0.1)
    # 		if os.path.exists(filename): break
    # 		else: pass
    # 	gameVer = platform = driverVer = None
    # 	with open(filename, 'r') as file:
    # 		for line in file:
    # 			line = line.lower()

    # 			if re.search(r'build: build', line):
    # 				split = line.split(' ')
    # 				for e in split:
    # 					if e.isdigit():
    # 						gameVer = e
    # 					elif ("b" not in e.lower()) and not (any(char.isdigit() for char in e)):
    # 						platform = e

    # 			if re.search(r'crashdb_renderer', line):
    # 				if "nvidia" in line:
    # 					if "opengl" in line:
    # 						pass

    # 				if "opengl" in line:
    # 					if "nvidia" in line:
    # 						splits = line.split("nvidia")
    # 						for s in splits:
    # 							s = s.replace(' ', '')
    # 							if s[0].isdigit():
    # 								driverVer = s[0:3].removesuffix('.') #Just in case of 4 digit version
    # 					if "amd" in line:
    # 						pass
    # 				elif "vulkan" in line:
    # 					if "nvidia" in line:
    # 						splits = line.split("|")
    # 						#pprint(splits)
    # 						for s in splits:
    # 							if s[1].isdigit():
    # 								driverVer = s[0:3].removesuffix('.')
    # 								break
    # 					elif "amd" in line:
    # 						pass
    # 	print(f"{gameVer}\n{platform}\n{driverVer}")


def setup(bot: commands.Bot):
    bot.add_cog(tes(bot))


# @bot.check
# async def noRepeatedPrefix(ctx):
# 	if ctx.message.content.startswith(f"{config.BOT_PREFIX}{config.BOT_PREFIX}"): return

{
    "Micrometre": "micrometre",
    "Millimetre": "millimetre",
    "Centimetre": "centimetre",
    "Metre": "metre",
    "Kilometre": "kilometre",
    "Microgram": "microgram",
    "Miligram": "miligram",
    "Gram": "gram",
    "Kilogram": "kilogram",
    "Tonne": "tonne",
    "Inch": "inch",
    "Feet": "feet",
    "Yard": "yard",
    "Mile": "mile",
    "Teaspoon": "teaspoon",
    "Tablespoon": "tablespoon",
    "Fluid ounce": "fluid ounce",
    "Cup": "cup",
    "Pint": "pint",
    "Quart": "quart",
    "Gallon": "gallon",
    "Ounce": "ounce",
    "Pound": "pound",
    "Ton": "ton",
    "Seconds": "seconds",
    "Minute": "minute",
    "Hour": "hour",
    "Day": "day",
    "Week": "week",
    "Year": "year",
    "Not listed?": "NL",
}
