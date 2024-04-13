import pytest

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE

pytestmark = pytest.mark.django_db


def test_news_per_page(client, multiple_news_samples, homepage_url):
    assert (
        client.get(homepage_url).context['object_list'].count()
        == NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_order(client, homepage_url):
    object_list = client.get(homepage_url).context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news_detail_url):
    all_comments = client.get(
        news_detail_url).context['news'].comment_set.all()
    sorted_comments = sorted(
        all_comments, key=lambda x: x.created
    )
    assert list(all_comments) == sorted_comments


def test_anonymous_client_has_no_form(client, news_detail_url):
    assert 'form' not in client.get(news_detail_url).context


def test_authorized_client_has_form(author_client, news_detail_url):
    context = author_client.get(news_detail_url).context
    assert 'form' in context
    assert isinstance(context['form'], CommentForm)
