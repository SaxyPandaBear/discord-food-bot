discord-food-bot
================

![ci](https://github.com/SaxyPandaBear/discord-food-bot/actions/workflows/main.yml/badge.svg) [![codecov](https://codecov.io/gh/SaxyPandaBear/discord-food-bot/branch/master/graph/badge.svg?token=GSDBRQNE4P)](https://codecov.io/gh/SaxyPandaBear/discord-food-bot)

Discord bot that posts a picture of food once an hour to all of the 
connected Discord servers. This feature is done in the background,
and the bot can handle search and random requests to post other content
as well.

The bot makes API calls to Reddit, using the application configurations
in order to find a random submission to post. These posts are unique, and
deduplicated in a Redis caching layer that the bot interfaces with.

The bot is deployed via Heroku, and depends on the Heroku Redis add-on.

> It's important to note that despite the fact that this is branded as a food
posting bot, the actuality is that it's generic enough that it can work with
any subreddit that primarily has picture posts (i.e.: art subreddits).

## Features
`!food help` prints a description of the bot, as well as lists out options for usage.

- `!food help [function]` prints a description of the given function, as well as example usage.

`!food new` picks a random picture of food and posts it to the channel.

`!food search [query]` takes in a search query and returns the first, most relevant result *that is not a duplicate*.
 
 `!food clear` flushes the Redis cache, allowing all previously posted content that is persisted to Redis to be posted again.

## Post Deduplication
Currently this is deployed on Heroku, and utilizes Heroku Redis in order to 
store the Reddit IDs that are posted. This is used as a LRU cache, such that 
the oldest ID gets evicted when the cache is at capacity. This helps for 
deduplication, because the newer post will evict a post that has been posted 
a while ago (hopefully). The data is stored in Redis in this pattern:
```
abc123 -> discord_server1
bcd234 -> all
cde345 -> discord_server2
```
In this way, we can store somewhat useful information on which Discord server
each Reddit post is sent to. The `all` value denotes that the given Reddit ID is
sent to all of the Discord servers via the scheduled event loop task.

See `redis_connector.store_post_from_server` and its usages.

## Setup

- Python <= 3.7 (The pipfile installation breaks for 3.8+)
- [discord.py](https://github.com/Rapptz/discord.py) 1.6.0
- [PRAW](https://praw.readthedocs.io/en/latest/index.html) 6.2.0
- [redis](https://github.com/andymccurdy/redis-py) 3.5.3
- NodeJS 6+
- [pm2](https://pm2.keymetrics.io/) for automatic restarts on app failure on the deployed instance

A simple way to get the required libraries is through Pip: `pip install -r requirements.txt`

pm2 is not required to run the application, but is required for deployment.
> Technically, it's required for the `!food restart` command, but that's 
already hacky enough as it is, and not that important of a feature to require
pm2.

To set up the bot, it requires a file, `auths.py` (a template is provided). 
This file contains all of the authentication for both Discord and Reddit, 
and is necessary to interface with their APIs.

On top of this, a file called `subreddits.txt` must be in the same directory as
the bot (template provided). This file will contain a list of subreddit names 
that will be used by the bot to find submissions to post. This list requires
the items to be all lowercase, even if the subreddit itself uses capitalization.

These files can be auto generated using the `bootstrap.sh` script 
(this is used to bootstrap the application when deploying to Heroku).

For example: for a subreddit /r/FooBar, the entry in the text file would simply be `foobar`

## Developing
When adding new features, make sure that you cover tests and linting locally
to save yourself the trouble of it failing in the CICD pipeline.

### Testing
```
pytest
```

### Linting
```
# Syntax errors
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Lint warnings
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --exclude auths.py
```
