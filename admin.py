"""
admin module

functions that help with administrative tasks as well as
functions for allowing configuration of the bot through
bot commands

"""

import cfg #to enable referring to variables in cfg with the namespace prefix
from cfg import * #to enable calling things imported in cfg /without/ the namespace prefix

@cfg.bot.command()
@cfg.is_staff()
async def die(ctx):
	await ctx.send("<:exclamation_exclamation:534138087966638081> Are you sure you want to shut down Hermes?")

	def check(msg):
		return msg.content.startswith(("!y", "!n")) and msg.channel == ctx.channel and msg.author == ctx.author

	resp = await bot.wait_for('message', check=check)

	if resp.content.startswith("!y"):
		await ctx.send("<:ok:534138088319090689> <:dead:534144868927275068> Hermes will now shut down.")
		await cfg.bot.logout()
		cfg.settings.close()
		exit()
	elif resp.content.startswith("!n"):
		await ctx.send("<:ok:534138088319090689> <:weary:534147756407652361>")

@cfg.bot.group(aliases=['cfg', 'configure'])
@cfg.is_staff()
async def config(ctx):
	return

@config.group(aliases=['refdoc', 'refdoclink', 'doclink', 'docurl'])
@cfg.is_staff()
async def refdocurl(ctx, url):
	cfg.settings['refdoclink'] = "<"+url+">"
	await ctx.send("Set refdoc link to " + cfg.settings['refdoclink'])

	with open(os.path.join(cfg.fileDir, cfg.settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

@config.group(aliases=['view','check','list'])
@cfg.is_staff()
async def display(ctx):
	displaystring = "```"
	for setting, value in cfg.settings.copy().items():
		displaystring += (setting+":").ljust(30)
		displaystring += (str(value)+"\n")
	displaystring += "```"
	await ctx.send(displaystring)

@config.group()
@cfg.is_staff()
async def channel(ctx):
	return

@channel.command(name='set')
@cfg.is_staff()
async def channel_set(ctx, channelType, value: commands.TextChannelConverter):
	if channelType == "botlog":
		cfg.botlog = bot.get_channel(value.id)
		cfg.settings['botlogID'] = cfg.botlog.id
		await ctx.send("<:ok:534138088319090689> Set bot log channel to " + value.mention)
	elif channelType == "appeals":
		cfg.appeals = bot.get_channel(value.id)
		cfg.settings['appealsID'] = cfg.appeals.id
		await ctx.send("<:ok:534138088319090689> Set appeals channel to " + value.mention)

	with open(os.path.join(cfg.fileDir, cfg.settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

@channel.command(name='check')
@cfg.is_staff()
async def channel_check(ctx, option=None):
	if option == "botlog":
		await cfg.botlog.send("<:arms_in_the_air_y2:534138087517716481> " + ctx.message.author.mention + ", this is the channel currently configured to receive bot messages.")
	elif option == "appeals":
		await cfg.appeals.send("<:arms_in_the_air_y2:534138087517716481> " + ctx.message.author.mention + ", this is the channel currently configured to receive muted members.")
	else:
		await ctx.send("The bot is currently sending notifications to " + cfg.botlog.mention + "\nMuted members are currently sent to " + cfg.appeals.mention)

## verification variable config ##

@config.group(aliases=['v', 'verif'])
@cfg.is_staff()
async def verification(ctx):
	return

@verification.command(name='open', aliases=['toggleopen', 'closed', 'toggledclosed'])
@cfg.is_staff()
async def verif_open(ctx):
	cfg.verifOpen = not cfg.verifOpen

	if cfg.verifOpen:
		await ctx.send("Verification is now open.")
	else:
		await ctx.send("Verification is now closed.")

	with open(os.path.join(cfg.fileDir, cfg.settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

@verification.command(aliases=['delay', 'wait'])
@cfg.is_staff()
async def timer(ctx, value: int):
	cfg.requiredTimeDiff = value
	cfg.settings['requiredTimeDiff'] = cfg.requiredTimeDiff
	await ctx.send("<:ok:534138088319090689> Set verification delay time to " + naturaltime(value) + ".")

	with open(os.path.join(cfg.fileDir, cfg.settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

@verification.command(aliases=['check', 'checktimer'])
@cfg.is_staff()
async def checkperiod(ctx, value: int):
	cfg.verificationCheckPeriod = value
	cfg.settings['verificationCheckPeriod'] = cfg.verificationCheckPeriod
	await ctx.send("<:ok:534138088319090689> Set queue check frequency to every " + naturaltime(value) + ".")

	with open(os.path.join(cfg.fileDir, cfg.settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

@verification.command(aliases=['pw', 'pass', 'passphrase', 'passcode'])
@cfg.is_staff()
async def password(ctx, value):
	cfg.passphrase = value
	cfg.settings['passphrase'] = cfg.passphrase
	if value == 'NONE':
		await ctx.send("<:ok:534138088319090689> **Disabled passphrase.** Users will not be prompted to enter anything before being verified.")
	else:
		await ctx.send("<:ok:534138088319090689> Set verification passphrase to `" + value + "`.")

	with open(os.path.join(cfg.fileDir, cfg.settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

@verification.command(aliases=['minvouchrole', 'minvouch', 'vouchrole', 'vouch'])
@cfg.is_staff()
async def min_vouch_role(ctx, value: commands.RoleConverter):
	cfg.minVouchRole = value.id
	cfg.settings['minVouchRole'] = cfg.minVouchRole
	await ctx.send("<:ok:534138088319090689> Set minimum vouch role to `" + value.name + "`.")

	with open(os.path.join(cfg.fileDir, cfg.settingsFile), "w") as file:
		json.dump(settings, file, indent=4)

## other verification tools ##

@cfg.bot.group()
@cfg.is_staff()
async def pending(ctx):
	return

@pending.command(name='check', aliases=['list'])
@cfg.is_staff()
async def pending_check(ctx):
	if cfg.pendingq: #only build the message if the list has things in it
		pending = "The following people are in the verification queue:"
		for requestID, request in cfg.pendingq.copy().items():
			member = cfg.server.get_member(request['user'])
			if member == None:
				await cfg.botlog.send("Can't find user with id `" + str(request['user']) + "` in the server any more. Their verification request will be dumped.")
				cfg.pendingq.pop(requestID)
				cfg.settings['pendingq'] = cfg.pendingq
				continue

			timeDiff = datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(request['timeSent'])
			secondsTimeDiff = timeDiff / datetime.timedelta(seconds=1)
			pending += ("\n**" + member.name + "** submitted a request " + cfg.naturaltime(secondsTimeDiff) + " ago.")

		await ctx.send(pending)

	if cfg.passwordq: #same as above
		pending = "Passwords are pending from the following people:"
		for requestID, request in cfg.passwordq.copy().items():
			member = cfg.server.get_member(request['user'])
			if member == None:
				await cfg.botlog.send("Can't find user with id `" + str(request['user']) + "` in the server any more. Their verification request will be dumped.")
				cfg.passwordq.pop(requestID)
				cfg.settings['passwordq'] = cfg.passwordq
				continue

			pending += ("\n**" + member.name + "**")
		await ctx.send(pending)

	if not cfg.pendingq and not cfg.passwordq:
		await ctx.send("There are currently no pending requests.")

@pending.command(name='flush')
@cfg.is_staff()
async def pending_flush(ctx, listname):
	await cfg.botlog.send("<:exclamation_mark_red:534138087828226081> Are you sure you want to flush all entries from " + listname + " list?")

	def check(msg):
		return msg.content.startswith(("!y", "!n")) and msg.channel == ctx.channel and msg.author == ctx.author

	resp = await bot.wait_for('message', check=check)

	if resp.content.startswith("!y"):
		if listname == 'pending':
			cfg.pendingq = {}

			with open(os.path.join(cfg.fileDir, cfg.pendingqfile), "w") as file:
				json.dump(cfg.pendingq, file, indent=4)

		elif listname == 'password':
			cfg.passwordq = {}

			with open(os.path.join(cfg.fileDir, cfg.passwordqfile), "w") as file:
				json.dump(cfg.passwordq, file, indent=4)

		elif listname == 'request':
			cfg.requestq = {}

			with open(os.path.join(cfg.fileDir, cfg.requestqfile), "w") as file:
				json.dump(cfg.requestq, file, indent=4)

		elif listname == 'all':
			cfg.pendingq = {}
			cfg.passwordq = {}
			cfg.requestq = {}

			with open(os.path.join(cfg.fileDir, cfg.pendingqfile), "w") as file:
				json.dump(cfg.pendingq, file, indent=4)
			with open(os.path.join(cfg.fileDir, cfg.passwordqfile), "w") as file:
				json.dump(cfg.passwordq, file, indent=4)
			with open(os.path.join(cfg.fileDir, cfg.requestqfile), "w") as file:
				json.dump(cfg.requestq, file, indent=4)

		await cfg.botlog.send("<:ok:534138088319090689> Flushed " + listname + " list.")
	elif resp.content.startswith("!n"):
		await ctx.send("<:ok:534138088319090689> Cancelled action.")

@pending.command(name='remove')
@cfg.is_staff()
async def pending_remove(ctx, user: commands.MemberConverter, listname):
	if listname == 'pending':
		if any(request == str(user.id) for request in cfg.pendingq):
			cfg.pendingq.pop(str(user.id))
			with open(os.path.join(cfg.fileDir, cfg.pendingqfile), "w") as file:
				json.dump(cfg.pendingq, file, indent=4)

			await ctx.send("Removed user from pending list.")
		else:
			await ctx.send("<:question_mark_red:534138088478212096> User isn't in pending list.")

	elif listname == 'password':
		if any(request == str(user.id) for request in cfg.passwordq):
			cfg.passwordq.pop(str(user.id))
			with open(os.path.join(cfg.fileDir, cfg.passwordqfile), "w") as file:
				json.dump(cfg.passwordq, file, indent=4)

			await ctx.send("Removed user from password list.")

		else:
			await ctx.send("<:question_mark_red:534138088478212096> User isn't in password list.")

	elif listname == 'request':
		if any(request == str(user.id) for request in cfg.requestq):
			cfg.requestq.pop(str(user.id))
			with open(os.path.join(cfg.fileDir, cfg.requestqfile), "w") as file:
				json.dump(cfg.requestq, file, indent=4)

			await ctx.send("Removed user from request list.")

		else:
			await ctx.send("<:question_mark_red:534138088478212096> User isn't in request list.")

@cfg.bot.command()
@cfg.is_staff()
async def mute(ctx, user):
	role = discord.utils.find(lambda m: m.name == "mature access", cfg.server.roles)
	if not (role is None):
		await user.remove_roles(role)

	role = discord.utils.find(lambda m: m.name == "debate access", cfg.server.roles)
	if not (role is None):
		await user.remove_roles(role)

	role = discord.utils.find(lambda m: m.name == "research access", cfg.server.roles)
	if not (role is None):
		await user.remove_roles(role)

	role = discord.utils.find(lambda m: m.name == "body_expression access", cfg.server.roles)
	if not (role is None):
		await user.remove_roles(role)

	role = discord.utils.find(lambda m: m.name == "verified_muted", cfg.server.roles)
	await user.add_roles(role)

	role = discord.utils.find(lambda m: m.name == "verified", cfg.server.roles)
	await user.remove_roles(role)

	channel = discord.utils.find(lambda m: m.id == cfg.appeals, cfg.server.channels)
	await cfg.appeals.send(user.mention + ", you have been muted, as a staff member has determined that your behaviour in the chat is currently actively damaging the wellbeing of our users and the chat environment. **This is not a kick or a ban;** you've been given access to this channel so that we can talk the issue out with you away from the main server. If it gets sorted out satisfactorily, you'll be unmuted again.")

@cfg.bot.command()
@cfg.is_staff()
async def hackban(ctx, uuid):
	await cfg.server.ban(discord.Object(id=uuid))
	await ctx.send("Added user with ID " + str(uuid) + " to banlist.")

## debug ##

@cfg.bot.command()
@cfg.is_staff()
async def exception(ctx):
	raise Exception('uh oh!')
	await ctx.send("Raised an exception. You should get an email about this")
