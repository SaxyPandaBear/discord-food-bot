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


# function that posts a picture to the server once every hour
async def post_new_picture():
    await client.wait_until_ready()  # doesn't execute until the client is ready
    channel: discord.Channel = discord.Object(id='some channel id')  # TODO: figure out channel ID
    while not client.is_closed:
        em: discord.Embed = discord.Embed(title='Title',
                                          description='Description',
                                          color=0xFFFFFF,
                                          url=get_new_picture_url())
        client.send_message(channel, embed=em)
        await asyncio.sleep(3600)  # once an hour


# function that retrieves a URL for an image on reddit and returns the URL as a string
def get_new_picture_url():
    return ''


client.loop.create_task(post_new_picture())  # looped task
client.start(auths.discord_token)
