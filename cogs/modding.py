import asyncio
import logging
import re
import textwrap

from config import generalEventConfig as geConfig
from util.apiUtil import nexusModGet, parseURL, steamUsrGet, steamWSGet, tpfnetModGet
from util.genUtil import getChan, getCol

print("CogModding")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY MODDING IMPORT MODULES")
    import nextcord
    from nextcord.ext import commands
except Exception:
    logSys.exception("MODDING IMPORT MODULES")


class modding(commands.Cog, name="Modding"):
    """Class containing commands and functions related to game modding"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        tpfID = geConfig.guildListName["TPFGuild"]
        self.globalPreviewChan = getChan(guild=tpfID, chan="NewModPreview")

    @commands.Cog.listener()
    async def on_ready(self):
        logSys.debug(f"{self.__cog_name__} Ready")

    async def modPreview(
        self,
        dets,
        chan,
        platform,
        img=None,
        globalPreview: bool = False,
    ):
        """Create a mod preview embed and send it to the appropriate channel"""
        log.debug("modPreview")
        NSFW = False
        auth = authURL = authIcon = desc = createdAt = updatedAt = modThumb = None
        tags = []
        if platform == "steam":
            createdAt = dets["time_created"]
            updatedAt = dets["time_updated"]
            modName = dets["title"]
            auth = dets["personaname"]
            authIcon = dets["avatarmedium"]
            authURL = dets["profileurl"]
            desc = dets["description"]
            desc = textwrap.shorten(desc, width=400, placeholder="...")
            markTags = [
                "[h1]",
                "[/h1]",
                "[h2]",
                "[/h2]",
                "[b]",
                "[/b]",
                "[i]",
                "[/i]",
                "[strike]",
                "[/strike]",
                "[spoiler]",
                "[/spoiler]",
                "[noparse]",
                "[/noparse]",
                "[hr]",
                "[/hr]",
                "[list]",
                "[/list]",
                "[*]",
                "[code]",
                "[/code]",
            ]
            for t in markTags:
                desc = desc.replace(t, "")
            desc = f"```\n{desc}\n```"
            modThumb = dets["preview_url"]
            url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={dets['publishedfileid']}"
            tagList = dets["tags"]
            for t in tagList:
                d = t["tag"]
                tags.append(d)
            if tags is not None:
                tags = ", ".join(tags)
            e = nextcord.Embed(
                title=f"Workshop Mod Published;\n{modName}",
                colour=getCol("steam"),
                url=url,
            )

        elif platform == "nexus":
            createdAt = dets["created_timestamp"]
            updatedAt = dets["updated_timestamp"]
            modName = dets["name"]
            auth = dets["author"]
            authIcon = None
            authURL = dets["uploaded_users_profile_url"]
            desc = dets["summary"]
            tagRM = re.compile(r"<[^>]+>")
            desc = tagRM.sub("", desc)
            desc = f"```\n{desc}\n```"
            modThumb = dets["picture_url"]
            url = (
                f"https://www.nexusmods.com/{dets['domain_name']}/mods/{dets['mod_id']}"
            )
            e = nextcord.Embed(
                title=f"NexusMods Mod Published;\n{modName}",
                colour=getCol("nexusmods"),
                url=url,
            )
            NSFW = dets["contains_adult_content"]
            if NSFW is True:
                e.insert_field_at(1, name="NSFW", value="**`TRUE`**", inline=False)

        elif platform == "tpfnet":
            modid = dets["ID"]
            name = dets["name"]
            name = name.replace("-", " ")
            name = name.removesuffix("/")
            url = f"https://www.transportfever.net/filebase/index.php?entry/{modid}"
            desc = "TpF|Net not currently supported but here is an embed anyway :)"
            e = nextcord.Embed(
                title=f"TPF|NET Mod Published;\n{name}",
                colour=getCol("tpfnet"),
                url=url,
            )

        else:
            e = nextcord.Embed(
                title="Mod Published", colour=getCol("neutral_Light"), url=None
            )
        if auth and authURL and authIcon:
            e.set_author(name=auth, url=authURL, icon_url=authIcon)
        elif (auth and authURL) and not authIcon:
            e.set_author(name=auth, url=authURL)
        elif auth and not (authURL or authIcon):
            e.set_author(name=auth)
        if desc is not None:
            e.add_field(name="Description", value=desc, inline=False)
        if createdAt is not None:
            e.add_field(name="Published", value=f"<t:{createdAt}:R>", inline=True)
            if not createdAt <= updatedAt <= (createdAt + 3600):
                e.add_field(name="Updated", value=f"<t:{updatedAt}:R>", inline=True)
        if len(tags) != 0:
            e.add_field(name="Tags", value=tags, inline=False)
        if modThumb is not None:
            e.set_image(url=modThumb)
        if NSFW is True:
            e.set_image(url=())
        log.debug(f"img type: {type(img)}")
        if img is not None:
            ty = str(type(img))
            if "Attach" in ty:
                e.set_image(url=img.url)
            elif "str" in ty:
                e.set_image(url=img)
        try:
            await chan.send(embed=e)
        except Exception:
            log.exception("Mod Preview")
        else:
            log.debug(f"Mod Preview Sent {globalPreview=}")
        if globalPreview is True:
            try:
                globalPreviewChan = getChan(
                    guild=geConfig.guildListName["TPFGuild"], chan="NewModPreview"
                )
                gnmp = await self.bot.fetch_channel(int(globalPreviewChan))
                await gnmp.send(embed=e)
            except Exception:
                log.exception("Global Mod Preview")
                return
            log.debug("Global Mod Preview Sent")

    async def modRelease(
        self,
        ctx,
        chan,
        globalPreview: bool = False,
    ):
        """Parse URLs from the new mod release channels and gather the required info to pass to modPreview"""
        if len(ctx.attachments) != 0:
            attach = ctx.attachments[0]
            if attach.content_type.startswith("image"):
                img = attach
        else:
            img = None
        cont = ctx.content
        cont = cont.replace("\n", " ")
        mess = cont.split(" ")
        for M in mess:
            # print(f"L: {l}")
            if re.search(r"https:", M):
                # l = l.replace(' ','')
                urlDic = parseURL(M)
                ID = urlDic["ID"]
                game = urlDic["game"]
                plat = urlDic["platform"]
                err = "There was an error. "
                if plat == "steam":
                    dets = steamWSGet(ID)
                    if isinstance(dets, int):
                        err = err + str(dets)
                        log.error(f"steamWS | {dets}")
                        try:
                            await ctx.channel.send(err)
                        except Exception:
                            log.exception(f"MR ERR Steam WS")
                        return
                    usrID = int(dets["creator"])
                    author = steamUsrGet(usrID)
                    if isinstance(author, int):
                        err = err + str(author)
                        log.error(f"steamUsr | {dets}")
                        try:
                            await ctx.channel.send(err)
                        except Exception:
                            log.exception(f"MR ERR Steam Usr")
                        return
                    dets = dets | author
                    try:
                        await modding.modPreview(
                            self=self,
                            dets=dets,
                            chan=chan,
                            platform=plat,
                            img=img,
                            globalPreview=globalPreview,
                        )
                    except Exception:
                        log.exception(f"MR MP Send Steam")
                if plat == "nexus":
                    dets = nexusModGet(game, ID)
                    if isinstance(dets, int):
                        err = err + str(dets)
                        log.error(f"nexus | {dets}")
                        try:
                            await ctx.channel.send(err)
                        except Exception:
                            log.exception(f"MR ERR Nexus")
                        return
                    try:
                        await modding.modPreview(
                            dets=dets,
                            chan=chan,
                            platform=plat,
                            img=img,
                            globalPreview=globalPreview,
                        )
                    except Exception:
                        log.exception(f"MR MP Send nexus")
                if plat == "tpfnet":  # not supported at present.
                    if not re.search(r"filebase", cont):
                        continue
                    dets = tpfnetModGet(ID)
                    # if isinstance(dets, int):
                    #    err = err+str(dets)
                    #    log.error(f"tpfnet | {dets}")
                    #    try:
                    #      await ctx.channel.send(err)
                    #    except Exception:
                    #        log.exception(f"MR ERR TpF")
                    #    return
                    dets = {"ID": ID, "name": game}
                    try:
                        await modding.modPreview(
                            dets=dets,
                            chan=chan,
                            platform=plat,
                            img=img,
                            globalPreview=globalPreview,
                        )
                    except Exception:
                        log.exception(f"MR MP Send TpF")
                    log.debug("ModPreviewSent")
                await asyncio.sleep(0.1)
        print("NMR Done")


def setup(bot: commands.Bot):
    bot.add_cog(modding(bot))


# MIT APasz
