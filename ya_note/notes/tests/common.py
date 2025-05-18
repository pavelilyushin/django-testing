from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class NotesTestCase(TestCase):
    """Базовый класс для тестов с общими фикстурами."""

    @classmethod
    def setUpTestData(cls):
        """Создание общих тестовых данных."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='note-slug'
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.list_url = reverse('notes:list')
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')

    def setUp(self):
        """Настройка тестовых клиентов."""
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)
