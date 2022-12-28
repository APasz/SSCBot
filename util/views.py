import inspect
import logging
import time

print("UtilViews")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY VIEWS IMPORT MODULES")
    import nextcord
    from nextcord import Interaction

    from config import generalEventConfig as geConfig
    from config import genericConfig as gxConfig
    from util.fileUtil import paths, readJSON, writeJSON
    from util.genUtil import getServConf, hasRole, setUserConf
except Exception:
    logSys.exception("VIEWS IMPORT MODULES")


async def clicky(
    role: nextcord.Role,
    button: nextcord.ui.Button,
    interaction: Interaction,
    action="both",
) -> None:
    """Do the role action=(add|remove)"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {role.id=} {role.name=} | {action=}")
    Rtxt = "*undefinded*"

    async def add():
        """Actually add the role"""
        await interaction.user.add_roles(role)
        txt = "role added!"
        logSys.debug(f"clickyADD: {interaction.user.id=} | {button.label=}")
        return txt

    async def remove():
        """Actually remove the role"""
        await interaction.user.remove_roles(role)
        txt = "role removed!"
        logSys.debug(f"clickyRMV: {interaction.user.id=} | {button.label=}")
        return txt

    roly = hasRole(role=role, userRoles=interaction.user.roles)
    mod = False
    if roly:
        if action == "add":
            Rtxt = "role can not be removed."
        else:
            Rtxt = await remove()
            mod = 0
    else:
        if action == "remove":
            Rtxt = "role can not be added."
        else:
            Rtxt = await add()
            mod = 1
    Etxt = f"**{button.label}** {Rtxt}"
    await interaction.response.send_message(Etxt, ephemeral=True)
    return mod


def _getRole(guildID: int | str, roleName: str):
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {guildID=} | {roleName=}")
    return int(getServConf(guildID, group="Roles", option=roleName))


tpfID = int(geConfig.guildListName["TPFGuild"])
nixID = int(geConfig.guildListName["NIXGuild"])


class tpfroles(nextcord.ui.View):
    """Buttons for assign roles in the global server"""

    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @nextcord.ui.button(
        label="Verified",
        style=nextcord.ButtonStyle.green,
        custom_id="TPF|ROLE|VERIFIED",
    )
    async def TPFVERIFIED(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Verified role, and remove Unverified role."""
        role = interaction.guild.get_role(_getRole(tpfID, "Verified"))
        await clicky(role, button, interaction, "add")
        role = interaction.guild.get_role(_getRole(tpfID, "Unverified"))
        await clicky(role, button, interaction, "remove")

    @nextcord.ui.button(
        label="Modder Intern",
        style=nextcord.ButtonStyle.blurple,
        custom_id="TPF|ROLE|NEWMODDER",
    )
    async def NEWMODDER(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Modder Intern role"""
        role = interaction.guild.get_role(_getRole(tpfID, "ModderNew"))
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="TpF Player",
        style=nextcord.ButtonStyle.blurple,
        custom_id="TPF|ROLE|TPFPLAYER",
    )
    async def TPFPLAYER(self, button: nextcord.ui.Button, interaction):
        """Add/remove the TpF Player role"""
        role = interaction.guild.get_role(_getRole(tpfID, "Player_TPF"))
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="CSL Player",
        style=nextcord.ButtonStyle.blurple,
        custom_id="TPF|ROLE|CSLPLAYER",
    )
    async def CSLPLAYER(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Cities: Skylines Player role"""
        role = interaction.guild.get_role(_getRole(tpfID, "Player_CSL"))
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="OpenTTD Player",
        style=nextcord.ButtonStyle.blurple,
        custom_id="TPF|ROLE|TTDPLAYER",
    )
    async def TTDPLAYER(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Transport Tycoon Player role"""
        role = interaction.guild.get_role(_getRole(tpfID, "Player_TTD"))
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Factorio Player",
        style=nextcord.ButtonStyle.blurple,
        custom_id="TPF|ROLE|FCTPLAYER",
    )
    async def FCTPLAYER(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Factorio Player role"""
        role = interaction.guild.get_role(_getRole(tpfID, "Player_FCT"))
        await clicky(role, button, interaction)


class sscroles(nextcord.ui.View):
    """Buttons for assign roles for ssc"""

    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    def updateConf(userID: int, role: str):
        "If user not in config,"

    @nextcord.ui.button(
        label="General Noification",
        style=nextcord.ButtonStyle.blurple,
        custom_id="SSC|ROLE|NOTIFIY_GENERAL",
    )
    async def SSCNOTIFY(self, button: nextcord.ui.Button, interaction: Interaction):
        """Add/remove the SSC Notify role"""
        role = interaction.guild.get_role(_getRole(tpfID, "SSC_Notify_General"))
        mod = await clicky(role, button, interaction)
        logSys.debug(f"{mod=}")
        if mod == 0:
            setUserConf(
                userID=interaction.user.id, option="SSC_Notify_General", value=False
            )
        elif mod == 1:
            setUserConf(
                userID=interaction.user.id, option="SSC_Notify_General", value=True
            )

    @nextcord.ui.button(
        label="Prize Noification",
        style=nextcord.ButtonStyle.blurple,
        custom_id="SSC|ROLE|NOTIFIY_PRIZE",
    )
    async def SSCNOTIFYPRIZE(
        self, button: nextcord.ui.Button, interaction: Interaction
    ):
        """Add/remove the SSC Notify Prize role"""
        role = interaction.guild.get_role(_getRole(tpfID, "SSC_Notify_Prize"))
        mod = await clicky(role, button, interaction)
        logSys.debug(f"{mod=}")
        if mod == 0:
            setUserConf(
                userID=interaction.user.id, option="SSC_Notify_Prize", value=False
            )
        elif mod == 1:
            setUserConf(
                userID=interaction.user.id, option="SSC_Notify_Prize", value=True
            )


class nixroles(nextcord.ui.View):
    """Buttons for assign non-colour roles in the NIX server"""

    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @nextcord.ui.button(
        label="Linux", style=nextcord.ButtonStyle.blurple, custom_id="NIX|ROLE|LINUX"
    )
    async def NIXLINUX(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Linux role"""
        role = nextcord.utils.get(interaction.guild.roles, id=_getRole(nixID, "Linux"))
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="MacOS", style=nextcord.ButtonStyle.blurple, custom_id="NIX|ROLE|MACOS"
    )
    async def NIXMACOS(self, button: nextcord.ui.Button, interaction):
        """Add/remove the MacOS role"""
        role = nextcord.utils.get(interaction.guild.roles, id=_getRole(nixID, "MacOS"))
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Windows",
        style=nextcord.ButtonStyle.blurple,
        custom_id="NIX|ROLE|WINDOWS",
    )
    async def NIXWINDOWS(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Windows role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "Windows")
        )
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Aussie", style=nextcord.ButtonStyle.blurple, custom_id="NIX|ROLE|AUSSIE"
    )
    async def NIXAUSSIE(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Aussie role"""
        role = nextcord.utils.get(interaction.guild.roles, id=_getRole(nixID, "AUS"))
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Kiwi", style=nextcord.ButtonStyle.blurple, custom_id="NIX|ROLE|KIWI"
    )
    async def NIXKIWI(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Kiwi role"""
        role = nextcord.utils.get(interaction.guild.roles, id=_getRole(nixID, "NZ"))
        await clicky(role, button, interaction)


class nixrolesCOL(nextcord.ui.View):
    """Buttons for assign colour roles in the NIX server"""

    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @nextcord.ui.button(
        label="Black", style=nextcord.ButtonStyle.grey, custom_id="NIX|ROLE|BLACK"
    )
    async def NIXBLACK(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Black role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "COL_black")
        )
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Blue", style=nextcord.ButtonStyle.grey, custom_id="NIX|ROLE|BLUE"
    )
    async def NIXBLUE(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Blue role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "COL_blue")
        )
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Dark Blue",
        style=nextcord.ButtonStyle.grey,
        custom_id="NIX|ROLE|BLUEDARK",
    )
    async def NIXBLUEDARK(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Dark Blue role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "COL_blueDark")
        )
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Brown", style=nextcord.ButtonStyle.grey, custom_id="NIX|ROLE|BROWN"
    )
    async def NIXBROWN(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Brown role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "COL_brown")
        )
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Green", style=nextcord.ButtonStyle.grey, custom_id="NIX|ROLE|GREEN"
    )
    async def NIXGREEN(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Green role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "COL_green")
        )
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Dark Green",
        style=nextcord.ButtonStyle.grey,
        custom_id="NIX|ROLE|GREENDARK",
    )
    async def NIXGREENDARK(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Dark Green role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "COL_greenDark")
        )
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Lilac", style=nextcord.ButtonStyle.grey, custom_id="NIX|ROLE|LILAC"
    )
    async def NIXLILAC(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Lilac role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "COL_lilac")
        )
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Orange", style=nextcord.ButtonStyle.grey, custom_id="NIX|ROLE|ORANGE"
    )
    async def NIXORANGE(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Orange role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "COL_orange")
        )
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Pink", style=nextcord.ButtonStyle.grey, custom_id="NIX|ROLE|PINK"
    )
    async def NIXPINK(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Pink role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "COL_pink")
        )
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Dark Red", style=nextcord.ButtonStyle.grey, custom_id="NIX|ROLE|REDDARK"
    )
    async def NIXREDDARK(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Dark Red role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "COL_redDark")
        )
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="White", style=nextcord.ButtonStyle.grey, custom_id="NIX|ROLE|WHITE"
    )
    async def NIXWHITE(self, button: nextcord.ui.Button, interaction):
        """Add/remove the White role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "COL_white")
        )
        await clicky(role, button, interaction)

    @nextcord.ui.button(
        label="Yellow", style=nextcord.ButtonStyle.grey, custom_id="NIX|ROLE|YELLOW"
    )
    async def NIXYELLOW(self, button: nextcord.ui.Button, interaction):
        """Add/remove the Yellow role"""
        role = nextcord.utils.get(
            interaction.guild.roles, id=_getRole(nixID, "COL_yellow")
        )
        await clicky(role, button, interaction)


