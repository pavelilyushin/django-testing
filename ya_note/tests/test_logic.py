from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestLogic(TestCase):
    """Класс для тестирования логики работы."""

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
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def setUp(self):
        """Настройка тестовых клиентов."""
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

    def test_authenticated_user_can_create_note(self):
        """Аутентифицированный пользователь может создать заметку."""
        url = reverse('notes:add')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Аноним не может создать заметку."""
        url = reverse('notes:add')
        response = self.guest_client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_not_unique_slug(self):
        """Нельзя создать заметку с неуникальным slug."""
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            url, data=self.form_data, follow=True
            )
        self.assertContains(response, self.note.slug + WARNING)
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """При пустом slug генерируется автоматически."""
        url = reverse('notes:add')
        self.form_data.pop('slug')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.exclude(pk=self.note.pk)[0]
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_edit_note_without_changing_slug(self):
        """Редактирование заметки без изменения slug."""
        url = reverse('notes:edit', args=(self.note.slug,))
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Другой пользователь не может редактировать заметку."""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.reader_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, 404)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Автор может удалить заметку."""
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """Другой пользователь не может удалить заметку."""
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.reader_client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Note.objects.count(), 1)
