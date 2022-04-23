print ("CogModding")
import logging
import re
import textwrap
import asyncio

import nextcord
import nextcord.ext

log = logging.getLogger("discordGeneral")

from util.fileUtil import readJSON
from util.genUtil import getCol
from util.apiUtil import parseURL, steamWSGet, steamUsrGet, nexusModGet, tpfnetModGet

configuration = readJSON(filename = "config")
configGen = configuration['General']
configTPF = configuration['TPFGuild']
configNIX = configuration['NIXGuild']
modChans = {
	configTPF['ID']:configTPF['Channels']['NewModPreview'],
	configNIX['ID']:configNIX['Channels']['NewModPreview']
}

async def modPreview(dets, chan, platform, img=None):
		log.debug("modPreview")
		NSFW = False
		auth = None
		authURL = None
		authIcon = None
		desc = None
		createdAt = None
		updatedAt = None
		modThumb = None
		tags = []
		if platform == "steam":
			createdAt = dets['time_created']
			updatedAt = dets['time_updated']
			modName = dets['title']
			auth = dets['personaname']
			authIcon = dets['avatarmedium']
			authURL = dets['profileurl']
			desc = dets['description']
			desc = textwrap.shorten(desc, width=250, placeholder='...')
			markTags = ["[h1]", "[/h1]", "[h2]", "[/h2]", "[b]", "[/b]", "[i]", "[/i]", "[strike]", "[/strike]", "[spoiler]", "[/spoiler]", "[noparse]", "[/noparse]", "[hr]", "[/hr]", "[list]", "[/list]", "[*]", "[code]", "[/code]"]
			for t in markTags:
				desc = desc.replace(t, '')
			desc = f"```\n{desc}\n```"
			modThumb = dets['preview_url']
			url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={dets['publishedfileid']}"
			tagList = dets['tags']
			for t in tagList:
				d = t['tag']
				tags.append(d)
			if tags is not None: tags = ', '.join(tags)
			e = nextcord.Embed(title=f"Workshop Mod Published;\n{modName}",
			colour=getCol('steam'),
			url=url)
				
		elif platform == "nexus":
			createdAt = dets['created_timestamp']
			updatedAt = dets['updated_timestamp']
			modName = dets['name']
			auth = dets['author']
			authIcon = None
			authURL = dets['uploaded_users_profile_url']
			desc = dets['summary']
			tagRM = re.compile(r'<[^>]+>')
			desc = tagRM.sub('', desc)
			desc = f"```\n{desc}\n```"
			modThumb = dets['picture_url']
			url = f"https://www.nexusmods.com/{dets['domain_name']}/mods/{dets['mod_id']}"
			e = nextcord.Embed(title=f"NexusMods Mod Published;\n{modName}",
			colour=getCol('nexusmods'),
			url=url)
			NSFW = dets['contains_adult_content']
			if NSFW is True:
				e.insert_field_at(1, name="NSFW", value="**`TRUE`**", inline=False)
		
		elif platform == "tpfnet":
			modid = dets['ID']
			name = dets['name']
			name = name.replace('-', ' ')
			name = name.removesuffix('/')
			url = f"https://www.transportfever.net/filebase/index.php?entry/{modid}"
			desc = "TpF|Net not currently supported but here is an embed anyway :)"
			e = nextcord.Embed(title=f"TPF|NET Mod Published;\n{name}",
			colour=getCol('tpfnet'),
			url=url)
		
		else:
			e = nextcord.Embed(title="Mod Published",
			colour=getCol('neutral_Light'),
			url=None)
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
		print(type(img))
		if img is not None:
			ty = str(type(img))
			if "Attach" in ty:
				e.set_image(url=img.url)
			elif "str" in ty:
				e.set_image(url=img)
		await chan.send(embed = e)



async def modRelease(ctx, chan):
	if len(ctx.attachments) != 0:
		attach = ctx.attachments[0]
		if attach.content_type.startswith("image"): img = attach
	else: img = None
	cont = ctx.content
	mess = cont.split("\n")
	for l in mess:
		#print(f"L: {l}")
		if re.search(r'https:', l):
			#l = l.replace(' ','')
			urlDic = parseURL(l)
			ID = urlDic['ID']
			game = urlDic['game']
			plat = urlDic['platform']
			err = "There was an error. "
			if plat == "steam":
				dets = steamWSGet(ID)
				if isinstance(dets, int):
					err = err+str(dets)
					log.error(f"steamWS | {dets}")
					await ctx.channel.send(err)
					return
				usrID = int(dets['creator'])
				author = steamUsrGet(usrID)
				if isinstance(author, int):
					err = err+str(author)
					log.error(f"steamUsr | {dets}")
					await ctx.channel.send(err)
					return
				dets = dets | author
				await modPreview(dets=dets, chan=chan, platform=plat, img=img)
			if plat == "nexus":
				dets = nexusModGet(game, ID)
				if isinstance(dets, int):
					err = err+str(dets)
					log.error(f"nexus | {dets}")
					await ctx.channel.send(err)
					return
				await modPreview(dets=dets, chan=chan, platform=plat, img=img)
			if plat == "tpfnet": #not supported at present.
				if not re.search(r'filebase', cont): continue
				dets = tpfnetModGet(ID)
				# if isinstance(dets, int):
				# 	err = err+str(dets)
				# 	log.error(f"tpfnet | {dets}")
				# 	await ctx.channel.send(err)
				# 	return
				dets = {
					'ID':ID,
					'name':game
				}
				await modPreview(dets=dets, chan=chan, platform=plat, img=img)
			await asyncio.sleep(0.1)
	print("NMR Done")



#MIT APasz
