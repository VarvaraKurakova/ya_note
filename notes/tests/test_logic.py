from http import HTTPStatus

from pytils.translit import slugify
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='user01')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.url_success = reverse('notes:success')
        cls.url_add = reverse('notes:add')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url_add, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_auth_user_can_create_note(self):
        response = self.auth_client.post(self.url_add, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_cant_create_duplicate_slug(self):
        self.auth_client.post(self.url_add, data={
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
            'slug': 'note_slug'
        })
        self.auth_client.post(self.url_add, data={
            'title': 'Другая заметка',
            'text': 'другой текст заметки',
            'slug': 'note_slug'
        })
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_auto_slugify(self):
        self.auth_client.post(self.url_add, data=self.form_data)
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(note.title))


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Text'
    NOTE_TEXT_NEW = 'New text'
    NOTE_TITLE = 'Title'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='user01')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.another_author = User.objects.create(username='user02')
        cls.another_author_client = Client()
        cls.another_author_client.force_login(cls.another_author)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT_NEW
        }

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT_NEW)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)


    def test_user_cant_edit_note_of_another_author(self):
        response = self.another_author_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_user_cant_delete_note_of_another_author(self):
        response = self.another_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)