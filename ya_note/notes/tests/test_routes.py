from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

SLUG = 'slug'

HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
NOTES_LIST_URL = reverse('notes:list')
ADD_NOTE_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
DETAIL_NOTE_URL = reverse('notes:detail', args=(SLUG,))
EDIT_NOTE_URL = reverse('notes:edit', args=(SLUG,))
DELETE_NOTE_URL = reverse('notes:delete', args=(SLUG,))


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.client_reader = Client()
        cls.client_reader.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=SLUG,
            author=cls.author,
        )
        cls.urls = (
            HOME_URL,
            LOGIN_URL,
            SIGNUP_URL,
            NOTES_LIST_URL,
            ADD_NOTE_URL,
            SUCCESS_URL,
            DETAIL_NOTE_URL,
            EDIT_NOTE_URL,
            DELETE_NOTE_URL,
            LOGOUT_URL,
        )

    def test_author_access_pages(self):
        """Автор заметки имеет доступ ко всем страницам."""
        for name in self.urls:
            with self.subTest(name=name):
                response = self.client_author.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_non_author_access_pages(self):
        author_urls = (EDIT_NOTE_URL, DELETE_NOTE_URL, DETAIL_NOTE_URL)
        for name in self.urls:
            with self.subTest(name=name):
                response = self.client_reader.get(name)
                if name not in author_urls:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.OK)

    def test_anonymous_access_pages(self):
        anonymous_urls = (LOGIN_URL, SIGNUP_URL, HOME_URL, LOGOUT_URL)
        for name in self.urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                if name not in anonymous_urls:
                    redirect_url = f'{LOGIN_URL}?next={name}'
                    self.assertRedirects(response, redirect_url)
