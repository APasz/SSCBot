import json
import logging
import os

print("UtilFile")

log = logging.getLogger("discordGeneral")
try:
    log.debug("TRY UTIL_FILE IMPORT MODUELS")
    log.debug("No external moduels")
except Exception:
    log.exception("UTIL_FILE IMPORT MODUELS")

cacheJSON = {}


def parentDir() -> str:
    """Assuming this function is where it's meant to be, returns the folder of the main script."""
    curDir = os.path.dirname(os.path.realpath(__file__))
    parDir = os.path.abspath(os.path.join(curDir, os.pardir))
    return parDir


def writeJSON(data: dict, filename: str, directory: list = None) -> bool:
    """Creates a JSON file contain data."""
    log.debug(f"{filename=}")
    if not filename.casefold().endswith(".json"):
        filename = filename + ".json"
    botDir = parentDir()
    if isinstance(directory, list):
        fileDir = os.path.join(*directory, filename)
    else:
        fileDir = filename
    fullDir = os.path.join(botDir, fileDir)
    try:
        with open(fullDir, "w") as file:
            json.dump(obj=data, fp=file, indent=4)
            return True
    except Exception:
        log.exception("WriteJSON")
        return False


def cacheWrite() -> bool:
    log.debug(f"writeCache")
    global cacheJSON
    dumpPath = os.path.join(parentDir(), "dump")
    try:
        os.mkdir(dumpPath)
    except FileExistsError:
        pass
    except Exception:
        log.exception(f"Make Dump Folder")
    log.info("Dumping CacheJSON")
    return writeJSON(data=cacheJSON, filename="cacheJSON", directory=["dump"])


def readJSON(filename: str, directory: list = None, cache: bool = True) -> dict | bool:
    """Read a JSON file. By default caches all files to memory. If files doesn't exist, it'll be created and return an empty dict"""
    log.debug(f"{filename=}")
    if not filename.casefold().endswith(".json"):
        filename = filename + ".json"
    if isinstance(directory, list):
        fileDir = os.path.join(*directory, filename)
    else:
        fileDir = filename
    fullDir = os.path.join(parentDir(), fileDir)
    global cacheJSON

    def read() -> dict | bool:
        data = {}
        try:
            with open(fullDir, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            if writeJSON(data=data, directory=directory, filename=filename) is False:
                log.error(f"| writeJSON: {fullDir=}")
                return False
        except Exception:
            log.exception("readJSON")
            return False
        finally:
            return data

    if cache is False:
        return read()
    if os.path.exists(fullDir):
        newModTime = int(os.path.getmtime(fullDir))
        # log.debug(f"exists:, {fullDir=}, {newModTime=}")
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


def newFile(data, directory: str, filename: str, extenstion: str = "txt") -> bool:
    """Creates a file"""
    log.debug(f"{type(data)} | {directory=}, {filename=} {extenstion=}")
    try:
        file = os.path.join(directory, f"{filename}.{extenstion}")
        f = open(file, "w")
        f.write(str(data))
        f.close()
    except Exception:
        log.exception("newFile")
        return False
    return True


def readFile(directory: str, filename: str, extenstion: str = "txt") -> str | bool:
    """Reads any sort of file and returns its content"""
    log.debug(f"{directory=}, {filename=} {extenstion=}")
    try:
        file = os.path.join(directory, f"{filename}.{extenstion}")
        f = open(file, "r")
        data = f.read()
        f.close()
    except Exception:
        log.exception("readFile")
    return data


# MIT APasz
