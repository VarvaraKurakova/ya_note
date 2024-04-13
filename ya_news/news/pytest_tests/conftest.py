from datetime import datetime, timedelta

from django.test import Client
from django.urls import reverse
from django.utils import timezone
import pytest

from news.models import News, Comment
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


# URLS
@pytest.fixture
def homepage_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news_sample):
    return reverse('news:detail', args=(news_sample.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def register_url():
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def base_url(login_url):
    return f'{login_url}?next='


@pytest.fixture
def delete_comment_redirect_url(base_url, delete_comment_url):
    return f"{base_url}{delete_comment_url}"


@pytest.fixture
def edit_comment_redirect_url(base_url, edit_comment_url):
    return f"{base_url}{edit_comment_url}"


# Users and clients
@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


# Instances and their attributes
@pytest.fixture
def news_sample():
    return News.objects.create(
        title='Новость 1',
        text='Текст новости 1'
    )


@pytest.fixture
def comment(author, news_sample):
    return Comment.objects.create(
        author=author,
        text='Текст комментария тест',
        news=news_sample,
    )


@pytest.fixture
def multiple_news_samples():
    News.objects.bulk_create(News(
        title=f'Новость {i}',
        text=f'Текст новости {i}',
        date=datetime.today() - timedelta(days=i),
    )
        for i in range(
        0 + 1, NEWS_COUNT_ON_HOME_PAGE
        + 1 + 1)
    )


@pytest.fixture
def multiple_comments(author, news_sample):
    Comment.objects.create(
        Comment(
            author=author,
            text=f'Текст комментария {i+1}',
            created_at=timezone.now() + timedelta(days=i + 1),
            news=news_sample
        )for i in range(222)
    )
