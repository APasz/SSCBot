print ("UtilFile")
import asyncio
import json
import logging
import os
import shutil
import time

log = logging.getLogger("discordGeneral")

ownerName = "APasz"
botName = "Strider"
botID = 764270771350142976

cacheJSON = {}

def splitDirFile(directory:str, limit:int=1):
	return directory.rsplit(os.sep, limit)

def parentDir():
	curDir = os.path.dirname(os.path.realpath(__file__))
	parDir = os.path.abspath(os.path.join(curDir, os.pardir))
	return parDir

def writeJSON(data, filename:str, directory:list=None):
	print(f"writeJSON: {filename}")
	if not filename.casefold().endswith(".json"):
		filename = filename + ".json"
	parDir = parentDir()
	if "list" in str(type(directory)):
		fileDir = os.path.join(*directory, filename)
	else: fileDir = filename
	fullDir = os.path.join(parDir, fileDir)
	try:
		with open(fullDir, "w") as file:
			json.dump(data, file, indent=4) #sort_keys=True
			return True
	except Exception as e:
		log.error(f"writeJSON: XCP {e}")
		return False

def readJSON(filename:str, directory:list=None, cache:bool=True):
	print(f"readJSON: {filename}")
	if not filename.casefold().endswith(".json"):
		filename = filename + ".json"
	parDir = parentDir()
	if "list" in str(type(directory)):
		fileDir = os.path.join(*directory, filename)
	else: fileDir = filename
	fullDir = os.path.join(parDir, fileDir)
	global cacheJSON
	def read():
		data = {}
		try:
			with open(fullDir, 'r') as file:
				data = json.load(file)
		except FileNotFoundError:
			if writeJSON(data=data, directory=directory, filename=filename) is False:
				log.error(f"readJSON; writeJSON: {fullDir}")
				return False
		except Exception as e:
			log.error(f"readJSON: XCP {e}")
			return False
		finally: return data
	if cache is False: return read()
	if os.path.exists(fullDir):
		newModTime = int(os.path.getmtime(fullDir))
	else: newModTime = None
	if fileDir in cacheJSON:
		oldModTime = cacheJSON[fileDir]['modTime']
		newModTime = int(os.path.getmtime(fullDir))
		if oldModTime != newModTime:
			data = read()		
			meta = {
				'modTime':newModTime,
				'content':data
			}
			cacheJSON[fileDir] = meta
		else:
			data = cacheJSON[fileDir]['content']
	else:
		data = read()
		meta = {
			'modTime':newModTime,
			'content':data
		}
		cacheJSON[fileDir] = meta
	return data

def combineJSON(current:str, new:str):
	try:
		if not os.path.exists(current): return False
		if not os.path.exists(new): return False
		curSplit = splitDirFile(current)
		curJSON = readJSON(directory=curSplit[0], filename=curSplit[1])
		newSplit = splitDirFile(new)
		newJSON = readJSON(directory=newSplit[0], filename=newSplit[1])
		mergeJSON = curJSON | newJSON
		if writeJSON(data=mergeJSON, directory=curSplit[0], filename=curSplit[1]):
			return True
		else: return False
	except Exception as e: return e

def copyFile(src:str, dst:str, file:str):
	if not os.path.exists(dst):
		try:
			os.makedirs(dst)
		except Exception as e:
			log.error(e)
			return False
	try:
		shutil.copy(os.path.join(src, file), os.path.join(dst, file))
		return True
	except Exception as e:
		log.error(e)
		return False

def newFile(data, directory:str, filename:str, extenstion:str="txt"):
	file = os.path.join(directory, f"{filename}.{extenstion}")
	f = open(file, 'w')
	print(data)
	f.write(str(data))
	f.close()
	return True

def readFile(directory:str, filename:str, extenstion:str="txt"):
	file = os.path.join(directory, f"{filename}.{extenstion}")
	f = open(file, 'r')
	data = f.read()
	f.close()
	return data

def configUpdate(tmpDir:str, curDir:str, attachCF):
	"""Takes a discord json file object, saves it and merges it with the existing config json file"""
	print("configUpdate")
	log.critical("configUpdate")
	curCF = os.path.join(curDir, 'config.json')
	if os.path.exists(curCF):
		with open(curCF, 'r') as file:
			oldCFdata = json.load(file)
		file.close()
	else: return False

	newCF = os.path.join(tmpDir, 'config.json')	
	attachCF.save(newCF)
	asyncio.sleep(0.5)
	if os.path.exists(newCF):
		with open(newCF, 'r') as file:
			newCFData = json.load(file)
		file.close()
	else: return False

	mergedCFdata = oldCFdata | newCFData
	mergedCF = os.path.join(curDir, "config.py")
	if os.path.exists(mergedCF): os.remove(mergedCF)
	with open(mergedCF, "w") as file:
		json.dump(mergedCFdata, file, sort_keys=True, indent=4)
	file.close()
	return True


#MIT APasz
