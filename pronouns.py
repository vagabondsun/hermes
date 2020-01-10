"""

pronouns module

handles the assignment of pronoun roles

"""

import cfg #to enable referring to variables in cfg with the namespace prefix
from cfg import * #to enable calling things imported in cfg /without/ the namespace prefix

@cfg.bot.group(aliases=['pronoun', 'prn'])
async def pronouns(ctx):
	return

# detects roles on the server without corresponding dict entries and prompts
# the user to create them
@pronouns.command()
@cfg.is_staff()
async def sync(ctx):

	regex = cfg.re.compile(r'\w+\/\w+/\w+')
	roleindex = 0
	for role in cfg.server.roles:
		if re.match(regex, role.name) and role.name not in cfg.pronoundict.keys():
			name = role.name
			await ctx.send("Role `" + name + "` not found in dict. Please input full declension (or `!ignore` to skip)")

			def check(msg):
				return re.match("^.+(?:[\s\/].+){4}(self|selves)$", msg.content) and msg.channel == ctx.channel and msg.author == ctx.author

			msg = await cfg.bot.wait_for('message', check=check, timeout=300)
			pronstring = msg.content.replace(" ", "/")
			cfg.pronoundict[role.name] = pronstring
			roleindex += 1

	with open(os.path.join(cfg.fileDir, cfg.pronoundictfile), "w") as file:
		json.dump(cfg.pronoundict, file, indent=4, sort_keys=True)
	if roleindex == 0:
		await ctx.send("<:arms_in_the_air_y2:534138087517716481> Roles already synced!")
	else:
		await ctx.send("Added " + str(roleindex) + " roles.")

@pronouns.command()
async def list(ctx):
	await list_(ctx)

async def list_(ctx):

	await ctx.send("<:bookmark:534138087874363392> These are the registered pronoun roles:")

	pList = "```"

	roleindex = 1
	for rolename, set in cfg.pronoundict.items():
		pList += "\n" + str(roleindex) + ") " + set
		roleindex += 1

	pList += "```"

	await ctx.send(pList)

@pronouns.command(aliases=['create', 'addnew', 'createnew'])
async def new(ctx, *, newset=None):

	if newset is not None:
		if not re.match("^.+(?:[\s\/].+){4}(self|selves)$", newset):
			await ctx.send("<:exclamation_mark_red:534138087828226081> Pronoun set must be in the format: `they/them/their/theirs/themselves`. The reflexive form must end in -self or -selves.")
			return
		else:
			await new_r(ctx, newset)
	else:
		await ctx.send("Please input the new pronoun set in the format: `they/them/their/theirs/themselves`. The reflexive form must end in -self or -selves.")

		def check(msg):
			return re.match("^.+(?:[\s\/].+){4}(self|selves)$", msg.content) and msg.channel == ctx.channel and msg.author == ctx.author

		msg = await cfg.bot.wait_for('message', check=check, timeout=300)
		newset = msg.content

		await new_r(ctx, newset)

async def new_r(ctx, newset):
	pronstring = newset.replace(" ", "/")
	groups = pronstring.split('/')
	rolename = '/'.join(groups[:3])

	if rolename in cfg.pronoundict:
		await ctx.send(" <:exclamation_mark_red:534138087828226081> A role named `" + rolename + "` already exists. Would you like to assign yourself this role? (`!y`|`!retype`|`!cancel`)")

		def check(msg):
			return re.match("^(!y|!retype|!cancel)$", msg.content) and msg.channel == ctx.channel and msg.author == ctx.author

		msg = await cfg.bot.wait_for('message', check=check, timeout=300)

		if msg.content.startswith("!y"):
			role = discord.utils.find(lambda m: m.name == rolename, cfg.server.roles)
			member = cfg.server.get_member(ctx.author.id)
			await member.add_roles(role)

			await ctx.send("<:ok_hand_hmn_y2:534138088373485618> Gave you role `" + rolename + "`.")

		elif msg.content.startswith("!retype"):
			await ctx.send("Please input the new pronoun set in the format: `they/them/their/theirs/themselves`. The reflexive form must end in -self or -selves.")

			def check(msg):
				return re.match("^.+(?:[\s\/].+){4}(self|selves)$", msg.content) and msg.channel == ctx.channel and msg.author == ctx.author

			msg = await cfg.bot.wait_for('message', check=check, timeout=300)
			newset = msg.content

			await new_r(ctx, newset)

		elif msg.content.startswith("!cancel"):
			await ctx.send("<:ok:534138088319090689> Cancelled adding pronoun role.")
			return
	else:
		await ctx.send("This will create a role named `" + rolename + "`. Is this okay? (`!y`|`!retype`|`!cancel`)")

		def check(msg):
			return re.match("^(!y|!retype|!cancel)$", msg.content)

		msg = await cfg.bot.wait_for('message', check=check, timeout=300)

		if msg.content.startswith("!y"):
			await cfg.server.create_role(name=rolename)
			cfg.pronoundict[rolename] = pronstring
			with open(os.path.join(cfg.fileDir, cfg.pronoundictfile), "w") as file:
				json.dump(cfg.pronoundict, file, indent=4, sort_keys=True)

			await ctx.send("<:tick:534138088549646356> Created role `" + rolename + "`. Would you like to assign this role to yourself now? (`!y`|`!n`)")

			def check(msg):
				return re.match("^(!y|!n)$", msg.content) and msg.channel == ctx.channel and msg.author == ctx.author

			msg = await cfg.bot.wait_for('message', check=check, timeout=300)

			if msg.content.startswith("!y"):
				role = discord.utils.find(lambda m: m.name == rolename, cfg.server.roles)
				member = cfg.server.get_member(ctx.author.id)
				await member.add_roles(role)
				await ctx.send("<:ok_hand_hmn_y2:534138088373485618> Gave you role `" + rolename + "`.")

			elif msg.content.startswith("!n"):
				await ctx.send("<:ok_hand_hmn_y2:534138088373485618> Will not give you role `" + rolename + "`.")

		elif msg.content.startswith("!retype"):
			await ctx.send("Please input the new pronoun set in the format: `they/them/their/theirs/themselves`. The reflexive form must end in -self or -selves.")

			def check(msg):
				return re.match("^.+(?:[\s\/].+){4}(self|selves)$", msg.content) and msg.channel == ctx.channel and msg.author == ctx.author

			msg = await cfg.bot.wait_for('message', check=check, timeout=300)
			newset = msg.content

			await new_r(ctx, newset)

		elif msg.content.startswith("!cancel"):
			await ctx.send("<:ok:534138088319090689> Cancelled creating pronoun role.")
			return

