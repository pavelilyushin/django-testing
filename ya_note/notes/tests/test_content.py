from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):
    """Класс для тестирования содержимого страниц."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='note-slug'
        )

    def setUp(self):
        """Настройка тестового клиента."""
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_note_in_list_for_author(self):
        """Заметка отображается в списке для автора."""
        url = reverse('notes:list')
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        """Заметка не отображается в списке для другого пользователя."""
        reader_client = Client()
        reader_client.force_login(self.reader)
        url = reverse('notes:list')
        response = reader_client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_create_edit_pages_contain_form(self):
        """Страницы создания и редактирования содержат форму."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
