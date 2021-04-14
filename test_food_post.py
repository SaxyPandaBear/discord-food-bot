# Tests for the FoodPost class
from food_post import FoodPost
from typing import Dict


class DummySubmission:
    def __init__(self, params: Dict):
        self.id = params['id']
        self.url = params['url']
        self.permalink = params['permalink']
        self.title = params['title']


def test_truncate_does_nothing_for_shorter_title():
    title = 'something short'
    assert FoodPost.truncate(title) == title


def test_truncate_returns_none_for_none_input():
    assert FoodPost.truncate(None) is None


def test_truncate_title_that_is_too_long():
    truncated_title = 'a' * 253  # the title will be truncated this much
    title = truncated_title + 'aaaaa'  # len(title) > 256
    expected = truncated_title + '...'
    actual = FoodPost.truncate(title)
    assert actual != title
    assert actual == expected


def test_transform_reddit_submission_to_food_post():
    submission_params = {
        'id': 'foo',
        'url': 'bar',
        'permalink': 'baz',
        'title': 'something'
    }
    fp = FoodPost.from_submission(DummySubmission(submission_params))
    assert fp is not None
    assert fp.id == submission_params['id']
    assert fp.image_url == submission_params['url']
    assert fp.title == submission_params['title']
    assert fp.post_url == f'https://www.reddit.com{submission_params["permalink"]}'


def test_discord_embed_omits_image_if_not_provided():
    fp = FoodPost(id='1', title='2', permalink='3')
    em = fp.to_embed()
    assert em.title == '2'
    assert em.description == '3'
    assert em._image == {'url': 'None'}


def test_discord_embed_truncates_title():
    truncated_title = 'a' * 253  # the title will be truncated this much
    title = truncated_title + 'aaaaa'  # len(title) > 256
    expected = truncated_title + '...'
    fp = FoodPost(id='1', title=title, permalink='2', image_url='3')
    em = fp.to_embed()
    assert fp.title == title
    assert em.title == expected
    assert em.description == '2'
    assert em._image == {'url': '3'}