class factSubmit(nextcord.ui.Modal):
    """Fact submission modal"""

    def __init__(self):
        super().__init__(title="Fact Submission", timeout=30 * 60)
        self.content = nextcord.ui.TextInput(
            label="Fact",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Please be concise but informative. Thank you.",
            required=True,
            min_length=3,
            max_length=300,
        )
        self.add_item(self.content)

        self.sourceLink = nextcord.ui.TextInput(
            label="Link to Source",
            required=False,
            min_length=3,
            max_length=250,
        )
        self.add_item(self.sourceLink)

        self.source = nextcord.ui.TextInput(
            label="Name of Source",
            required=True,
            min_length=3,
            max_length=75,
        )
        self.add_item(self.source)

        self.extraLinks = nextcord.ui.TextInput(
            label="If any additional links.",
            style=nextcord.TextInputStyle.paragraph,
            required=False,
            placeholder="Please put each link on new line.",
            min_length=3,
            max_length=300,
        )
        self.add_item(self.extraLinks)

        self.name = nextcord.ui.TextInput(
            label="Your name.",
            required=False,
            placeholder="If empty your current display name will be used.",
            min_length=3,
            max_length=300,
        )
        self.add_item(self.name)

    async def callback(self, inter: Interaction):
        """Callback function for use with the fact submission modal"""
        log.debug("factSubmit callback")
        if len(self.source.value) >= 3:
            source = str(self.source.value)
        else:
            source = None
        if len(self.sourceLink.value) >= 3:
            sourceLink = str(self.sourceLink.value)
        else:
            sourceLink = None
        if source is None and sourceLink is None:
            try:
                await inter.send("A source must be provided!", ephemeral=True)
            except Exception:
                log.exception(f"Fact Submit")
            log.debug(f"{source=} |{sourceLink=}")
            return
        data = {}
        data["source"] = source
        data["sourceLink"] = sourceLink
        data["content"] = str(self.content.value)
        usrID = str(inter.user.id)
        data["providerID"] = int(usrID)
        if len(self.extraLinks.value) >= 3:
            data["extraLinks"] = str(self.extraLinks.value)
        else:
            data["extraLinks"] = None
        if len(self.name.value) >= 3:
            data["providerName"] = str(self.name.value)
        else:
            data["providerName"] = str(inter.user.display_name)
        curTime = int(time.time())
        data["initialAdd"] = curTime
        data["lastUpdate"] = "YYYY-MM-DD"
        # log.debug(f"{type(data)}, {data}")
        factSubs = readJSON(file=paths.work.joinpath("factSubs"))
        if usrID not in factSubs:
            factSubs[usrID] = {}
        usrSubs = factSubs[usrID]
        keys = list(usrSubs.keys())
        print(type(keys), keys)
        if len(keys) > 0:
            key = keys[-1]
            case = str(int(key) + 1)
        else:
            case = "0"
        log.debug(f"{case=}")
        usrSubs[case] = data
        log.debug(usrSubs)
        factSubs[usrID] = usrSubs
        # log.debug(factSubs)
        writeJSON(data=factSubs, file=paths.work.joinpath("factSubs"))
        owner = inter.guild.get_member(gxConfig.ownerID)
        try:
            await owner.send(f"A fact has been submitted;\n\n{data}")
            await inter.send("Fact submitted. Once reviewed, you'll recieve a DM.")
        except Exception:
            log.exception(f"Fact Submit Final")


# MIT APasz
