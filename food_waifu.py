import discord
import praw
import asyncio
import auths


client: discord.Client = discord.Client()  # instantiate a new Discord Client
# TODO: get authentication details for reddit API
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
        # await client.send_message(message.channel, 'Received message')  # just for debug purposes
        em = discord.Embed(title='Food',
                           description='stuff about food',
                           color=0xFFFFFF)  # testing
        em.set_image(url='https://i.redd.it/6egiskh8k3101.jpg')
        await client.send_message(message.channel, embed=em)
        await client.send_message(message.channel, 'Yummy')
        # TODO: see how difficult it will be to search for a specific dish
        pass


# function that posts a picture to the server once every hour
async def post_new_picture():
    await client.wait_until_ready()  # doesn't execute until the client is ready
    channel: discord.Channel = discord.Object(id='some channel id')  # TODO: figure out channel ID
    while not client.is_closed:
        await client.send_message(channel, embed=get_embedded_post())
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


# client.loop.create_task(post_new_picture())  # looped task
client.run(auths.discord_token)
