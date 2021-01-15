"""
verification module

functions that handle users requesting access to the server,
assigning verification roles, and the security and anti-troll
measures related to this process

"""

import cfg #to enable referring to variables in cfg with the namespace prefix
from cfg import * #to enable calling things imported in cfg /without/ the namespace prefix

verified = discord.utils.find(lambda m: m.name == 'verified', cfg.server.roles)
if verified == None:
	logger.warning("could not find 'verified' role")

@cfg.bot.command()
@cfg.is_PM()
async def verify(ctx, *, voucher: commands.MemberConverter = None):

	member = cfg.server.get_member(ctx.author.id)

	if verified in member.roles:

		await ctx.send("<:thinking:534138088339931147> Looks like you're already verified - did you mean to ask for an opt-in channel role? These can only be given manually by mods.")

	elif any(request == str(member.id) for request in cfg.pendingq):

		req = None
		for requestID, request in cfg.passwordq.items():
			if request['user'] == member.id:
				req = request
				break

		timeDiff = datetime.datetime.utcnow() - req['timeSent']
		secondsTimeDiff = timeDiff / datetime.timedelta(seconds=1)

		await ctx.send("<:4_00:534138087731625994> You submitted a request " + cfg.naturaltime(secondsTimeDiff) + " ago.")

	elif any(request == str(member.id) for request in cfg.passwordq):

		await ctx.send("If you're having problems with submitting the passphrase, please contact a mod for help.")

	else:

		if not cfg.verifOpen:
			await ctx.send("Verification is currently closed - keep an eye on announcements to learn when it's open again <:eyes:534138088130215967>")

		else:

			if voucher != None: # if user specifies a username for voucher

				if cfg.vouchEnabled:

					voucherXP = await cfg.tatsu_score(voucher)
					logger.info("tatsu_score: " + str(voucherXP))
					if voucherXP < cfg.minVouchXP:
						await ctx.send("<:exclamation_question:534138088113569794> Looks like the user you specified doesn't have permission to vouch for new members.")
						return

					await ctx.send("Sent a message to **" + voucher.name + "** asking them to confirm.")
					await voucher.send("**" + member.name + "** is requesting access to the server and has specified you as a vouch. Can you confirm that you know this person and have agreed to vouch for them? (`!y`/`!n`)")

					def check(msg):
						return msg.content.startswith(("!y", "!n")) and msg.author == voucher

					resp = await bot.wait_for('message', check=check)

					if resp.content.startswith("!n"):
						await voucher.send("<:ok:534138088319090689><:no_entry:534138088545320971> **" + member.name + "** will not be verified.")
						await ctx.send("**" + voucher.name + "** has declined to vouch.")
						await cfg.botlog.send("**" + member.name + "** tried to request access with **" + voucher.name + "** as a vouch, but **" + voucher.name + "** declined.")
					elif resp.content.startswith("!y"):
						await ctx.send("<:ok_hand_hmn_y2:534138088373485618> **" + voucher.name + "** has confirmed their vouch.")
						await voucher.send("<:ok_hand_hmn_y2:534138088373485618> **" + member.name + "** will be verified immediately. _Please be aware that your ability to vouch for people will be removed if anyone you vouch for is banned or kicked._")

						await ctx.send("Now sending request to staffroom...")
						await build_request(ctx, voucher)

				else:
					await ctx.send("The vouch system currently isn't enabled. Please send `!verify` again if you'd like to submit a regular request.")

			else: # normal verif behaviour

					await ctx.send("Sending request...")
					await build_request(ctx)


async def build_request(ctx, vouch = None):

	vouchID = 0
	if vouch is not None:
		vouchID = vouch.id

	request = {'user':ctx.message.author.id, 'timeSent':datetime.datetime.utcnow().timestamp(), 'vouch':vouchID} #using UTC for accuracy here as datetime object is naieve
	cfg.requestq[str(ctx.message.author.id)] = request
	pprint.pprint(cfg.requestq)
	with open(os.path.join(cfg.fileDir, cfg.requestqfile), "w") as file:
		json.dump(cfg.requestq, file, indent=4)

