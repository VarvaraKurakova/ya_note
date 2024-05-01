from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


SLUG = 'slug'


class TestNotePage(TestCase):
    NOTES_LIST_URL = reverse('notes:list')
    NOTES_ADD_URL = reverse('notes:add')
    NOTES_EDIT_URL = reverse('notes:edit', args=(SLUG,))
    HOME_URL = reverse('notes:home')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)
        cls.another_author = User.objects.create(username='Другой автор')
        cls.client_another_author = Client()
        cls.client_another_author.force_login(cls.another_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=SLUG,
            author=cls.author
        )

    def test_notes_list_for_author_user(self):
        """Отдельная заметка передаётся на страницу."""
        response = self.client_author.get(self.NOTES_LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_notes_list_for_non_author_user(self):
        response = self.client_another_author.get(self.NOTES_LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 0)

    def test_anonymous_client_has_no_form(self):
        """На страницы создания и редактирования заметки
        для анонимного пользователя не передаются формы.
        """
        for name in (self.NOTES_ADD_URL, self.NOTES_EDIT_URL):
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertIsNone(response.context)

    def test_authorized_client_has_form(self):
        """На страницы создания и редактирования заметки
        для авторизованного пользователя передаются формы.
        """
        for name in (self.NOTES_ADD_URL, self.NOTES_EDIT_URL):
            with self.subTest(name=name):
                response = self.client_author.get(name)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
