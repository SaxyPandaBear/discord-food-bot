import discord
import praw
import asyncio
import auths
import random
from food_post import FoodPost


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
        await client.send_message(message.channel, msg)  # opt to send 1 message instead of 2.
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
            channel = get_default_text_channel(server)
            await client.send_message(channel, embed=em)  # post to the default text channel
        # we successfully (hopefully) posted an image to each server this bot is in,
        # but we don't want to post duplicates later.
        # write all of the ids used to a file
        await asyncio.sleep(3600)  # once an hour, or rather, once every 3,600 seconds


# returns a discord.Embed with all of the necessary information for an embedded message
def get_embedded_post():
    subs = []
    ids = []
    submission = get_submission_from_subs(subs, ids)  # TODO: read subs and ids from file
    post = transpose_submission_to_food_post(submission)
    # need to write the id of this post into our file so we don't post it again later
    ids.append(post.id)
    em = transpose_food_post_to_embed(post)
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


# takes a server object and searches for the first text channel it finds.
# Discord has decided to not designate a specific "default" text channel anymore,
# and the default is now the first text channel.
def get_default_text_channel(server: discord.Server):
    for channel in server.channels:
        if channel.type == discord.ChannelType.text:  # the first text channel is our default channel
            return channel
    return None  # somehow there isn't a text channel (not sure if it's even possible to get to this state


# a FoodPost makes it more readable to interface with different attributes needed for a discord.Embed object
# take a submission and return it's resulting FoodPost
def transpose_submission_to_food_post(submission):
    sub_id = submission.id
    url = get_image_url(submission)
    permalink = submission.permalink
    title = submission.title
    return FoodPost(id=sub_id, title=title, image_url=url, permalink=permalink)


# because a submission's URL can either be the link to a hosted image, or to the comments section of it's own
# submission, let's try to get the actual image every time.
def get_image_url(submission):
    return ''


# takes a FoodPost and maps its attributes to attributes of a discord.Embed object
# that will be posted by the bot
def transpose_food_post_to_embed(post: FoodPost):
    title = post.title
    desc = post.post_url
    color = 0xDB5172
    em = discord.Embed(title=title, description=desc, color=color)
    if post.image_url != '':  # safeguard for non-functional urls
        em.set_image(url=post.image_url)
    return em


# returns a random submission from the given list of subreddits
# uses the top 15 hot submissions
# has a list of ids for posts that were already posted.
def get_submission_from_subs(subs, already_posted):
    submissions = []
    subs_list = ''
    for i in range(len(subs)):
        subs_list += subs[i]
        if i != len(subs) - 1:
            subs_list += "+"
    # should have a string like "a+b+c"
    limit = 20  # this is the maximum number of submissions to poll
    for submission in reddit.subreddit(subs_list).hot(limit=limit):
        if submission.id not in already_posted:
            submissions.append(submission)
    # need a check in case all of the submissions were already posted
    while len(submissions) < 1:
        for submission in reddit.subreddit(subs_list).hot(limit=limit):
            if submission.id not in already_posted:
                submissions.append(submission)
        limit += 20  # at some point either we will get rate limited, or we'll find a new post
    return random_submission(submissions)


def random_submission(submissions):
    index = random.randint(0, len(submissions) - 1)
    return submissions[index]


# Starts the discord client
client.loop.create_task(post_new_picture())  # looped task
client.run(auths.discord_token)
