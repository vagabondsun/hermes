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

cfg.bot.run(cfg.token)
