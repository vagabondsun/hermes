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
		userID = None
		for u, v in cfg.usertickets.items():
			if targetMessage.id in v['messages']:
				 userID = u
				 break
		if userID == None:
			return

		user = cfg.server.get_member(int(userID))
		if not user is None:
			return user
		else:
			await cfg.modmail.send("Couldn't find a user associated with that webhook.")


@cfg.is_PM()
@cfg.bot.command()
async def detach(ctx): #remove color association

	authorKey = str(ctx.author.id)
	if authorKey in cfg.usertickets:
		cfg.usertickets.pop(authorKey)
		await ctx.send("<:tick:534138088549646356> Removed your color association. Next time you send a message, a new one will be selected for you <:artist_palette:801099935322865725>")

@cfg.is_PM()
@cfg.bot.command()
async def tell(ctx, *, message : commands.clean_content):

	authorKey = str(ctx.author.id)
	if authorKey in cfg.usertickets:
		ticketName = cfg.usertickets[authorKey]['color']
		cfg.usertickets[authorKey]['lastSent'] = datetime.datetime.utcnow().timestamp()
		try:
			msg = cfg.modmailWebhook.send(message, username=ticketName.capitalize(), avatar_url=f"https://www.colorhexa.com/{webcolors.CSS3_NAMES_TO_HEX[ticketName][1:]}.png", wait=True) #wait allows the message to be returned
		except:
			await ctx.send("<:cross:534138087534755861> Your message could not be sent. Please try again, and if the error persists, let a member of staff know.")
		else:
			await ctx.message.add_reaction("<:tick:534138088549646356>")
			cfg.usertickets[authorKey]['messages'].append(msg.id)
	else:
		ticketName = random.choice(list(webcolors.CSS3_NAMES_TO_HEX.keys()))
		cfg.usertickets[authorKey] = { 'color': ticketName, 'lastSent' : datetime.datetime.utcnow().timestamp(), 'messages' : [] }
		try:
			msg = cfg.modmailWebhook.send(message, username=ticketName.capitalize(), avatar_url=f"https://www.colorhexa.com/{webcolors.CSS3_NAMES_TO_HEX[ticketName][1:]}.png", wait=True)  #wait allows the message to be returned
		except:
			await ctx.send("<:cross:534138087534755861> Your message could not be sent. Please try again, and if the error persists, let a member of staff know.")
			cfg.usertickets.pop(authorKey)
		else:
			await ctx.send(f"<:tick:534138088549646356> Sent message to staffroom as anon user {ticketName} ({webcolors.CSS3_NAMES_TO_HEX[ticketName]}) <:artist_palette:801099935322865725>")
			cfg.usertickets[authorKey]['messages'].append(msg.id)


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
		cfg.modmailWebhook.send(f"Modmail webhook is working! Proxying as {name} ({webcolors.CSS3_NAMES_TO_HEX[name]})", username=name.capitalize(), avatar_url=f"https://www.colorhexa.com/{webcolors.CSS3_NAMES_TO_HEX[name][1:]}.png")

@cfg.bot.listen('on_message')
async def reply_to_webook(message):
	if message.reference is None:
		return

	user = await get_webhook_user(message.reference.message_id)

	try:
		await user.send(f"""_**{message.author}** says:_
		{message.clean_content}""")
	except:
		await message.channel.send("<:cross:534138087534755861> Your message could not be sent. Please try again, and if the error persists, let mord know.")
	else:
		await message.add_reaction("<:tick:534138088549646356>")

@cfg.bot.listen('on_raw_reaction_add')
async def reveal_user(reaction):

	logger.info("a")

	if not (reaction.channel_id == cfg.modmail.id and reaction.emoji.name == u"\U00002753"):
		logger.info("b")
		return

	logger.info("c")
	targetUser = await get_webhook_user(reaction.message_id)
	colorName = cfg.usertickets[str(targetUser.id)]['color']

	await cfg.modmail.send(f"""The **{colorName}** webhook is currently attached to **{targetUser.display_name} ({targetUser.name})**""")
