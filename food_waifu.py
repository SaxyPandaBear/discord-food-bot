from typing import List, Optional, Tuple
import discord
from discord.ext import commands
import praw
import asyncio
import auths
import random
from time import gmtime
from food_post import FoodPost
import logging
import subprocess
import os
from predicates import is_admin
from help_commands import *
import redis_connector
from utility import *


logger = logging.getLogger()
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
# file_handler = logging.FileHandler(f'{os.getcwd()}/log.txt')  # TODO: figure out how to do this dynamically
# file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
logger.addHandler(stream_handler)


MAX_ALLOWED_SEARCH_SIZE = 500  # Not sure if the API actually lets me do this
# read a list of subreddits from the environment, and use that
# for the search criteria
subs_list = read_subreddits_from_env()


# Instantiate the bot
bot_presence = discord.Activity(
    name=f"Serving good food from {' and '.join(subs_list)}",
    type=discord.ActivityType.playing)
bot = commands.Bot(command_prefix="!food ", description=bot_description(), activity=bot_presence)


# use this to determine when to post hourly
stored_hour = None


# function that posts a picture to the server on a timer
async def post_new_picture():
    global stored_hour
    await bot.wait_until_ready()  # doesn't execute until the client is ready
    while not bot.is_closed():
        current_time = gmtime().tm_hour
        if stored_hour is None or is_scheduled_time(current_time, stored_hour):
            # set stored_hour for next scheduled post
            stored_hour = current_time

            post_id, em = get_random_embedded_post()  # get a single post, and post it to each server
            for guild in bot.guilds:  # each server that this bot is active in
                channel = get_text_channel(guild)
                # because we can't filter for posts that are already there in each server before
                # generating the post, make the check here
                if redis_connector.post_already_used(post_id, logger):
                    # if the post is already there, generate a new one specific to this guild and return
                    p_id, diff_em = get_random_embedded_post(guild.id) # already written to file
                    await channel.send(embed=diff_em)
                    redis_connector.store_post_from_server(p_id, guild.id, logger)
                    continue
                await channel.send(embed=em)  # post to the default text channel
            # after the post has been posted to all connected servers,
            # persist the post
            redis_connector.store_post_from_server(post_id, 'all', logger) # right now, we don't use the value stored in Redis
        await asyncio.sleep(30)  # wait 30 seconds before checking again


# return True if is next hour, false otherwise
def is_scheduled_time(current_time: int, stored_hour: Optional[int] = None) -> bool:
    # if the hour that we store is 23, that means the next hour should be 0
    if stored_hour == 23:
        return current_time < 23
    else:
        # otherwise compare normally
        return current_time > stored_hour


# returns a discord.Embed with all of the necessary information for an embedded message
# this function accepts a guild parameter so that the ID can be written for the specific guild
# If a server ID is passed in, then the post is persisted in Redis,
# associated with the given server ID so that it doesn't get reposted
# elsewhere later
def get_random_embedded_post(server = None) -> Tuple[str, discord.Embed]:
    submission = get_submission_from_subs(subs_list)
    post = FoodPost.from_submission(submission)
    # need to write the id of this post into our file so we don't post it again later
    if server is not None:
        # write_id_to_file(post.id, server)
        redis_connector.store_post_from_server(post.id, server, logger)
    return post.id, post.to_embed()


# takes a search query and returns the first result within the given
# subreddits. no duplicates are allowed
def search_posts(query: str, server: str) -> Optional[discord.Embed]:
    # This searches, and returns a new post that isn't already persisted
    # to Redis
    submission = search_submission_from_subs(subs_list, query)
    
    # if submission is None, then the search returned no results
    if submission is None:
        return None
    
    # write_id_to_file(submission.id, server)
    redis_connector.store_post_from_server(submission.id, server, logger)
    post = FoodPost.from_submission(submission)
    return post.to_embed()


# find the first, most relevant result from the search. do not include duplicates
def search_submission_from_subs(subs: List[str], query: str):
    subs_list = '+'.join(subs)
    for submission in reddit.subreddit(subs_list).search(query=query, sort='relevance', syntax='lucene'):
        if not redis_connector.post_already_used(submission.id, logger):
            return submission
    # if we didn't return in the iteration, just return the first relevant one this month
    try:
        # call to next() can raise StopIteration error if the list generator has no values left, meaning there were no results for this search
        result = next(reddit.subreddit(subs_list).search(query=query, sort='relevance', syntax='lucene', time_filter='month'))
        return result
    except StopIteration:
        logger.error(f'No results found for {query} in subs: {subs}')
        return None


# because a submission's URL can either be the link to a hosted image, 
# or to the comments section of it's own submission, let's try to get
# the actual image every time.
def get_image_url(submission) -> str:
    return submission.url  # TODO: figure out what kinds of data can appear


