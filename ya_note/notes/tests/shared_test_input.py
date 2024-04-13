from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note

User = get_user_model()


class SharedTestInput(TestCase):

    @classmethod
    def setUpTestData(
        cls,
        generate_single_note=False,
        generate_note_list_author=False
    ):
        cls.user_author = User.objects.create(username='author')
        cls.client_author = Client()
        cls.client_author.force_login(cls.user_author)
        cls.user_another = User.objects.create(username='another')
        cls.client_another = Client()
        cls.client_another.force_login(cls.user_another)

        if generate_single_note:
            cls.note = Note.objects.create(
                title='Заметка 1',
                text='Просто текст',
                author=cls.user_author,
                slug='Zametka-1'
            )

        if generate_note_list_author:
            cls.notes = Note.objects.bulk_create(
                Note(
                    title=f'Заметка {index}',
                    text='Просто текст.',
                    author=cls.user_author,
                    slug=f'Zametka-{index}'
                )for index in range(11)
            )
