import json
import logging
import inspect
from pathlib import Path as Pathy

print("UtilFile")

log = logging.getLogger("discordGeneral")
logSys = logging.getLogger("discordSystem")
try:
    logSys.debug("TRY UTIL_FILE IMPORT MODUELS")
    logSys.debug("No external moduels")
except Exception:
    logSys.exception("UTIL_FILE IMPORT MODUELS")


class paths:
    "Central location of all useful paths as path objects"

    work = Pathy(__file__).absolute().parent.parent
    "Directory where the primary bot file should be"
    log = work.joinpath("logs")
    cog = work.joinpath("cogs")
    util = work.joinpath("util")
    conf = work.joinpath("configs")
    dump = work.joinpath("dump")
    locale = work.joinpath("locale")
    secret = work.joinpath("secrets")


cacheJSON = {}


def writeJSON(data: dict, file: Pathy, sort=False) -> bool:
    """Creates a JSON file contain data."""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {file=}")
    if not (file.name).casefold().endswith(".json"):
        file = Pathy(f"{file}.json").absolute()

    if file.exists():
        logSys.warning(f"Exists: {file=}")
    try:
        with open(file, "w") as f:
            json.dump(obj=data, fp=f, indent=4, separators=(", ", ": "), sort_keys=sort)
            return True
    except Exception:
        logSys.exception("WriteJSON")
        return False


def cacheWrite() -> bool:
    logSys.debug(f"writeCache")
    global cacheJSON

    dmpDir = paths.dump
    try:
        dmpDir.mkdir()
    except FileExistsError:
        pass
    except Exception:
        logSys.exception(f"Make Dump Folder")
    logSys.info("Dumping CacheJSON")
    return writeJSON(data=cacheJSON, file=dmpDir.joinpath("cacheJSON"))


def readJSON(file: Pathy, cache: bool = True) -> dict | bool:
    """Read a JSON file. By default caches all files to memory.
    If files doesn't exist, it'll be created and return an empty dict"""
    func = inspect.stack()[1][3]
    logSys.debug(f"{func=} | {file=}")
    global cacheJSON

    if not (file.name).casefold().endswith(".json"):
        file = Pathy(f"{file}.json").absolute()

    def read(file) -> dict | bool:
        # logSys.debug(f"read {file=}")
        data = {}
        try:
            with open(file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            logSys.error(f"File not Found {file=}")
            if writeJSON(data=data, file=file) is False:
                logSys.error(f"| writeJSON")
                return False
        except Exception:
            logSys.exception("readJSON")
            return False
        finally:
            return data

    if cache is False:
        return read(file)

    if file.exists():
        newModTime = int(file.stat().st_mtime)
        # logSys.debug(f"exists:, {file=}, {newModTime=}")
    else:
        newModTime = 0

    relFile = file.relative_to(paths.work)
    print(relFile)
    if relFile in cacheJSON:
        # logSys.debug("fileInCache")
        oldModTime = cacheJSON[relFile]["modTime"]
        if oldModTime != newModTime:
            data = read(file)
            meta = {"modTime": newModTime, "content": data}
            cacheJSON[relFile] = meta
        else:
            data = cacheJSON[relFile]["content"]
    else:
        # logSys.debug("fileNotInCache")
        data = read(file)
        meta = {"modTime": newModTime, "content": data}
        cacheJSON[relFile] = meta
    return data


# MIT APasz
