from django.urls import reverse

from .common import NotesTestCase


class TestRoutes(NotesTestCase):
    """Класс для тестирования доступности страниц."""

    def test_pages_availability(self):
        """Проверяет доступность страниц для разных пользователей."""
        url_status_map = [
            ('notes:home', None, 200),
            ('users:login', None, 200),
            ('users:signup', None, 200),
            ('users:logout', None, 405),
            # Auth
            ('notes:list', None, 200, self.author_client),
            ('notes:add', None, 200, self.author_client),
            ('notes:success', None, 200, self.author_client),
            ('notes:detail', (self.note.slug,), 200, self.author_client),
            ('notes:edit', (self.note.slug,), 200, self.author_client),
            ('notes:delete', (self.note.slug,), 200, self.author_client),
            # Other
            ('notes:detail', (self.note.slug,), 404, self.reader_client),
            ('notes:edit', (self.note.slug,), 404, self.reader_client),
            ('notes:delete', (self.note.slug,), 404, self.reader_client),
        ]

        for name, args, expected_status, *client in url_status_map:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                test_client = client[0] if client else self.client
                response = test_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects(self):
        """Проверяет редиректы для анонимного пользователя."""
        login_url = reverse('users:login')
        urls = [
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        ]

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
