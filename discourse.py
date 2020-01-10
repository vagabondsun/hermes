"""

discourse module

provides integration with the forum

"""

import cfg #to enable referring to variables in cfg with the namespace prefix
from cfg import * #to enable calling things imported in cfg /without/ the namespace prefix

@cfg.bot.command()
@cfg.is_PM()
async def forum(ctx):
    await ctx.send("<:envelope_with_arrow:534138087958249489> Please enter the email you want to sign up to the forum with: _(or `!cancel`)_")

    def check(msg):
        return re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$|!cancel", msg.content)

    msg = await bot.wait_for('message', check=check)

    if msg.content.startswith("!cancel"):
        await ctx.send("Cancelled generating invite.")
        return

    response = cfg.forum_client.invite_link(email=msg.content, group_names='', custom_message='')

    await ctx.send("<:ok_hand_hmn_y2:534138088373485618> Here's your invite link: " + str(response))
