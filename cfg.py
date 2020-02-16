import discord
from discord.ext import commands

import os
from os import path

import logging
import pprint

import time,datetime

import asyncio,aiohttp

import urllib.request
from bs4 import BeautifulSoup

import hdebug
import privatevalues as priv

import shelve #for writing variables to a binary file

import json

import re #regex

from tatsumaki.wrapper import ApiWrapper as TatsuWrapper

from pydiscourse import DiscourseClient

# ~~~~~~ logger stuff ~~~~~~

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

#instantiate the handler that writes to file
if hdebug.hdebug:
	loggerFilename = 'debugbot.log'
else:
	loggerFilename = 'hermes.log'

fh = logging.FileHandler(filename=loggerFilename, encoding='utf-8', mode='w')
fh.setLevel(logging.DEBUG)

#instantiate the handler that prints to console
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

logger.debug('file logging initialized successfully')

bot = commands.Bot(command_prefix='!')

if hdebug.hdebug:
	token = priv.debugToken
else:
	token = priv.liveToken

tatsu = TatsuWrapper(priv.tatsuToken)

# discourse api stuff
forum_client = DiscourseClient(
        'https://forum.alt-h.net',
        api_username='Hermes',
        api_key=priv.discourseToken)

if hdebug.hdebug:
	fileDir = 'debug'
else:
	fileDir = 'live'

# ~~~~~~ other shit ~~~~~~
salutations = re.compile(r"(?i)^(well met|bonjour|greetings|salutations|(?:me|h)owdy|h(?:i)+|(?:ny|h)e(?:ll|ww)(?:o)+|hola|(?:g(?:ood |')?)?(?:(?:mornin|evenin)(?:g)*|afternoon|day))\W* (alt(?:.)*h|eve(?:r|w)y(?:one|being|body|pony)|fol(?:ks|x)|f(?:r|w)iend(?:o)*s|guys|hermes|people(s)*|peeps|ppl|(?:n)?(?:y)?(?:')?all)")

# ~~~~~~ save file ~~~~~~

settingsFile = 'settings.json'

try:
	with open(os.path.join(fileDir, settingsFile)) as file:
			settings = json.load(file)
except:
	logger.warning("file pendingq was blank - please check if this is as expected")
	settings = {}

# ~~~~~ verification stuff ~~~~~~

try:
	verifOpen = settings['verifOpen']
