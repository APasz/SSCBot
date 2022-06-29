print("UtilFile")
import asyncio
import json
import logging
import os
import shutil

import nextcord

log = logging.getLogger("discordGeneral")

ownerName = "APasz"
botName = "Strider"
botID = 764270771350142976

cacheJSON = {}


def splitDirFile(directory: str, limit: int = 1):
    return directory.rsplit(os.sep, limit)


def parentDir():
    curDir = os.path.dirname(os.path.realpath(__file__))
    parDir = os.path.abspath(os.path.join(curDir, os.pardir))
    return parDir


def writeJSON(data, filename: str, directory: list = None):
    log.debug(f"{filename}")
    if not filename.casefold().endswith(".json"):
        filename = filename + ".json"
    parDir = parentDir()
    if "list" in str(type(directory)):
        fileDir = os.path.join(*directory, filename)
    else:
        fileDir = filename
    fullDir = os.path.join(parDir, fileDir)
    try:
        with open(fullDir, "w") as file:
            json.dump(data, file, indent=4)  # sort_keys=True
            return True
    except Exception as e:
        log.error(f"writeJSON: XCP {e}")
        return False


def cacheWrite():
    log.debug(f"writeCache")
    writeJSON(data=cacheJSON, filename="cache")


def readJSON(filename: str, directory: list = None, cache: bool = True):
    log.debug(f"{filename}")
    if not filename.casefold().endswith(".json"):
        filename = filename + ".json"
    if "list" in str(type(directory)):
        fileDir = os.path.join(*directory, filename)
    else:
        fileDir = filename
    fullDir = os.path.join(parentDir(), fileDir)
    global cacheJSON

    def read():
        data = {}
        try:
            with open(fullDir, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            if writeJSON(data=data, directory=directory, filename=filename) is False:
                log.error(f"readJSON; writeJSON: {fullDir}")
                return False
        except Exception as e:
            log.error(f"readJSON: XCP {e}")
            return False
        finally:
            return data

    if cache is False:
        return read()
    if os.path.exists(fullDir):
        newModTime = int(os.path.getmtime(fullDir))
        # log.debug(f"exists:, {fullDir}, {newModTime}")
    else:
        newModTime = 0
    if fileDir in cacheJSON:
        # log.debug("fileInCache")
        oldModTime = cacheJSON[fileDir]["modTime"]
        if oldModTime != newModTime:
            data = read()
            meta = {"modTime": newModTime, "content": data}
            cacheJSON[fileDir] = meta
        else:
            data = cacheJSON[fileDir]["content"]
    else:
        log.debug("fileNotInCache")
        data = read()
        meta = {"modTime": newModTime, "content": data}
        cacheJSON[fileDir] = meta
    return data


def combineJSON(current: str, new: str):
    log.debug(f"{current} -> {new}")
    try:
        if not os.path.exists(current):
            return False
        if not os.path.exists(new):
            return False
        curSplit = splitDirFile(current)
        curJSON = readJSON(directory=curSplit[0], filename=curSplit[1])
        newSplit = splitDirFile(new)
        newJSON = readJSON(directory=newSplit[0], filename=newSplit[1])
        mergeJSON = curJSON | newJSON
        if writeJSON(data=mergeJSON, directory=curSplit[0], filename=curSplit[1]):
            return True
        else:
            return False
    except Exception as xcp:
        return xcp


def copyFile(src: str, dst: str, file: str):
    log.debug(f"{src} -> {dst}")
    if not os.path.exists(dst):
        try:
            os.makedirs(dst)
        except Exception as e:
            log.error(e)
            return False
    try:
        shutil.copy(os.path.join(src, file), os.path.join(dst, file))
        return True
    except Exception as xcp:
        log.error(xcp)
        return False


def newFile(data, directory: str, filename: str, extenstion: str = "txt"):
    log.debug(f"{type(data)} | {directory}, {filename} {extenstion}")
    file = os.path.join(directory, f"{filename}.{extenstion}")
    f = open(file, "w")
    f.write(str(data))
    f.close()
    return True


def readFile(directory: str, filename: str, extenstion: str = "txt"):
    log.debug(f"{directory}, {filename} {extenstion}")
    file = os.path.join(directory, f"{filename}.{extenstion}")
    f = open(file, "r")
    data = f.read()
    f.close()
    return data


async def configUpdate(tmpDir: str, curDir: str, attachCF):
    """Takes a discord json file object, saves it and merges it with the existing config json file"""
    log.debug(f"{tmpDir} | {curDir}")
    curCF = os.path.join(curDir, "config.json")
    if os.path.exists(curCF):
        with open(curCF, "r") as file:
            oldCFdata = json.load(file)
        file.close()
    else:
        return False

    newCF = os.path.join(tmpDir, "config.json")
    await attachCF.save(newCF)
    await asyncio.sleep(0.5)
    if os.path.exists(newCF):
        with open(newCF, "r") as file:
            newCFData = json.load(file)
        file.close()
    else:
        return False

    mergedCFdata = oldCFdata | newCFData
    mergedCF = os.path.join(curDir, "config.json")
    if os.path.exists(mergedCF):
        os.remove(mergedCF)
    with open(mergedCF, "w") as file:
        json.dump(mergedCFdata, file, sort_keys=True, indent=4)
    file.close()
    return True


async def uploadfile(directory, newfile: nextcord.Attachment, bak: bool):
    log.debug(f"{directory}, {newfile.filename}, {bak}")
    if directory is not None:
        filepath = f"{os.sep}".join(directory)
        fullPath = os.path.join(parentDir(), filepath, newfile.filename)
    else:
        fullPath = os.path.join(parentDir(), newfile.filename)
    log.debug(fullPath)
    if os.path.exists(fullPath):
        if bak is True:
            shutil.move(fullPath, fullPath + ".bak")
            log.info("File bakked")
        else:
            os.remove(filepath)
            log.info("File removed")
    await newfile.save(fullPath)
    return os.path.exists(fullPath)


# MIT APasz
