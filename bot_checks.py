# File that contains predicates that are used by the Discord bot
# as checks for it's commands
import discord
import asyncio # not sure if this import is needed

# predicate used as a Check for the bot to verify from context if it should process the request
async def pred_is_admin(ctx):
    return is_user_admin(ctx.channel, ctx.author)

def is_user_admin(channel, user):
    perms = user.permissions_in(channel)
    return perms.administrator

async def pred_is_text_channel(ctx):
    return isinstance(ctx.channel, discord.TextChannel)
