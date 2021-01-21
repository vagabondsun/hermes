"""
modmail module

functions to allow users to anonymously message
the mod team

"""

import cfg #to enable referring to variables in cfg with the namespace prefix
from cfg import * #to enable calling things imported in cfg /without/ the namespace prefix

async def get_webhook_user(msgID):

	targetMessage = await cfg.modmail.fetch_message(msgID)
	if (targetMessage.author.id == modmailWebhook.id):
		ticketName = None
		for u, v in cfg.usertickets.items():
			if targetMessage.id in v['messages']:
				 return u

	await cfg.modmail.send("Couldn't find a user associated with that webhook.")

async def checktickets():
	for u, v in cfg.usertickets.copy().items():
		timeDiff = datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(v['lastSent'])
		secondsTimeDiff = timeDiff / datetime.timedelta(seconds=1)

		try:
			temp = cfg.usertickets[u]['destroy']
		except:
			if secondsTimeDiff >= cfg.ticketExpiryPeriod:
				user = cfg.server.get_member(v['user'])
				await user.send(f"Your color association with {u} has expired. Next time you send a message, a new one will be selected for you <:artist_palette:801099935322865725>")
				logger.info(f"cleaning naturally expired ticket {u}")
				cfg.usertickets.pop(u)
		else:
			#if the user has already detached from the color, they don't need to know it's being cleaned up
			cfg.usertickets.pop(u)
			logger.info(f"cleaning revealed detached ticket {u}")

		with open(os.path.join(cfg.fileDir, cfg.userticketsfile), "w") as file:
			json.dump(cfg.usertickets, file, indent=4)

@cfg.is_PM()
@cfg.bot.command()
async def detach(ctx): #remove color association

	for u, v in cfg.usertickets.copy().items():
		if v['user'] == ctx.author.id:
			try:
				temp = cfg.usertickets[u]['detached']
			except:
				cfg.usertickets[u]['detached'] = True
				await ctx.send("<:tick:534138088549646356> Removed your color association. Next time you send a message, a new one will be selected for you <:artist_palette:801099935322865725>")
				with open(os.path.join(cfg.fileDir, cfg.userticketsfile), "w") as file:
					json.dump(cfg.usertickets, file, indent=4)
				return

	await ctx.send("<:thinking:534138088339931147> It looks like you're not associated with a color name right now.")

@cfg.is_PM()
@cfg.bot.command()
async def tell(ctx, *, message : commands.clean_content):

	ticketName = None
	for u, v in cfg.usertickets.copy().items():
		if v['user'] == ctx.author.id:
			try:
				temp = v['detached'] #test if detached flag
			except:
				ticketName = u #if it doesn't, we're done searching
				break
			else:
				continue #if it does, skip

	if not ticketName == None:
		cfg.usertickets[ticketName]['lastSent'] = datetime.datetime.utcnow().timestamp()
		try:
			msg = cfg.modmailWebhook.send(message, username=ticketName.capitalize(), avatar_url=f"https://www.colorhexa.com/{webcolors.CSS3_NAMES_TO_HEX[ticketName][1:]}.png", wait=True) #wait allows the message to be returned
		except:
			await ctx.send("<:cross:534138087534755861> Your message could not be sent. Please try again, and if the error persists, let a member of staff know.")
		else:
			await ctx.message.add_reaction("<:tick:534138088549646356>")
			cfg.usertickets[ticketName]['messages'].append(msg.id)
	else:
		if len(cfg.usertickets) == 140:
			await ctx.message.add_reaction("<:surprised:534138088398651403> Somehow, it seems like all 140 color names are in use right now. This is probably a bug, so please consider telling a mod about it.")
			return

		ticketName = random.choice(list(webcolors.CSS3_NAMES_TO_HEX.keys()))
		while ticketName in cfg.usertickets:
			ticketName = random.choice(list(webcolors.CSS3_NAMES_TO_HEX.keys())) #if you pick a name already in use, reroll

		cfg.usertickets[ticketName] = { 'user': ctx.author.id, 'lastSent' : datetime.datetime.utcnow().timestamp(), 'messages' : [] }
		try:
			msg = cfg.modmailWebhook.send(message, username=ticketName.capitalize(), avatar_url=f"https://www.colorhexa.com/{webcolors.CSS3_NAMES_TO_HEX[ticketName][1:]}.png", wait=True)  #wait allows the message to be returned
		except:
			await ctx.send("<:cross:534138087534755861> Your message could not be sent. Please try again, and if the error persists, let a member of staff know.")
			cfg.usertickets.pop(ticketName)
		else:
			await ctx.send(f"<:tick:534138088549646356> Sent message to staffroom as anon user {ticketName} ({webcolors.CSS3_NAMES_TO_HEX[ticketName]}) <:artist_palette:801099935322865725>")
			cfg.usertickets[ticketName]['messages'].append(msg.id)


	#dict gets edited either way so the dump happens outside of the if
	with open(os.path.join(cfg.fileDir, cfg.userticketsfile), "w") as file:
		json.dump(cfg.usertickets, file, indent=4)

