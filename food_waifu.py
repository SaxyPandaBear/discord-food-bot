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
    if not message.content.startswith('$food'):
        return  # don't process messages without the "$food" tag
    msg_contents = message.content.split(' ')
    if len(msg_contents) < 2:
        msg = bot_description() + '\n' + help_message()  # send 1 concatenation rather than 2 messages
        await client.send_message(message.channel, msg)
        return
    msg_contents = msg_contents[1:]  # ignore the "$food" part of the message

    # "$food help [function]"
    # if an optional [function] argument is given, the bot prints a description
    # of that function's usage,
    # otherwise, it just prints out the generic help text that is printed out
    # when an unrecognized command is given, or no commands are given.
    if msg_contents[0] == 'help':
        # help no longer is a single command usage.
        # it can be used to get more detailed info on other available functions
        if len(msg_contents) == 1:  # no args were passed in
            await client.send_message(message.channel, help_message())
        else:
            if msg_contents[1] == 'random':
                await client.send_message(message.channel, help_bot_random())
            else:
                await client.send_message(message.channel, help_message())
    elif msg_contents[0] == 'random':
        await client.send_message(message.channel, embed=get_hardcoded_embedded())
    else:
        msg = "Unrecognized operation: '%s'\n" % msg_contents[0]
        msg += help_message()
        await client.send_message(message.channel, msg)
    # TODO: see how difficult it will be to search for a specific dish
    pass


# hard-coded embed object for testing purposes
def get_hardcoded_embedded():
    em = discord.Embed(title='Food',
                       description='stuff about food',
                       color=0xDB5172)
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
    color = 0xDB5172
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
