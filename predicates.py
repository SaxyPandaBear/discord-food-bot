# File that contains predicates that are used by the Discord bot
# as checks for it's commands
from discord.ext import commands


def is_admin():
    async def predicate(ctx):
        return ctx.author.permissions_in(ctx.channel).administrator
    return commands.check(predicate)
