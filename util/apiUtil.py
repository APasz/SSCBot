import logging
import os

import requests

from config import NEXUSAPI, STEAMAPI

print("UtilAPI")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY UTIL_API IMPORT MODULES")
    import gspread
except Exception:
    logSys.exception("UTIL_API IMPORT MODULES")


def steamWSGet(wsID) -> int | dict:
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
        return data["response"]["publishedfiledetails"][0]
    else:
        return res.status_code


def steamUsrGet(usrID) -> int | dict:
    log.debug("steamUsr")
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": str(STEAMAPI), "steamids": str(usrID)}
    try:
        res = requests.get(url, params=params)
    except Exception:
        log.exception(f"steamUsrGet | {res.status_code=}")
    log.info(f"steamUsrGet | {res.status_code=}")
    if res:
        data = res.json()
        return data["response"]["players"][0]
    else:
        return res.status_code


def nexusModGet(game, modID) -> int | dict:
    log.debug("nexusMod")
    url = f"https://api.nexusmods.com/v1/games/{game}/mods/{modID}.json"
    params = {"apikey": NEXUSAPI}
    try:
        res = requests.get(url, headers=params)
    except Exception:
        log.exception(f"nexusModGet | {res.status_code=}")
    log.info(f"nexusModGet | {res.status_code=}")
    if res:
        return res.json()
    else:
        return res.status_code


def tpfnetModGet(data) -> int | dict:
    log.debug("tpfnetMod")
    return 200
    params = {}
    # f"https://www.transportfever.net/filebase/repos/tpf2.json"
    url = "https://www.transportfever.net/filebase/index.php?recent-entry-list/"
    try:
        res = requests.get(url, data=params)
    except Exception:
        log.exception(f"tpfnetModGet | {res.status_code=}")
    log.info(f"tpfnetModGet | {res.status_code=}")
    return


def parseURL(url) -> dict | None:
    """Separates out the platform, ID, and game (if present)"""
    log.debug(f"parseURL: {url=}")

    data = {"url": url, "game": None}
    cont = url.split("https://")[-1]

    if "steamcommunity" in cont:
        data["platform"] = "steam"
        cont = cont.split("id=")[-1]
        if "&" in cont:
            cont = cont.split("&")[0]
        data["ID"] = cont

    elif "nexusmods" in cont:
        data["platform"] = "nexus"
        cont = cont.split("com/")[-1]
        data["game"] = cont.split("/mods")[0]
        cont = cont.split("mods/")[-1]
        if "?" in cont:
            cont = cont.split("?")[0]
        data["ID"] = cont.removesuffix("/")

    elif "transportfever" in cont:
        if "attachment" in cont:
            pass
        data["platform"] = "tpfnet"
        cont = cont.split("entry/")[-1]
        if "-" in cont:
            stuff = cont.split("-", 1)
            data["ID"] = stuff[0]
            data["game"] = stuff[1]

    else:
        return None

    log.debug(f"{data=}")
    return data


def GSheetGet(
    sheetName: str = "TpF Screenshot Competition Public", page: str = "List"
) -> any:
    log.debug(f"GSheetGet: {sheetName=}")
    servAcc = gspread.service_account(
        filename=f"secrets{os.sep}google_service_account.json"
    )
    sheet = servAcc.open(sheetName)
    data = sheet.worksheet(page)
    return data


# MIT APasz
