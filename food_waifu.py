import discord
import praw
import asyncio
import auths


client: discord.Client = discord.Client()  # instantiate a new Discord Client
reddit = praw.Reddit(client_id=auths.reddit_client_id,
                     client_secret=auths.reddit_client_secret,
                     user_agent='discord:food_waifu:v0.1')  # instantiate a new Reddit Client


@client.event
async def on_ready():
    print('Username: %s\nID: %s' % (client.user.name, client.user.id))


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return  # we want to filter out messages from our bot
    if message.content.startswith('$food'):
        msg_contents = message.content.split(' ')[1:]  # ignore the '$food' token in the string
        if len(msg_contents) < 1:
            await client.send_message(message.channel, bot_description())
            await client.send_message(message.channel, help_message())
            return
        await client.send_message(message.channel, embed=get_hardcoded_embedded())
        # TODO: see how difficult it will be to search for a specific dish
        pass


# hard-coded embed object for testing purposes
def get_hardcoded_embedded():
    em = discord.Embed(title='Food',
                       description='stuff about food',
                       color=0xFFFFFF)  # testing
    em.set_image(url='https://i.redd.it/6egiskh8k3101.jpg')
    return em


# function that posts a picture to the server once every hour
async def post_new_picture():
    await client.wait_until_ready()  # doesn't execute until the client is ready
    while not client.is_closed:
        # em = get_embedded_post()  # get a single post, and post it to each server
        em = get_hardcoded_embedded()  # TODO: test with hardcoded value to get desired format
        for server in client.servers:  # each server that this bot is active in
            await client.send_message(server.default_channel(), embed=em)  # post to the default text channel
        await asyncio.sleep(3600)  # once an hour, or rather, once every 3,600 seconds


# returns a discord.Embed with all of the necessary information for an embedded message
def get_embedded_post():
    # TODO: determine what data is available when getting a reddit post
    title = 'Try to get Post title here'
    description = 'Try to get link to post here'
    color = 0xFFFFFF
    em = discord.Embed(title=title, description=description, color=color)
    em.set_image(url='URL of image post goes here')
    return em


# returns a formatted string that describes the bot's usage
def bot_description():
    return 'This bot posts a picture of food once every hour, to the default text channel.\n' \
           'Read more about this bot, or contribute to it at https://github.com/SaxyPandaBear/food_waifu'


# returns a formatted string that lists the available functions
def help_message():
    return 'Available functions: [ random ]\n' \
           'Type "$food help [function]" for more details on a specific function and it\'s usage.'


# returns a string that details the usage of the 'random' function of the bot
def help_bot_random():
    return '[random] => the bot posts an embedded message with a picture of food.\n' \
           'Example usage: "$food random"'


# client.loop.create_task(post_new_picture())  # looped task
client.run(auths.discord_token)
