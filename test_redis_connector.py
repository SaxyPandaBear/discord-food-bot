# Tests that cover the Redis integration
from mock_logger import MockLogger
from typing import Optional
import sys
import pytest


original_imports = set(sys.modules.keys())
k = 'foo'
v = 'bar'
logger = MockLogger()


# Mock Redis client to use for testing.
# The `should_fail` flag is used to force specific code branches for
# consistent testing and more code coverage.
class MockRedisClient:
    def __init__(self, should_fail: bool=False):
        self.cache = {}  # store a cache internally
        self.should_fail = should_fail

    def set(self, post_id: str, server: str) -> bool:
        if not self.should_fail:
            self.cache[post_id] = server
            return True
        else:
            return False

    def exists(self, post_id: str) -> int:
        if post_id in self.cache:
            return 1
        else:
            return 0

    def flushall(self, asynchronous: bool=False) -> bool:
        return not self.should_fail

    def keys(self):
        if self.should_fail:
            raise Exception('Oops')
        else:
            return self.cache.keys()

    def get(self, post_id: str) -> Optional[str]:
        if post_id in self.cache:
            return self.cache[post_id]
        else:
            return None


# The things that get mocked, such as `redis` are cached
# by Python import magic, and need to be removed in each
# test setup in order to reapply a different mock.
# https://github.com/pytest-dev/pytest-mock/issues/161
@pytest.fixture(autouse=True)
def cleanup(monkeypatch):
    monkeypatch.setenv('REDIS_URL', 'something')
    current_imports = set(sys.modules.keys())
    for key in current_imports - original_imports:
        del sys.modules[key]
    logger.flush()  # flush all of the messages before executing a new test


def valid_client(*args, **kwargs):
    return MockRedisClient()


def invalid_client(*args, **kwargs):
    return MockRedisClient(should_fail=True)


def test_store_post_successfully(mocker):
    import redis
    mocker.patch.object(redis, 'from_url', valid_client)
    from redis_connector import store_post_from_server

    assert store_post_from_server(k, v, logger)
    assert len(logger.info_messages) == 1
    assert logger.info_messages[0] == 'Successfully persisted foo -> bar to Redis'
    assert len(logger.warn_messages) == 0


def test_store_post_fails(mocker):
    import redis
    mocker.patch.object(redis, 'from_url', invalid_client)
    from redis_connector import store_post_from_server

    assert not store_post_from_server(k, v, logger)
    assert len(logger.warn_messages) == 1
    assert logger.warn_messages[0] == f'Failed to persist {k} -> {v} to Redis'
    assert len(logger.info_messages) == 0


def test_accurately_finds_post_already_used(mocker):
    import redis
    mocker.patch.object(redis, 'from_url', valid_client)
    from redis_connector import post_already_used, store_post_from_server

    store_post_from_server(k, v)
    assert post_already_used(k, logger)
    assert len(logger.info_messages) == 1
    assert logger.info_messages[0] == f'Found {k} already in Redis'
    

def test_accurately_does_not_find_unused_post(mocker):
    import redis
    mocker.patch.object(redis, 'from_url', valid_client)
    from redis_connector import post_already_used

    assert not post_already_used(k, logger)
    assert len(logger.info_messages) == 1
    assert logger.info_messages[0] == f'Key {k} not currently in Redis'


def test_flush_all_records_succeeds(mocker):
    import redis
    mocker.patch.object(redis, 'from_url', valid_client)
    from redis_connector import flush_all_records
    
    assert flush_all_records(logger)
    assert len(logger.info_messages) == 1
    assert logger.info_messages[0] == 'Successfully flushed all keys in Redis'


def test_flush_all_records_fails(mocker):
    import redis
    mocker.patch.object(redis, 'from_url', invalid_client)
    from redis_connector import flush_all_records

    assert not flush_all_records(logger)
    assert len(logger.info_messages) == 0
    assert len(logger.warn_messages) == 1
    assert logger.warn_messages[0] == 'Did not successfully flush all keys in Redis'


def test_enumerate_keys_succeeds(mocker):
    import redis
    mocker.patch.object(redis, 'from_url', valid_client)
    from redis_connector import enumerate_keys, store_post_from_server
    
    store_post_from_server(k, v)
    store_post_from_server(v, k)
    assert enumerate_keys(logger)
    assert len(logger.info_messages) == 1
    msg = logger.info_messages[0]
    assert k in msg
    assert v in msg
    # flaky?
    assert msg == f'{k}, {v}'


def test_enumerate_keys_prints_empty(mocker):
    import redis
    mocker.patch.object(redis, 'from_url', valid_client)
    from redis_connector import enumerate_keys
    
    assert enumerate_keys(logger)
    assert len(logger.info_messages) == 1
    assert logger.info_messages[0] == ''


def test_enumerate_keys_fails(mocker):
    import redis
    mocker.patch.object(redis, 'from_url', invalid_client)
    from redis_connector import enumerate_keys, store_post_from_server
    
    store_post_from_server(k, v)
    assert not enumerate_keys(logger)
    assert len(logger.info_messages) == 0
    assert len(logger.error_messages) == 1
    assert logger.error_messages[0] == repr(Exception('Oops'))


def test_get_value_that_exists(mocker):
    import redis
    mocker.patch.object(redis, 'from_url', valid_client)
    from redis_connector import get_value, store_post_from_server

    store_post_from_server(k, v)
    assert get_value(k) == v
    

def test_get_value_returns_none_for_invalid_key(mocker):
    import redis
    mocker.patch.object(redis, 'from_url', valid_client)
    from redis_connector import get_value

    assert get_value(k) == None
