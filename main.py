import cfg #to enable referring to variables in cfg with the namespace prefix
from cfg import * #to enable calling things imported in cfg /without/ the namespace prefix


@cfg.bot.event
async def on_ready():
	await cfg.init()
	import verification
	import admin
	import pronouns
	import lookup
	import discourse
	logger.info('logged into {0.name} as {1.user}'.format(cfg.server, bot))
	vCheckLoop = bot.loop.create_task(verification.checkloop())

@cfg.bot.command()
async def ping(ctx):
	startTime = ctx.message.created_at
	pingTime = datetime.datetime.now() - startTime
	await ctx.send("Pong! :open_mouth: _(" + str(round(pingTime.microseconds/1000000, 3)) + " seconds)_")

@cfg.bot.listen('on_message')
async def salutation_message(message):
	#bot shouldn't reply to itself
	if message.author.id == cfg.bot.user.id:
		return

	m = cfg.salutations.match(message.content)
	if m != None:
		if m.group(1) == "hewwo":
			emoji = "<:crazy:678015749020975148> "
		elif m.group(2) == "everypony" or m.group(1) == "howdy":
			emoji = "<:cowhand:678015748723048506> "
		else:
			emoji = "<:blushing:678012723879084097> "
		await message.channel.send(emoji + (m.group(1) + ", " + message.author.display_name + "!").capitalize())

cfg.bot.run(cfg.token)
