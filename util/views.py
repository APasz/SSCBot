print ("UtilViews")
import logging

import config
import nextcord
from nextcord import Interaction

log = logging.getLogger("discordGeneral")

from util.fileUtil import readJSON
from util.genUtil import hasRole

configuration = readJSON(filename = "config")
configTPF = configuration['TPFGuild']['Roles']
configNIX = configuration['NIXGuild']['Roles']


async def clicky(role:nextcord.Role, button:nextcord.ui.Button, interaction:Interaction, action="both"):
		Rtxt = "*undefinded*"
		async def add():
			await interaction.user.add_roles(role)
			txt = "role added!"
			log.debug(f"clickyADD: {interaction.user.id} | {button.label}")
			return txt
		async def remove():
			await interaction.user.remove_roles(role)
			txt = "role removed!"
			log.debug(f"clickyRMV: {interaction.user.id} | {button.label}")
			return txt
		roly = hasRole(role=role, roles=interaction.user.roles)
		if roly:
			if action == "add": Rtxt = "role can not be removed."
			else: Rtxt = await remove()
		else:
			if action == "remove": Rtxt = "role can not be added."
			else: Rtxt = await add()
		Etxt = f"**{button.label}** {Rtxt}"
		await interaction.response.send_message(Etxt, ephemeral=True)

class tpfroles(nextcord.ui.View):
	
	def __init__(self):
		super().__init__(timeout=None)
		self.value = None
	
	@nextcord.ui.button(label = "Verified",
	style = nextcord.ButtonStyle.blurple,
	custom_id="TPF|ROLE|VERIFIED")
	async def TPFVERIFIED(self, button:nextcord.ui.Button, interaction):
		role = interaction.guild.get_role(configTPF['Verified'])
		await clicky(role, button, interaction, "add")

	@nextcord.ui.button(label = "Modder Intern",
	style = nextcord.ButtonStyle.blurple,
	custom_id="TPF|ROLE|NEWMODDER")
	async def NEWMODDER(self, button:nextcord.ui.Button, interaction):
		role = interaction.guild.get_role(configTPF['ModderNew'])
		await clicky(role, button, interaction)

	@nextcord.ui.button(label = "TpF Player",
	style = nextcord.ButtonStyle.blurple,
	custom_id="TPF|ROLE|TPFPLAYER")
	async def TPFPLAYER(self, button:nextcord.ui.Button, interaction):
		role = interaction.guild.get_role(configTPF['Player_TPF'])
		await clicky(role, button, interaction)

	@nextcord.ui.button(label = "CSL Player",
	style = nextcord.ButtonStyle.blurple,
	custom_id="TPF|ROLE|CSLPLAYER")
	async def CSLPLAYER(self, button:nextcord.ui.Button, interaction):
		role = interaction.guild.get_role(configTPF['Player_CSL'])
		await clicky(role, button, interaction)

	@nextcord.ui.button(label = "OpenTTD Player",
	style = nextcord.ButtonStyle.blurple,
	custom_id="TPF|ROLE|TTDPLAYER")
	async def TTDPLAYER(self, button:nextcord.ui.Button, interaction):
		role = interaction.guild.get_role(configTPF['Player_TTD'])
		await clicky(role, button, interaction)

	@nextcord.ui.button(label = "Factorio Player",
	style = nextcord.ButtonStyle.blurple,
	custom_id="TPF|ROLE|FCTPLAYER")
	async def FCTPLAYER(self, button:nextcord.ui.Button, interaction):
		role = interaction.guild.get_role(configTPF['Player_FCT'])
		await clicky(role, button, interaction)


class nixroles(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.value = None
	
	@nextcord.ui.button(label = "Linux",
	style = nextcord.ButtonStyle.blurple,
	custom_id="NIX|ROLE|LINUX")
	async def NIXLINUX(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['Linux'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "MacOS",
	style = nextcord.ButtonStyle.blurple,
	custom_id="NIX|ROLE|MACOS")
	async def NIXMACOS(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['MacOS'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Windows",
	style = nextcord.ButtonStyle.blurple,
	custom_id="NIX|ROLE|WINDOWS")
	async def NIXWINDOWS(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['Windows'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Aussie",
	style = nextcord.ButtonStyle.blurple,
	custom_id="NIX|ROLE|AUSSIE")
	async def NIXAUSSIE(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['AUS'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Kiwi",
	style = nextcord.ButtonStyle.blurple,
	custom_id="NIX|ROLE|KIWI")
	async def NIXKIWI(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['NZ'])
		await clicky(role, button, interaction)


class nixrolesCOL(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.value = None

	@nextcord.ui.button(label = "Black",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|BLACK")
	async def NIXBLACK(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['COL_black'])
		await clicky(role, button, interaction)

	@nextcord.ui.button(label = "Blue",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|BLUE")
	async def NIXBLUE(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['COL_blue'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Dark Blue",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|BLUEDARK")
	async def NIXBLUEDARK(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['COL_blueDark'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Brown",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|BROWN")
	async def NIXBROWN(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['COL_brown'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Green",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|GREEN")
	async def NIXGREEN(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['COL_green'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Dark Green",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|GREENDARK")
	async def NIXGREENDARK(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['COL_greenDark'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Lilac",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|LILAC")
	async def NIXLILAC(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['COL_lilac'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Orange",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|ORANGE")
	async def NIXORANGE(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['COL_orange'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Pink",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|PINK")
	async def NIXPINK(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['COL_pink'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Dark Red",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|REDDARK")
	async def NIXREDDARK(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['COL_redDark'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "White",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|WHITE")
	async def NIXWHITE(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['COL_white'])
		await clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Yellow",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|YELLOW")
	async def NIXYELLOW(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=configNIX['COL_yellow'])
		await clicky(role, button, interaction)

#MIT APasz
