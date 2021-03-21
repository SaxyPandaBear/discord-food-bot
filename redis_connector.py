# Handles connecting to Heroku Redis, and persisting a
# server ID and post ID record to Redis, as a key to look up.
# It also is used to handle looking up a record from Redis.
# This probably could have been put in the main script, but
# I think it's already too messy.
import os
from typing import Optional
import redis
import logging

r = redis.from_url(os.environ['REDIS_URL'], decode_responses=True)


# store the post_id, and the server it's associated with
def store_post_from_server(post_id: str, server: str, logger: Optional[logging.Logger] = None) -> bool:
    res = r.set(post_id, server)
    if logger is not None:
        if res:
            logger.info(f'Successfully persisted {post_id} -> {server} to Redis')
        else:
            logger.warn(f'Failed to persist {post_id} -> {server} to Redis')
    return res


# check if a key is already persisted in Redis
def post_already_used(post_id: str, logger: Optional[logging.Logger] = None) -> bool:
    res = r.exists(post_id) > 0
    if logger is not None:
        if res:
            logger.info(f'Found {post_id} already in Redis')
        else:
            logger.info(f'Key {post_id} not currently in Redis')
    return res


# delete all of the keys stored in Redis
def flush_all_records(logger: Optional[logging.Logger] = None):
    res = r.flushall(asynchronous=False)
    if logger is not None:
        if res:
            logger.info('Successfully flushed all keys in Redis')
        else:
            logger.warn('Did not successfully flush all keys in Redis')


# for debugging purposes only, print all of the existing
# keys stored in Redis
def enumerate_keys(logger: logging.Logger) -> bool:
    try:
        res = r.keys()
        logger.info(', '.join(res))
        return True
    except Exception as e:
        logger.error(repr(e))
        return False


# for debugging purposes only, get the server associated
# with a Reddit submission ID
def get_value(post_id: str) -> Optional[str]:
    return r.get(post_id)