from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestHomePage(TestCase):
    HOME_URL = reverse('notes:home')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='user01')
        cls.another_author = User.objects.create(username='user02')
        cls.author_note = Note.objects.create(
            title='Заголовок01',
            text='Текст01',
            slug='slug',
            author=cls.author)
        cls.url_list = reverse('notes:list')

    def test_note_in_object_list(self):
        self.client.force_login(self.author)
        response = self.client.get(self.url_list)
        self.assertIn('object_list', response.context)
        self.assertIsInstance(response.context['object_list'][0], Note)

    def test_note_access_only_for_author(self):
        note_status = (
            (self.author, True),
            (self.another_author, False)
        )
        for user, expected_note_in_list in note_status:
            self.client.force_login(user)
            response = self.client.get(self.url_list)
            note_in_list = self.author_note in response.context['object_list']
            self.assertEqual(note_in_list, expected_note_in_list)

    def test_edit_and_delete_pages_have_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.author_note.slug,))
        )
        self.client.force_login(self.author)
        for name, args in urls:
            url = reverse(name, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)