@pronouns.command(aliases=['give', 'giveme', 'assign', 'get'])
async def add(ctx, *, rolename=None):

	if rolename is not None:
		role = discord.utils.find(lambda m: m.name == rolename, cfg.server.roles)
		if role == None:
			await ctx.send("<:thinking:534138088339931147> Doesn't look like there's a pronoun role with that name.")
		else:
			member = cfg.server.get_member(ctx.author.id)
			await member.add_roles(role)
			await ctx.send("<:ok_hand_hmn_y2:534138088373485618> Gave you role `" + rolename + "`.")
	else:
		await list_(ctx)
		await ctx.send("Please enter a number from the list above.")

		def check(msg):
			return re.match("^\d+$", msg.content) and msg.channel == ctx.channel and msg.author == ctx.author

		msg = await cfg.bot.wait_for('message', check=check, timeout=300)

		for i, key in enumerate(cfg.pronoundict.keys(), 1):
			if i == int(msg.content):
				rolename = key

		role = discord.utils.find(lambda m: m.name == rolename, cfg.server.roles)
		member = cfg.server.get_member(ctx.author.id)
		await member.add_roles(role)
		await ctx.send("<:ok_hand_hmn_y2:534138088373485618> Gave you role `" + rolename + "`.")

@pronouns.command()
async def remove(ctx, *, rolename=None):

	member = cfg.server.get_member(ctx.author.id)
	if rolename is not None:
		role = discord.utils.find(lambda m: m.name == rolename, cfg.server.roles)
		if role not in member.roles:
			await ctx.send("<:thinking:534138088339931147> Doesn't look like you have a pronoun role with that name.")
		else:
			await member.remove_roles(role)
			await ctx.send("<:ok_hand_hmn_y2:534138088373485618> Removed role `" + rolename + "`.")
	else:
		await ctx.send("<:bookmark:534138087874363392> These are the roles you currently have:")

		pList = "```"

		roleindex = 1
		list = []
		for rolename, set in cfg.pronoundict.items():
			if any(rolename == role.name for role in member.roles):
				list.append(rolename)
				pList += "\n" + str(roleindex) + ") " + rolename
				roleindex += 1

		pList += "```"

		await ctx.send(pList)
		await ctx.send("Please enter a number from the list above.")

		def check(msg):
			return re.match("^\d$", msg.content) and msg.channel == ctx.channel and msg.author == ctx.author

		msg = await cfg.bot.wait_for('message', check=check, timeout=300)

		rolename = list[int(msg.content)-1]
		role = discord.utils.find(lambda m: m.name == rolename, cfg.server.roles)
		await member.remove_roles(role)
		await ctx.send("<:ok_hand_hmn_y2:534138088373485618> Removed role `" + rolename + "`.")

@pronouns.command(aliases=['usage', 'conjugate', 'declension'])
async def explain(ctx, *, rolename=None):
	if rolename is not None:
		set = cfg.pronoundict.get(rolename, None)
		if set == None:
			await ctx.send("<:thinking:534138088339931147> Doesn't look like there's a pronoun role with that name.")
		elif not "/" in set:
			await ctx.send("<:surprised:534138088398651403> This is a special role; it doesn't have a set associated with it.")
		else:
			setlist = set.split('/')
			await ctx.send("""The set `{5}` is used like this:
```
{0} went to the park.
I went with {1}.
{0} brought {2} frisbee.
At least I think it was {3}.
{0} threw the frisbee to {4}.
```
""".format(setlist[0].capitalize(), setlist[1], setlist[2], setlist[3], setlist[4], set))
