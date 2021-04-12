# Tests that cover the Redis integration
from mock_logger import MockLogger
from typing import Optional
import sys
import pytest


original_imports = set(sys.modules.keys())
k = 'foo'
v = 'bar'


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
        return self.should_fail

    def keys(self):
        if self.should_fail:
            raise Exception('Oops')
        else:
            return self.cache.keys

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


def valid_client(*args, **kwargs):
    return MockRedisClient()


def invalid_client(*args, **kwargs):
    return MockRedisClient(should_fail=True)


def test_store_post_successfully(mocker):
    import redis
    from redis_connector import store_post_from_server
    mocker.patch.object(redis, 'from_url', valid_client)

    logger = MockLogger()
    assert store_post_from_server(k, v, logger)
    assert len(logger.info_messages) == 1
    assert logger.info_messages[0] == 'Successfully persisted foo -> bar to Redis'
    assert len(logger.warn_messages) == 0


def test_store_post_fails(mocker):
    import redis
    from redis_connector import store_post_from_server
    mocker.patch.object(redis, 'from_url', invalid_client)

    logger = MockLogger()
    assert not store_post_from_server(k, v, logger)
    assert len(logger.warn_messages) == 1
    assert logger.warn_messages[0] == f'Failed to persist {k} -> {v} to Redis'
    assert len(logger.info_messages) == 0


def test_accurately_finds_post_already_used(mocker):
    import redis
    from redis_connector import post_already_used, store_post_from_server
    mocker.patch.object(redis, 'from_url', valid_client)

    logger = MockLogger()
    store_post_from_server(k, v)
    assert post_already_used(k, logger)
    assert len(logger.info_messages) == 1
    assert logger.info_messages[0] == f'Found {k} already in Redis'
    

def test_accurately_does_not_find_unused_post(mocker):
    import redis
    from redis_connector import post_already_used
    mocker.patch.object(redis, 'from_url', valid_client)

    logger = MockLogger()
    assert not post_already_used(k, logger)
    assert len(logger.info_messages) == 1
    assert logger.info_messages[0] == f'Key {k} not currently in Redis'


def test_flush_all_records_succeeds(mocker):
    pass


def test_flush_all_records_fails(mocker):
    pass


def test_enumerate_keys_succeeds(mocker):
    pass


def test_enumerate_keys_fails(mocker):
    pass


def test_get_value(mocker):
    pass
