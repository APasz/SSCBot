print ("UtilFile")
import json
import logging
import os

log = logging.getLogger("discordGeneral")

import config


def readJSON(filename):
	print(f"readJSON: {filename}")
	dir = f"./{filename}.json"
	try:
		with open(f"{dir}", 'r') as file:
			data = json.load(file)
	except FileNotFoundError:
		data = {}
		with open(f"{dir}", 'w+') as file:
			json.dump(data, file, indent=4)
	return data

def writeJSON(data, filename):
	dir = f"./{filename}.json"
	print(f"writeJSON: {filename}")
	done = 0
	with open(f"{dir}", "w+") as file:
		json.dump(data, file, indent=4)
		done = 1
	return done

genBL = readJSON("secrets/GeneralBlacklist")
sscBL = readJSON("secrets/SSCBlacklist")
genModTime = int(os.path.getmtime('./secrets/GeneralBlacklist.json'))
sscModTime = int(os.path.getmtime('./secrets/SSCBlacklist.json'))

def blacklistCheck(usr:str, blklstType="gen"):
	log.info(f"BLCheck: {usr} | {blklstType}")
	if blklstType == "gen":
		global genBL
		global genModTime
		genNewTime = int(os.path.getmtime('./secrets/GeneralBlacklist.json'))
		if genNewTime != genModTime:
			print(genModTime)
			print(genNewTime)
			genBL = readJSON("secrets/GeneralBlacklist")
			genModTime = genNewTime
		else: genBL = genBL
		if usr in genBL:
			txt = f"""You're blacklisted from using {config.botName}
If you believe this to be an error, contact {config.ownerName} or an Admin/Moderator."""
			return txt
		else: return True
	elif blklstType == "ssc":
		global sscBL
		global sscModTime
		sscNewTime = int(os.path.getmtime('./secrets/SSCBlacklist.json'))
		if sscNewTime != sscModTime:
			print(sscModTime)
			print(sscNewTime)
			sscBL = readJSON("secrets/SSCBlacklist")
			sscModTime = sscNewTime
		else: sscBL = sscBL
		if usr in sscBL:
			txt = f"""You're blacklisted from participating in the SSC.
If you believe this to be an error, contact {config.ownerName} or an Admin/Moderator."""
			return txt
		else: return True

#MIT APasz