async def checkqueues():

	logger.info("checking status of pending requests - currently " + str(len(cfg.pendingq)))
	#pending loop - people who have been approved and are waiting
	for requestID, request in cfg.pendingq.copy().items(): #using a temporary copy bc dicts can't change size while being iterated over

		member = cfg.server.get_member(request['user'])
		if member == None:
			await cfg.botlog.send("Can't find user with id `" + str(request['user']) + "` in the server any more. Their verification request will be dumped.")
			cfg.pendingq.pop(requestID)
			with open(os.path.join(cfg.fileDir, cfg.pendingqfile), "w") as file:
				json.dump(cfg.pendingq, file, indent=4)
			continue

		timeDiff = datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(request['timeSent'])
		secondsTimeDiff = timeDiff / datetime.timedelta(seconds=1)
		logger.info("it has been " + str(cfg.naturaltime(secondsTimeDiff)) + " since this submission was received")

		if secondsTimeDiff >= cfg.requiredTimeDiff:

			if cfg.passphrase == 'NONE': #skip passphrase request

				cfg.pendingq.pop(requestID)
				with open(os.path.join(cfg.fileDir, cfg.pendingqfile), "w") as file:
					json.dump(cfg.pendingq, file, indent=4)

				member = cfg.server.get_member(request['user'])
				if member == None:
					await cfg.botlog.send("Can't find user with id `" + str(request['user']) + "` in the server any more. Their verification request will be dumped.")
					return

				await member.add_roles(verified)
				await member.send("""<:tada:534138088541388810> You've been successfully verified!\nNow that you have access to the rest of the server you can:\n
				Consider saying hello in the <#257777353659383809> channel\n
				Assign yourself pronoun roles with roleypoly: <https://roleypoly.com/s/206742087562035202>\n

				\nEnjoy the server!""")
				await cfg.botlog.send("**" + member.name + "** has been verified.")

			else:
				await request_passphrase(request)

	logger.info("checking for sent requests - found " + str(len(cfg.requestq)))
	#request loop - people who have just sent !verify
	for requestID, request in cfg.requestq.copy().items(): #using a temporary copy bc dicts can't change size while being iterated over

		cfg.requestq.pop(requestID)
		with open(os.path.join(cfg.fileDir, cfg.requestqfile), "w") as file:
			json.dump(cfg.requestq, file, indent=4)

		member = cfg.server.get_member(request['user'])

		if member == None: #assume they've left
			return

		await member.send("Request recieved. Awaiting moderator response...")

		vouchtext = ''
		if request['vouch'] != 0:
			voucher = cfg.server.get_member(request['vouch'])
			vouchtext = (" and has been vouched for by **" + voucher.name + "**")

		await cfg.botlog.send("**" + member.name + "** is requesting access to the server" + vouchtext + ". Allow? _(`!y`/`!n`)_")

		def check(msg):
			return msg.content.startswith(("!y", "!n")) and msg.channel == botlog

		resp = await bot.wait_for('message', check=check)

		if resp.content.startswith("!y"):

			if request['vouch'] != 0:

				await cfg.botlog.send("**" + member.name + "** will be verified immediately.")
				await request_passphrase(request)

			else:

				await cfg.botlog.send("**" + member.name + "** will be verified at the end of the delay period.")
				await member.send("<:tick:534138088549646356> Your verification request has been approved. _It can take up to a day to process this_; you'll receive another message when it's done.")
				await member.send("""While you're waiting, check out the **Discord reference document** ({}) to familiarize yourself with the rules.""".format(cfg.refdoclink))

				cfg.pendingq[requestID] = request
				with open(os.path.join(cfg.fileDir, cfg.pendingqfile), "w") as file:
					json.dump(cfg.pendingq, file, indent=4)

		elif resp.content.startswith("!n"):
			await cfg.botlog.send("Please input a reason for denial _(Hermes will look for a message starting with `reason:`; send `!n` again to skip providing a reason.)_")

			def check(msg):
				return msg.content.startswith(("reason:", "!n")) and msg.channel == botlog

			resp = await bot.wait_for('message', check=check)

			if resp.content.startswith("reason:"):
				await member.send("You have been denied access to the Alt+H server. Reason given:" + resp.content[7:])
				await cfg.botlog.send("Sent reason to user.")

			elif resp.content.startswith("!n"):
				await member.send("You have been denied access to the Alt+H server.")
				await cfg.botlog.send("No reason for denial will be provided.")


async def request_passphrase(request):

	if request['vouch'] == 0: # only pop from the pending queue if not vouched for, requests with vouches bypass this so won't be in there
		cfg.pendingq.pop(str(request['user']))
		with open(os.path.join(cfg.fileDir, cfg.pendingqfile), "w") as file:
			json.dump(cfg.pendingq, file, indent=4)

	cfg.passwordq[request['user']] = request
	with open(os.path.join(cfg.fileDir, cfg.passwordqfile), "w") as file:
		json.dump(cfg.passwordq, file, indent=4)

	member = cfg.server.get_member(request['user'])
	if member == None:
		return

	await member.send("""<:exclamation_exclamation:534138087966638081> **Before we grant you access**, we need to confirm you've read the Discord Reference Document ({})
Please input the passphrase to complete verification.""".format(cfg.refdoclink))

	await cfg.botlog.send("Wait time for " + member.name + " elapsed; sending password request.")

@cfg.bot.listen('on_message')
async def pwd_message(message):
	if message.author.id == cfg.bot.user.id:
		return

	if message.content.lower().startswith(cfg.passphrase):

		member = cfg.server.get_member(message.author.id)
		if member == None:
			return

		req = None
		reqID = None
		inpasswordq = False
		inpendingq = False

		for requestID, request in cfg.pendingq.items():
			if request['user'] == member.id:
				req = request
				reqID = requestID
				inpendingq = True
				break

		if inpendingq:
			await member.send("<:ok_hand_hmn_y2:534138088373485618> Thank you for reading the rules! Hermes will ask you for the password at the end of the wait period.")
			return

		for requestID, request in cfg.passwordq.items():
			if request['user'] == member.id:
				req = request
				reqID = requestID
				inpasswordq = True
				break

		if inpasswordq:
			await member.add_roles(verified)
			await member.send("<:tada:534138088541388810> You've been successfully verified. Enjoy the server!")
			await cfg.botlog.send("**" + member.name + "** has been verified.")

			cfg.passwordq.pop(reqID)
			with open(os.path.join(cfg.fileDir, cfg.passwordqfile), "w") as file:
				json.dump(cfg.passwordq, file, indent=4)

## caller for the verification task loop ##
async def checkloop():

	while not bot.is_closed():

		logger.info("checking for sent requests - found " + str(len(cfg.requestq)))
		await checkqueues()
		await asyncio.sleep(cfg.verificationCheckPeriod)
