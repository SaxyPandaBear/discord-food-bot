Food Waifu
===========

Discord bot that posts a picture of food once an hour to all of the 
connected Discord servers. This feature is done in the background,
and the bot can handle search and random requests to post other content
as well.

The bot makes API calls to Reddit, using the application configurations
in order to find a random submission to post. These posts are unique, and
deduplicated in a Redis caching layer that the bot interfaces with.

The bot is deployed via Heroku, and depends on the Heroku Redis add-on.

## Features
`!food help` prints a description of the bot, as well as lists out options for usage.

- `!food help [function]` prints a description of the given function, as well as example usage.

`!food new` picks a random picture of food and posts it to the channel.

`!food search [query]` takes in a search query and returns the first, most relevant result *that is not a duplicate*.
 
 `!food clear` flushes the Redis cache, allowing all previously posted content that is persisted to Redis to be posted again.

## Setup

- Python 3.6.3
- [discord.py](https://github.com/Rapptz/discord.py) 1.6.0
- [PRAW](https://praw.readthedocs.io/en/latest/index.html) 6.2.0
- [redis](https://github.com/andymccurdy/redis-py) 3.5.3

A simple way to get the required libraries is through Pip: `pip install -r requirements.txt`

To set up the bot, it requires a file, `auths.py` (a template is provided). This file contains all of the 
authentication for both Discord and Reddit, and is necessary to interface with their APIs.

On top of this, a file called `subreddits.txt` must be in the same directory as the bot (template provided). This 
file will contain a list of subreddit names that will be used by the bot to find submissions to post. This list 
requires the items to be all lowercase, even if the subreddit itself uses capitalization.

These files can be auto generated using the `bootstrap.sh` script 
(this is used to bootstrap the application when deploying to Heroku).

For example: for a subreddit /r/FooBar, the entry in the text file would simply be `foobar`

## Deduplication of Reddit posts
On Heroku, we use the provided Redis cache to persist Reddit posts by their
unique ID, and the Discord server ID where the post was sent to.

See `redis_connector.store_post_from_server` and its usages.

> It's important to note that despite the fact that this is branded as a food
posting bot, the actuality is that it's generic enough that it can work with
any subreddit that primarily has picture posts (i.e.: art subreddits).