@tell.error
async def on_command_error(ctx, error):

	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("<:envelope_with_arrow:534138087958249489><:exclamation_question:534138088113569794> You need to include a message to send!")

@cfg.bot.command()
@cfg.is_staff()
async def testwebhook(ctx, name='nothing'):
	if not name in webcolors.CSS3_NAMES_TO_HEX:
		await cfg.modmailWebhook.send("Modmail webhook is working, but you didn't specify a valid CSS3 webcolor.", username="Modmail test")
	else:
		cfg.modmailWebhook.send(f"Modmail webhook is working! Proxying as {name}", username=name.capitalize(), avatar_url=f"https://www.colorhexa.com/{webcolors.CSS3_NAMES_TO_HEX[name][1:]}.png")

@cfg.bot.command()
@cfg.is_staff()
async def activewebhooks(ctx):
	activeWebhooks = "<:bookmark:534138087874363392><:artist_palette:801099935322865725> The following colors are currently in use:\n"

	for u, v in cfg.usertickets.items():
		activeWebhooks += f"**{v['color'].capitalize()}**\n"

	await ctx.send(activeWebhooks)

@cfg.bot.listen('on_message')
async def reply_to_webook(message):
	if message.author.id != cfg.modmailWebhook.id or message.reference is None:
		return

	ticketName = await get_webhook_user(message.reference.message_id)
	targetUser = cfg.server.get_member(cfg.usertickets[ticketName]['user'])

	if targetUser is None:
		await message.channel.send("<:cross:534138087534755861> There is no user currently associated with that webhook.")
		return

	try:
		await targetUser.send(f"""_**{message.author}** says:_
{message.clean_content}""")
	except:
		await message.channel.send("<:cross:534138087534755861> Your message could not be sent. Please try again, and if the error persists, let mord know.")
	else:
		await message.add_reaction("<:tick:534138088549646356>")

@cfg.bot.listen('on_raw_reaction_add')
async def reveal_user(reaction):

	targetMessage = await cfg.modmail.fetch_message(reaction.message_id)

	if not (reaction.channel_id == cfg.modmail.id and reaction.emoji.name == u"\U00002753" and targetMessage.author.id == cfg.modmailWebhook.id):
		return

	ticketName = await get_webhook_user(reaction.message_id)
	targetUser = cfg.server.get_member(cfg.usertickets[ticketName]['user'])

	await cfg.modmail.send("<:exclamation_exclamation:534138087966638081> You must specify a reason for revealing the user. Hermes will look for a message starting with `reason:`; to cancel send `!cancel`")

	def check(msg):
		return msg.content.startswith(("!cancel", "reason:")) and msg.channel == cfg.modmail

	resp = await bot.wait_for('message', check=check)

	if resp.content.startswith("reason:"):
		try:
			await targetUser.send("<:exclamation_exclamation:534138087966638081> The mod team has decided to reveal your username. Reason given:" + resp.content[7:])
		except discord.errors.Forbidden:
			await cfg.modmail.send("It seems like **" + targetUser.name + "** has DMs from server members disabled. Their username will still be revealed, but they can't be notified.")
	elif resp.content.startswith("!cancel"):
		await cfg.modmail.send("<:ok:534138088319090689> Cancelled revealing username.")
		return

	try:
		temp = cfg.usertickets[ticketName]['detached'] # https://docs.python.org/2/glossary.html#term-eafp
	except KeyError:
		await cfg.modmail.send(f"The **{ticketName}** webhook is currently associated with **{targetUser.display_name} ({targetUser.name})**")
	else:
		await cfg.modmail.send(f"The **{ticketName}** webhook was associated with **{targetUser.display_name} ({targetUser.name})**, but has been detached. It will be cleaned up the next time the expired tickets checker runs.")
		cfg.usertickets[ticketName]['destroy'] = True
		with open(os.path.join(cfg.fileDir, cfg.userticketsfile), "w") as file:
			json.dump(cfg.usertickets, file, indent=4)

## caller for the verification task loop ##
async def checkloop():

	while not bot.is_closed():

		logger.debug("checking for expired modmail tickets")
		await checktickets()
		await asyncio.sleep(cfg.checkPeriod)
