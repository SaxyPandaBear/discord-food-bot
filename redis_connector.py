# Handles connecting to Heroku Redis, and persisting a
# server ID and post ID record to Redis, as a key to look up.
# It also is used to handle looking up a record from Redis.
# This probably could have been put in the main script, but
# I think it's already too messy.
import os
import redis

r = redis.from_url(os.environ['REDIS_URL'])


# store the post_id, and the server it's associated with
def store_post_from_server(post_id: str, server: str) -> bool:
    return r.set(post_id, server)


def post_already_used(post_id: str) -> bool:
    return r.exists(post_id) > 0


def flush_all_records():
    r.flushall(asynchronous=True)
