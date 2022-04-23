print ("UtilGen")
import nextcord
from nextcord import Interaction, Role
import config

from util.fileUtil import readJSON

configuration = readJSON(filename = "config")
configGen = configuration['General']
import logging

log = logging.getLogger("discordGeneral")

def getCol(col:str):
	red, green, blue = configGen['EmbedColours'][col]	
	colour = nextcord.Colour.from_rgb(red, green, blue)	
	return colour

def hasRole(role:Role, roles):
	if role in roles: return True
	else: return False
from pprint import pprint

def getUserID(obj):
	if hasattr(obj, "author"):
		return str(obj.author.id)
	if hasattr(obj, "user"):
		return str(obj.user.id)

async def blacklistCheck(ctx, blklstType:str="gen"):
	"""Checks if user in the blacklist"""
	def check():
		if blklstType == "gen":
			filename = "GeneralBlacklist"
		elif blklstType == "ssc":
			filename = "SSCBlacklist"
		return readJSON(filename=filename, directory=['secrets'])
	userID = None
	userID = getUserID(obj=ctx)
	print(userID)	
	if (userID == config.ownerID): return True
	if (userID == ctx.guild.owner.id): return True
	BL = check()
	if not bool(BL.get(userID)): return True
	txt = f"""You're blacklisted from using this **{config.botName}**.
If you believe this to be error, please contact a server Admin/Moderator."""
	if "inter" in str(type(ctx)):
		await ctx.response.send_message(txt, ephemeral=True)
	elif "user" in str(type(ctx)):
		await ctx.send(txt)
	elif "member" in str(type(ctx)):
		await ctx.send(txt)
	log.info(f"BLCheck: {userID} | {blklstType}")
	return False
