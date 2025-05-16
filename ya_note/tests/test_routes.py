from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Класс для тестирования доступности страниц."""

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
        """Настройка тестовых клиентов."""
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

    def test_home_page_available_to_anonymous(self):
        """Главная страница доступна анонимному пользователю."""
        url = reverse('notes:home')
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_pages(self):
        """Страницы доступны аутентифицированному пользователю."""
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_note_pages_available_only_to_author(self):
        """Страницы заметки доступны только автору."""
        users_statuses = (
            (self.author_client, 200),
            (self.reader_client, 404),
        )
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for user, status in users_statuses:
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_user(self):
        """Анонимный пользователь перенаправляется на страницу логина."""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.guest_client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_available_to_all_users(self):
        """Страницы аутентификации доступны всем пользователям."""
        url_status_map = [
            ('users:login', None, 200),
            ('users:signup', None, 200),
            ('users:logout', None, 405),
        ]
        for name, args, expected_status in url_status_map:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected_status)
