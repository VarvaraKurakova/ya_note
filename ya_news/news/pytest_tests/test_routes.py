from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

HOMEPAGE = pytest.lazy_fixture('homepage_url')
REGISTER = pytest.lazy_fixture('register_url')
LOGIN = pytest.lazy_fixture('login_url')
LOGOUT = pytest.lazy_fixture('logout_url')
NEWS_DETAIL = pytest.lazy_fixture('news_detail_url')
EDIT_COMMENT = pytest.lazy_fixture('edit_comment_url')
DELETE_COMMENT = pytest.lazy_fixture('delete_comment_url')
CLIENT = pytest.lazy_fixture('client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
READER_CLIENT = pytest.lazy_fixture('reader_client')
DELETE_COMMENT_REDIRECT_URL = pytest.lazy_fixture(
    'delete_comment_redirect_url'
)
EDIT_COMMENT_REDIRECT_URL = pytest.lazy_fixture('edit_comment_redirect_url')

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, expected_url',
    (
        (DELETE_COMMENT, DELETE_COMMENT_REDIRECT_URL),
        (EDIT_COMMENT, EDIT_COMMENT_REDIRECT_URL)
    ))
def test_edit_delete_comment_anonymous(client, url, expected_url):
    assertRedirects(client.get(url), expected_url)


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (HOMEPAGE, CLIENT, HTTPStatus.OK),
        (REGISTER, CLIENT, HTTPStatus.OK),
        (LOGIN, CLIENT, HTTPStatus.OK),
        (LOGOUT, CLIENT, HTTPStatus.OK),
        (NEWS_DETAIL, CLIENT, HTTPStatus.OK),
        (DELETE_COMMENT, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_COMMENT, READER_CLIENT, HTTPStatus.NOT_FOUND),
        (EDIT_COMMENT, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_COMMENT, READER_CLIENT, HTTPStatus.NOT_FOUND)
    )
)
def test_all(url, parametrized_client, expected_status):
    assert parametrized_client.get(url).status_code == expected_status
