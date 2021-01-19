"""
modmail module

functions to allow users to anonymously message
the mod team

"""

import cfg #to enable referring to variables in cfg with the namespace prefix
from cfg import * #to enable calling things imported in cfg /without/ the namespace prefix

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
			await ctx.send(f"<:tick:534138088549646356> Sent message to staffroom as anon user {ticketName} ({webcolors.CSS3_NAMES_TO_HEX[ticketName]})")
			cfg.usertickets[authorKey]['messages'].append(msg.id)


	#dict gets edited either way so the dump happens outside of the if
	with open(os.path.join(cfg.fileDir, cfg.userticketsfile), "w") as file:
		json.dump(cfg.usertickets, file, indent=4)

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

	targetMessage = await cfg.modmail.fetch_message(message.reference.message_id)
	if (targetMessage.author.id == modmailWebhook.id):
		userID = None
		for u, v in cfg.usertickets.items():
			if targetMessage.id in v['messages']:
				 userID = u
				 break
		if userID == None:
			return

		user = cfg.server.get_member(int(userID))
		await user.send(f"""_**{message.author}** says:_
		{message.clean_content}""")
