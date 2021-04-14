# Tests for the utility functions
from utility import read_subreddits_from_env, build_query
import pytest


def test_build_query():
    terms = ['a', 'b', 'c']
    query = build_query(terms)
    assert ' '.join(terms) in query
    assert 'self:no' in query


def test_build_query_raises_exception_on_none():
    with pytest.raises(ValueError):
        build_query(None)


def test_build_query_raises_exception_on_empty():
    with pytest.raises(ValueError):
        build_query([])


def test_read_from_env_fails_when_missing():
    with pytest.raises(LookupError):
        read_subreddits_from_env()


def test_read_from_env_fails_on_empty_value(monkeypatch):
    monkeypatch.setenv('SUBREDDITS', '')
    with pytest.raises(ValueError):
        read_subreddits_from_env()


def test_read_from_env_works(monkeypatch):
    sub_str = 'foo,bar,baz'
    monkeypatch.setenv('SUBREDDITS', sub_str)
    subs = read_subreddits_from_env()
    assert subs == sub_str.split(',')
