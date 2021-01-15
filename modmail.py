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

	if ctx.author.id in cfg.usertickets:
		ticketName = cfg.usertickets[ctx.author.id]['color']
		cfg.usertickets[ctx.author.id]['lastSent'] = datetime.datetime.utcnow().timestamp()
		await ctx.message.add_reaction("<:tick:534138088549646356>")
	else:
		ticketName = random.choice(list(webcolors.CSS3_NAMES_TO_HEX.keys()))
		cfg.usertickets[ctx.author.id] = { 'color': ticketName, 'lastSent' : datetime.datetime.utcnow().timestamp() }
		await ctx.send(f"<:tick:534138088549646356> Sent message to staffroom as anon user {ticketName} ({webcolors.CSS3_NAMES_TO_HEX[ticketName]})")

	#dict gets edited either way so the dump happens outside of the if
	with open(os.path.join(cfg.fileDir, cfg.userticketsfile), "w") as file:
		json.dump(cfg.usertickets, file, indent=4)

	cfg.modmailWebhook.send(message, username=ticketName)

@cfg.bot.command()
@cfg.is_staff()
async def testwebhook(ctx, name='nothing'):
	if not name in webcolors.CSS3_NAMES_TO_HEX:
		await cfg.modmailWebhook.send("Modmail webhook is working, but you didn't specify a valid CSS3 webcolor.", username="Modmail test")
	else:
		cfg.generateColorImg(name)
		cfg.modmailWebhook.send("Modmail webhook is working!", username=name.capitalize(), avatar_url="https://localhost/home/mordev/Desktop/hermes/"+name+".png")

@cfg.bot.listen('on_message')
async def reply_to_webook(message):
	if message.reference is not None:
		pass
