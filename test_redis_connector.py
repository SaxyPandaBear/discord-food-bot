# Tests that cover the Redis integration
from typing import Optional
from mock_logger import MockLogger
import redis
import pytest
from redis_connector import store_post_from_server, \
    flush_all_records, \
    get_value, \
    post_already_used, \
    enumerate_keys


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


def invalid_client(*args, **kwargs):
    return MockRedisClient(should_fail=True)


def valid_client(*args, **kwargs):
    return MockRedisClient()


@pytest.fixture
def mock_invalid_client(monkeypatch):
    monkeypatch.setenv('REDIS_URL', 'something')
    monkeypatch.setattr(redis, "from_url", invalid_client)


def test_store_post_successfully(monkeypatch):
    monkeypatch.setenv('REDIS_URL', 'something')
    monkeypatch.setattr(redis, "from_url", valid_client)

    res = store_post_from_server('foo', 'bar')
    assert res


def test_store_post_successfully_with_logging(monkeypatch):
    monkeypatch.setenv('REDIS_URL', 'something')
    monkeypatch.setattr(redis, "from_url", valid_client)
    
    logger = MockLogger()
    res = store_post_from_server('foo', 'bar', logger)
    assert res
    assert len(logger.info_messages) > 0
    assert len(logger.warn_messages) == 0

