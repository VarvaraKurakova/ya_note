from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING


pytestmark = pytest.mark.django_db

SLUG = 'slug'

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'title'
    NOTE_TEXT = 'Текст'
    NOTE_SLUG = SLUG

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'text': cls.NOTE_TEXT,
            'title': cls.NOTE_TITLE,
            'slug': cls.NOTE_SLUG}

    def test_anonymous_user_cant_create_note(self):
        notes_count_before = Note.objects.count()
        self.client.post(reverse('notes:add'), data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(
            reverse('notes:add'),
            data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before + 1, notes_count_after)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_user_empty_slug(self):
        Note.objects.all().delete()
        notes_before = Note.objects.count()
        self.assertEqual(notes_before, 0)
        self.form_data.pop('slug')
        response = self.auth_client.post(
            reverse('notes:add'),
            data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        notes_after = Note.objects.count()
        self.assertEqual(notes_before + 1, notes_after)
        note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user)


class TestNoteEditDelete(TestCase):

    NOTE_TITLE = 'title'
    NOTE_TEXT = 'Текст комментария'
    NOTE_SLUG = SLUG

    NEW_NOTE_TITLE = 'New title'
    NEW_NOTE_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            author=cls.author,
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
        )
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': cls.NEW_NOTE_TITLE,
            'slug': cls.NOTE_SLUG
        }
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(SLUG,))
        cls.delete_url = reverse('notes:delete', args=(SLUG,))

    def test_author_can_delete_note(self):
        notes_before = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_after = Note.objects.count()
        self.assertEqual(notes_before - 1, notes_after)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        #
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.note.author)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get()
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_not_unique_slug(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.note.slug + WARNING
        )
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
