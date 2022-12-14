# from nextcord import Locale
# import gettext
# from pathlib import Path as Pathy

# {"COMM_blabla": {Locale.en_GB: "enText", Locale.fr: "frText"}}

# localePath = Pathy().parent.absolute().joinpath("locale")

# localGettext = {}
# for item in localePath.iterdir():
#    itemPO = localePath.joinpath(str(item), "LC_MESSAGES", "base.po")
#    print(itemPO)
#    if not itemPO.exists():
#        continue
#    k = gettext.translation(
#        domain="base", localedir=localePath, languages=[str(item.name)]
#    )
#    localGettext[str(item.name)] = k

# enLoc = localePath.joinpath("en", "LC_MESSAGES", "base.po")
# print(enLoc, enLoc.exists())
# locDict = {}
# with enLoc.open("r") as file:
#    file = file.read().splitlines()
#    for line in file:
#        if line.startswith("msgid") and len(line) > 8:
#            line = line.removesuffix('"')
#            line = line.removeprefix('msgid "')
#            locDict[line] = {}


# for loc in locDict:
#    for item in Locale:
#        if item.name not in localGettext:
#            item.name = "en"
#        locDict[loc][item.name] = localGettext[item.name].gettext(loc)


# def getLC(key):
#    "Returns dict of all nextcord locale names and the translated text for key"
#    return locDict[key]
