print ("UtilAPI")
import os
import json
import requests
import logging

log = logging.getLogger("discordGeneral")

import config

def steamWSGet(wsID):
    print("steamWS")
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
    params = {
        'itemcount':1,
        'publishedfileids[0]':wsID
    }
    try:
        res = requests.post(url, data = params)
    except Exception as e: log.debug(f"{res.status_code} XCP {e}")
    log.info(f"steamWSGet | {res.status_code}")
    print(res.status_code)
    dets = None
    if res:
        data = res.json()
        dets = data['response']['publishedfiledetails'][0]
    else: return res.status_code
    return dets

def steamUsrGet(usrID):
    print("steamUsr")
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {
        'key':str(config.STEAMAPI),
        'steamids':str(usrID)
    }
    try:
        res = requests.get(url, params = params)
    except Exception as e: log.debug(f"{res.status_code} XCP {e}")
    log.info(f"steamUsrGet | {res.status_code}")
    print(res.status_code)
    author = None
    if res:
        data = res.json()
        author = data['response']['players'][0]
    else: return res.status_code
    return author
     
def nexusModGet(game, modID):
    print("nexusMod")
    url = f"https://api.nexusmods.com/v1/games/{game}/mods/{modID}.json"
    params = {
        'apikey':config.NEXUSAPI
    }
    try:
        res = requests.get(url, headers = params)
    except Exception as e: log.debug(f"{res.status_code} XCP {e}")
    log.info(f"nexusModGet | {res.status_code}")
    print(res.status_code)
    data = None
    if res:
        data = res.json()
    else: return res.status_code
    return data

def tpfnetModGet(data):
    print("tpfnetMod")
    return 200
    params = {

    }
    url = "https://www.transportfever.net/filebase/index.php?recent-entry-list/" #f"https://www.transportfever.net/filebase/repos/tpf2.json"
    try:
        res = requests.get(url, data=params)
    except Exception as e: log.debug(f"{res.status_code} XCP {e}")
    log.info(f"tpfnetModGet | {res.status_code}")
    print(res.status_code)
    return

def parseURL(url):
    log.debug(f"parseURL: {url}")
    game = None
    cont = url.split("https://")[-1]
    if "steamcommunity" in cont:
        plat = "steam"
        cont = cont.split("?id=")[-1]
        if "&" in cont:
            cont = cont.split("&")[0]
    elif "nexusmods" in cont:
        plat = "nexus"
        cont = cont.split("com/")[-1]
        game = cont.split("/mods")[0]
        cont = cont.split("mods/")[-1]
        if "?" in cont:
            cont = cont.split("?")[0]
        cont = cont.removesuffix('/')
    elif "transportfever" in cont:
        plat = "tpfnet"
        cont = cont.split("entry/")[-1]
        if "-" in cont:
            stuff = cont.split("-", 1)
            cont = stuff[0]
            game = stuff[1]
    data = {'ID':cont,
    'game':game,
    'platform':plat}
    log.debug(data)
    return data


    # with open('./Data.json', 'w') as file:
    #     json.dump(res.text, file)

#MIT APasz