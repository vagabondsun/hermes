"""
help module

help shit

"""

import cfg #to enable referring to variables in cfg with the namespace prefix
from cfg import * #to enable calling things imported in cfg /without/ the namespace prefix

async def on_command_error(ctx, error):

    if hasattr(ctx.command, 'on_error'):
        return
