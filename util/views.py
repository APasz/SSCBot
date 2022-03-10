print ("UtilViews")
import logging

import config
import nextcord
from nextcord import Interaction

log = logging.getLogger("discordGeneral")


class tpfroles(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.value = None

	async def clicky(self, role, button, interaction):
		if role in interaction.user.roles:
			await interaction.user.remove_roles(role)
			await interaction.response.send_message(f"**{button.label}** role removed!", ephemeral=True)
			log.debug(f"clickyRMV: {interaction.user.id} | {button.label}")
		else:
			await interaction.user.add_roles(role)
			await interaction.response.send_message(f"**{button.label}** role added!", ephemeral=True)
			log.debug(f"clickyADD: {interaction.user.id} | {button.label}")


	@nextcord.ui.button(label = "Modder Intern",
	style = nextcord.ButtonStyle.blurple,
	custom_id="TPF|ROLE|NEWMODDER")
	async def NEWMODDER(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_newModder)
		await self.clicky(role, button, interaction)

	@nextcord.ui.button(label = "TpF Player",
	style = nextcord.ButtonStyle.blurple,
	custom_id="TPF|ROLE|TPFPLAYER")
	async def TPFPLAYER(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_tpfPlayer)
		await self.clicky(role, button, interaction)

	@nextcord.ui.button(label = "CSL Player",
	style = nextcord.ButtonStyle.blurple,
	custom_id="TPF|ROLE|CSLPLAYER")
	async def CSLPLAYER(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_cslPlayer)
		await self.clicky(role, button, interaction)

	@nextcord.ui.button(label = "OpenTTD Player",
	style = nextcord.ButtonStyle.blurple,
	custom_id="TPF|ROLE|TTDPLAYER")
	async def TTDPLAYER(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_ttdPlayer)
		await self.clicky(role, button, interaction)

	@nextcord.ui.button(label = "Factorio Player",
	style = nextcord.ButtonStyle.blurple,
	custom_id="TPF|ROLE|FCTPLAYER")
	async def FCTPLAYER(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_fctPlayer)
		await self.clicky(role, button, interaction)


class nixroles(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.value = None

	async def clicky(self, role, button, interaction):
		if role in interaction.user.roles:
			await interaction.user.remove_roles(role)
			await interaction.response.send_message(f"**{button.label}** role removed!", ephemeral=True)
			log.debug(f"clickyRMV: {interaction.user.id} | {button.label}")
		else:
			await interaction.user.add_roles(role)
			await interaction.response.send_message(f"**{button.label}** role added!", ephemeral=True)
			log.debug(f"clickyADD: {interaction.user.id} | {button.label}")

	@nextcord.ui.button(label = "Linux",
	style = nextcord.ButtonStyle.blurple,
	custom_id="NIX|ROLE|LINUX")
	async def NIXLINUX(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXlinux)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "MacOS",
	style = nextcord.ButtonStyle.blurple,
	custom_id="NIX|ROLE|MACOS")
	async def NIXMACOS(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXmacos)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Windows",
	style = nextcord.ButtonStyle.blurple,
	custom_id="NIX|ROLE|WINDOWS")
	async def NIXWINDOWS(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXwindows)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Aussie",
	style = nextcord.ButtonStyle.blurple,
	custom_id="NIX|ROLE|AUSSIE")
	async def NIXAUSSIE(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXaussie)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Kiwi",
	style = nextcord.ButtonStyle.blurple,
	custom_id="NIX|ROLE|KIWI")
	async def NIXKIWI(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXkiwi)
		await self.clicky(role, button, interaction)


class nixrolesCOL(nextcord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.value = None

	async def clicky(self, role, button, interaction):
		if role in interaction.user.roles:
			await interaction.user.remove_roles(role)
			await interaction.response.send_message(f"**{button.label}** role removed!", ephemeral=True)
			log.debug(f"clickyRMV: {interaction.user.id} | {button.label}")
		else:
			await interaction.user.add_roles(role)
			await interaction.response.send_message(f"**{button.label}** role added!", ephemeral=True)
			log.debug(f"clickyADD: {interaction.user.id} | {button.label}")

	@nextcord.ui.button(label = "Black",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|BLACK")
	async def NIXBLACK(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXblack)
		await self.clicky(role, button, interaction)

	@nextcord.ui.button(label = "Blue",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|BLUE")
	async def NIXBLUE(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXblue)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Dark Blue",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|BLUEDARK")
	async def NIXBLUEDARK(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXblueDark)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Brown",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|BROWN")
	async def NIXBROWN(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXbrown)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Green",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|GREEN")
	async def NIXGREEN(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXgreen)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Dark Green",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|GREENDARK")
	async def NIXGREENDARK(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXgreenDark)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Lilac",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|LILAC")
	async def NIXLILAC(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXlilac)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Orange",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|ORANGE")
	async def NIXORANGE(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXorange)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Pink",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|PINK")
	async def NIXPINK(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXpink)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Dark Red",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|REDDARK")
	async def NIXREDDARK(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXredDark)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "White",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|WHITE")
	async def NIXWHITE(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXwhite)
		await self.clicky(role, button, interaction)
	
	@nextcord.ui.button(label = "Yellow",
	style = nextcord.ButtonStyle.grey,
	custom_id="NIX|ROLE|YELLOW")
	async def NIXYELLOW(self, button:nextcord.ui.Button, interaction):
		role = nextcord.utils.get(interaction.guild.roles, id=config.roles_NIXyellow)
		await self.clicky(role, button, interaction)

#MIT APasz