# returns a random submission from the given list of subreddits
# uses the top 20 hot submissions
# has a list of ids for posts that were already posted.
def get_submission_from_subs(subs):
    submissions = []
    joined_subs = '+'.join(subs)  # should have a string like "a+b+c"
    limit = 20  # this is the maximum number of submissions to poll
    for submission in reddit.subreddit(joined_subs).hot(limit=limit):
        if not redis_connector.post_already_used(submission.id, logger):
            submissions.append(submission)
    # need a check in case all of the submissions were already posted
    hit_max_search = False
    while len(submissions) < 1:
        if limit == MAX_ALLOWED_SEARCH_SIZE and not hit_max_search:
            hit_max_search = True
        if limit == MAX_ALLOWED_SEARCH_SIZE and hit_max_search:
            raise Exception("Reached search limit, but couldn't find a new post")
        for submission in reddit.subreddit(joined_subs).hot(limit=limit):
            if not redis_connector.post_already_used(submission.id, logger):
                submissions.append(submission)
        # at some point either we will get rate limited, or we'll find a new post
        # by including a max search size, a big TODO would be to actually paginate
        # the search... but oh well
        limit = min(limit * 2, MAX_ALLOWED_SEARCH_SIZE)
    return random.choice(submissions)


# restarts the bot using pm2's restart functionality.
# if the bot restarts successfully, then the bot will have been
# abruptly stopped, not gracefully.
def restart_bot():
    # first, need to get this process's ID from pm2.
    # then, invoke restart on it.
    id_output = subprocess.run(["pm2", "id", "Food Bot"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.info(id_output)
    # the output of the above command would be in the form of "[ id ]" with the intended whitespace illustrated
    # need to strip the characters around the ID
    pm2_id = id_output.stdout.decode('utf-8').replace("[", "").replace("]", "").strip()
    if len(pm2_id) == 0: 
        logger.error('Could not find pm2 ID for this bot')
        return False
    logger.info(pm2_id)

    # attempt to restart the bot
    subprocess.run(["pm2", "restart", str(pm2_id)])
    return False


@bot.event
async def on_ready():
    logger.info(f"Username: {bot.user.name}")
    logger.info(f"ID: {bot.user.id}")

@bot.command(description="Post a new food picture into the channel", help=help_bot_random(), brief="Post food picture")
async def new(context):
    post_id, em = get_random_embedded_post(context.guild.id)
    await context.send(embed=em)

@bot.command(description="Searches for a new food picture to post into the channel", help=help_bot_search(), usage="something I want to search separated by spaces", brief="Search for new food picture")
async def search(context, *search_terms: str):
    if len(search_terms) < 1:
        await context.send("Specify at least one term to search for")
        return
    query = build_query(search_terms)
    em = search_posts(query, context.guild.id)
    if em is None:
        await context.send(f"No titles containing {search_terms} found in defined subreddits")
        return
    else:
        await context.send(embed=em)
        return

@bot.command(description="Clears all of the Reddit post IDs that are persisted for deduplication", help=help_bot_clear(), brief="Flushes Redis keys")
@commands.guild_only()
@is_admin() # restrict this command to Guild channels
async def clear(context):
    redis_connector.flush_all_records(logger)
    await context.send("Successfully cleared contents")

@bot.command(description="Restarts the bot on request", help=help_bot_restart(), brief="Restarts bot")
@commands.guild_only()
@is_admin() # restrict this command to Guild channels
async def restart(context):
    if not restart_bot():
        await context.send("Error when attempting to restart bot. Please restart manually.")

@bot.command(description="Print all stored Redis keys to log", help=help_bot_list_keys(), brief="Logs Redis keys")
@is_admin()
async def keys(context):
    if redis_connector.enumerate_keys(logger):
        await context.send("Successfully printed Redis keys to log")
    else:
        await context.send("Error occurred when printing Redis keys to log")

@bot.command(description="Get and print the server where a Reddit submission was posted", help=help_bot_fetch_value_from_redis(), brief="Print Redis key-value pair", usage="some_reddit_post_id")
@is_admin()
async def fetch(context, *ids: str):
    if len(ids) != 1:
        await context.send("Only allowed to fetch one value from Redis at a time.")
        return
    reddit_id = ids[0]
    val = redis_connector.get_value(reddit_id)
    if val is not None:
        await context.send(f"{reddit_id} -> {val}")
    else:
        await context.send(f"Couldn't find key {reddit_id} in Redis.")

# Starts the discord client
logger.info("Creating looped task")
bot.loop.create_task(post_new_picture())  # looped task
logger.info("Finished creating looped task")
try:
    reddit = praw.Reddit(client_id=auths.reddit_client_id,
                     client_secret=auths.reddit_client_secret,
                     user_agent='discord:food_waifu:v0.2')  # instantiate a new Reddit Client
    bot.run(auths.discord_token)
except Exception as e:
    logger.error(repr(e))
