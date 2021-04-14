# Collection of utility functions that are used by the main script.
from typing import List, Optional
import os
from discord import TextChannel


# Read the "SUBREDDITS" key from the environment, and parse the string that
# is expected to be a comma delimited list of valid subreddits, and return
# that list.
# If the "SUBREDDITS" key is not in the environment, raises an Exception
# If the value is empty, raises an Exception
def read_subreddits_from_env() -> List[str]:
    if "SUBREDDITS" not in os.environ:
        raise LookupError('SUBREDDITS is not defined as an environment variable')
    else:
        subs_str = os.environ["SUBREDDITS"]
        if len(subs_str) < 1:
            raise ValueError('SUBREDDITS value cannot be an empty string')
        return subs_str.split(',')


# takes a Guild object and returns the first channel that the bot has access to post to.
# this is determined by using the Channel class's `permissions_for(..)` function
# This function returns None for the given guild if it could not find a TextChannel
# that it has send_message permissions for.
# Note that the iteration over the channels in the guild are up to the
# underlying implementation, and not necessarily guaranteed to maintain
# a consistent ordering. As such, this function cannot be expected to be
# deterministic.
def get_text_channel(guild) -> Optional[TextChannel]:
    member = guild.me
    for channel in guild.channels:
        if isinstance(channel, TextChannel) and channel.permissions_for(member).send_messages:
            return channel
    return None


# takes a query for searching and applies the necessary restrictions
# we want to limit our searches to just the title of the post, and also
# exclude all self posts (text posts)
def build_query(search_terms: List[str]) -> str:
    if search_terms is None:
        raise ValueError('Cannot search on no terms')
    if len(search_terms) < 1:
        raise ValueError('Cannot search on no terms')
    joined = ' '.join(search_terms)
    return f'title:"{joined}" self:no'