except:
	verifOpen = True
	logger.warning("didn't find variable 'verifOpen' in save file - reverting to default: " + str(verifOpen))

	settings['verifOpen'] = verifOpen
	with open(os.path.join(fileDir, settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

try:
	passphrase = settings['passphrase']
except:
	passphrase = 'haircut'
	logger.warning("didn't find variable 'passphrase' in save file - reverting to default: " + passphrase)

	settings['passphrase'] = passphrase
	with open(os.path.join(fileDir, settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

try:
	refdoclink = settings['refdoclink']
except:
	refdoclink = '<http://bit.ly/alth-refdoc>'
	logger.warning("didn't find variable 'refdoclink' in save file - reverting to default: " + refdoclink)

	settings['refdoclink'] = refdoclink
	with open(os.path.join(fileDir, settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

try:
	requiredTimeDiff = settings['requiredTimeDiff']
except:
	if hdebug.hdebug:
		requiredTimeDiff = 120 #in seconds
		logger.warning("didn't find variable 'requiredTimeDiff' in save file - reverting to DEBUG default: " + str(requiredTimeDiff))
	else:
		requiredTimeDiff = 129600 #in seconds
		logger.warning("didn't find variable 'requiredTimeDiff' in save file - reverting to LIVE default: " + str(requiredTimeDiff))

	settings['requiredTimeDiff'] = requiredTimeDiff
	with open(os.path.join(fileDir, settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

try:
	verificationCheckPeriod = settings['verificationCheckPeriod']
except:
	verificationCheckPeriod = 10 #in seconds
	logger.warning("didn't find variable 'verificationCheckPeriod' in save file - reverting to default")
	settings['verificationCheckPeriod'] = verificationCheckPeriod
	with open(os.path.join(fileDir, settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

try:
	minVouchXP = settings['minVouchXP']
except:
	if hdebug.hdebug:
		minVouchXP = 5000
		logger.warning("didn't find variable 'minVouchXP' in save file - reverting to DEBUG default: " + str(minVouchXP))
	else:
		minVouchXP = 5000
		logger.warning("didn't find variable 'minVouchXP' in save file - reverting to LIVE default: " + str(minVouchXP))
	settings['minVouchXP'] = minVouchXP
	with open(os.path.join(fileDir, settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

requestqfile = 'requestq.json'

try:
	with open(os.path.join(fileDir, requestqfile)) as file:
			requestq = json.load(file)
except:
	logger.warning("file requestq was blank - please check if this is as expected")
	requestq = {}

pendingqfile = 'pendingq.json'

try:
	with open(os.path.join(fileDir, pendingqfile)) as file:
			pendingq = json.load(file)
except:
	logger.warning("file pendingq was blank - please check if this is as expected")
	pendingq = {}

passwordqfile = 'passwordq.json'

try:
	with open(os.path.join(fileDir, passwordqfile)) as file:
			passwordq = json.load(file)
except:
	logger.warning("file passwordq was blank - please check if this is as expected")
	passwordq = {}

# ------ pronoun stuff ------

pronoundictfile = 'pronouns.json'

try:
	with open(os.path.join(fileDir, pronoundictfile)) as file:
			pronoundict = json.load(file)
except:
	logger.warning("file pronoundict was blank - please check if this is as expected")
	pronoundict = {}

# ------ predicates -------

#checks if the message is being sent privately
def is_PM():

	async def predicate(ctx):

		if not ctx.guild is None:
			await ctx.send("This command must be used in a private message.")
			return False
		return True

	return commands.check(predicate)

#checks whether or not a user has the 'staff' role
def is_staff():
	async def predicate(ctx):
		if not any(role.name == "staff" for role in ctx.message.author.roles) or not any(role.name == "moderator" for role in ctx.message.author.roles):
			await ctx.send("You must be a member of staff or a moderator to use this command.")
			return False
		return True
	return commands.check(predicate)

# ------ utility functions ------

def naturaltime(tis):

	tis = round(tis)

	if (tis > 60):
		tim = round(tis / 60)
		if (tim > 60):
			tih = round(tim / 60)
			return (str(tih) + " hours")
		else:
			return (str(tim) + " minutes")
	else:
		return (str(tis) + " seconds")

async def tatsu_score(member: commands.MemberConverter):
	stats = await tatsu.get_user_stats(priv.liveServer, member.id)
	score = stats['score']
	return int(score)

def contains_whitespace(s):
	return [c in s for c in string.whitespace]

# stuff that can only happen after on_ready()
async def init():
	#server
	global server
	if hdebug.hdebug:
		server = bot.get_guild(priv.testServer) #test server
	else:
		server = bot.get_guild(priv.liveServer) #alt+h server
	try:
		logger.info('got server: ' + server.name)
	except AttributeError:
		logger.warning('server not found')

	# channel ids
	#channel that bot prints mod alerts to
	global botlog
	try:
		botlog = bot.get_channel(settings['botlogID'])
	except:
		logger.warning("didn't find variable 'botlogID' in save file - reverting to server default")
		if hdebug.hdebug:
			botlog = bot.get_channel(priv.testBotlog)
		else:
			botlog = bot.get_channel(priv.liveBotlog)
		settings['botlogID'] = botlog.id

		with open(os.path.join(fileDir, settingsFile), "w") as file:
			json.dump(settings, file, indent=4)
	try:
		logger.info('got botlog channel: ' + botlog.name)
	except AttributeError:
		logger.warning('botlog channel not found')

	# channel that is used to hash things out with muted users
	global appeals
	try:
		appeals = bot.get_channel(settings['appealsID'])
	except:
		logger.warning("didn't find variable 'appealsID' in save file - reverting to server default")
		if hdebug.hdebug:
			appeals = bot.get_channel(priv.testAppeals)
		else:
			appeals = bot.get_channel(priv.liveAppeals)
		settings['appealsID'] = appeals.id

		with open(os.path.join(fileDir, settingsFile), "w") as file:
			json.dump(settings, file, indent=4)
	try:
		logger.info('got appeals channel: ' + appeals.name)
	except AttributeError:
		logger.warning('appeals channel not found')
