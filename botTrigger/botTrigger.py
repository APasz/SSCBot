#!/usr/bin/env python3
from operator import mod
import config
botRepo = config.repo
config.botFoldSeperator

import os
import platform
import sys

PID = os.getpid()
print (f"*** Starting ***\nPID: {PID}")
curDir = os.path.dirname(os.path.realpath(__file__))
scriptName = curDir.split(os.sep)[-1]


import logging

logLevel = f"logging.{config.logLevel.upper()}"

log = logging.getLogger()
log.setLevel(config.logLevel.upper())

handleConsole = logging.StreamHandler(sys.stdout)
handleConsole.setFormatter(logging.Formatter('%(asctime)s | %(message)s', "%H:%M:%S"))
log.addHandler(handleConsole)

handleFile = logging.FileHandler(filename=f'{scriptName}.log', encoding='utf-8', mode='a')
handleFile.setFormatter(logging.Formatter('%(asctime)s:%(created)f |:| %(funcName)s | %(message)s',))
log.addHandler(handleFile)

PID = os.getpid()
log.critical(f"\nStarting... PID: {PID}")

platformOS = sys.platform.lower()
log.info(f"Platform: {platformOS.title()} | {platform.node()}")
if platformOS.startswith('linux'): pingOP = "-c"
elif platformOS.startswith('windows'): pingOP = "-n"



if config.botDir is None:
	files = []
	for filename in os.listdir(curDir):
		if filename.startswith(botRepo) and config.botFoldSeperator in filename:
			timestamp = int(filename.split(config.botFoldSeperator)[-1])
			files.append(timestamp)
	botDir = f"{botRepo} {config.botFoldSeperator} {max(files)}"
else: botDir = os.path.join(curDir, config.botDir)

log.info(f"Old Bot Directory: {botDir}")

botReqsFile = os.path.join(botDir, "requirements.txt")
trigReqsFile = os.path.join(curDir, "require.txt")

critFiles = [botDir, trigReqsFile, botReqsFile]
for element in critFiles:
	if not os.path.exists(element):
		log.error(f"{element}: not found")
		sys.exit()


requiredBotMods = open(botReqsFile).read().splitlines()
requiredCoreMods = open(trigReqsFile).read().splitlines()
requiredModules = set(requiredBotMods + requiredCoreMods)

log.info(f"Bot Directory... Found")

import time
import subprocess
import netifaces
import shutil

log.info(f"Core Modules... Loaded")

def checkNet(host=None):
	def gate():
		gw = netifaces.gateways()['default']
		if gw: return gw[netifaces.AF_INET][0]
		else: return False
	if host is None: host = gate()
	if host: return subprocess.run(["ping", pingOP, "1", host], stdout=subprocess.DEVNULL)

def githubClone(repo:str, folder:str, directory:str=curDir):
	try:
		gitURL = f"https://github.com/APasz/{repo}.git"
		gitDir = os.path.join(directory, folder)
		if os.path.exists(gitDir):
			shutil.rmtree(gitDir)
		os.makedirs(gitDir)
		Repo.clone_from(gitURL, gitDir)
		return True
	except Exception as e:
		log.error(f"githubClone; XCP {e}")
		return False

log.info(f"Functions... OK")

for element in config.netChecks:
	while True:
		if checkNet(config.netChecks[element]):
			log.info(f"{element} Connection Established")
			time.sleep(config.paceNorm)
			break
		else:
			log.error(f"No {element} Connection")
			time.sleep(config.paceErr)
			continue

log.info(f"Internet... OK")

fails = []
def modules(fails):
	for module in requiredModules:
		if subprocess.run(["python3", "-m", "pip", "install", "-r", f"{module}"], stdout=subprocess.DEVNULL):
			log.info(f"{module}... Installed")
		else:
			log.error(f"{module}... Failure")
			fails.append(module)
		return fails
fails = modules(fails)
print(len(fails))
if len(fails) > 0:
	log.critical(f"Module/s not found {fails}")
	sys.exit()

from git import Repo

log.info("External Modules... Loaded")

unix = int(time.time())
newBotFold = f"{botRepo} {config.botFoldSeperator} {unix}"
if not githubClone(repo=botRepo, folder=newBotFold):
	log.critical("Git Clone Failed")
log.info(f"New Bot Directory: {newBotFold}")
log.info("Git Clone... OK")

shutil.rmtree(f"{newBotFold}{os.sep}secrets")

criticalBotData = ["secrets", "config.py", "config.json", "messID.txt"]
for item in criticalBotData:
	src = str(botDir + os.sep + item)
	dst = str(newBotFold + os.sep + item)
	if os.path.exists(src):
		if os.path.isfile(src): shutil.copy(src, dst)
		else: shutil.copytree(src, dst)
	else: log.critical(f"Missing SRC: {item}")

log.info("Critical Bot Files... Copied")
time.sleep(1)
log.critical(f"Starting Discord Bot {botRepo}")

while True:
	try:
		subprocess.run("python3 bot.py", shell=True, cwd=newBotFold, check=True)
	except subprocess.CalledProcessError as e:
		log.critical(f"except: {e.returncode}")
		if e.returncode == 194:
			log.critical("Rebooting Soon")
			time.sleep(config.paceNorm)
			if platformOS.startswith('linux'):
				os.system("reboot")
			elif platformOS.startswith('windows'):
				os.system("shutdown -t 0 -r -f")
		else: time.sleep(config.paceErr)
		txt = f"restarting in... {config.paceErr}"
		log.critical(txt)
		time.sleep(config.paceErr)

log.critical("*** Terminated ***")