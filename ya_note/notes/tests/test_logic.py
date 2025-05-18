from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .common import NotesTestCase


class TestLogic(NotesTestCase):
    """Класс для тестирования логики работы с заметками."""

    def test_authenticated_user_can_create_note(self):
        """Аутентифицированный пользователь может создать заметку."""
        notes_count = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count + 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        redirect_url = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_not_unique_slug(self):
        """Нельзя создать заметку с неуникальным slug."""
        notes_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            self.add_url, data=self.form_data, follow=True)
        self.assertContains(response, self.note.slug + WARNING)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_empty_slug(self):
        """При пустом slug генерируется автоматически."""
        notes_count = Note.objects.count()
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count + 1)
        new_note = Note.objects.exclude(pk=self.note.pk)[0]
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        notes_count = Note.objects.count()
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count)
        edited_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(edited_note.title, self.form_data['title'])
        self.assertEqual(edited_note.text, self.form_data['text'])
        self.assertEqual(edited_note.slug, self.form_data['slug'])

    def test_edit_note_without_changing_slug(self):
        """Редактирование заметки без изменения slug."""
        notes_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count)
        edited_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(edited_note.title, self.form_data['title'])
        self.assertEqual(edited_note.text, self.form_data['text'])
        self.assertEqual(edited_note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Другой пользователь не может редактировать заметку."""
        notes_count = Note.objects.count()
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Note.objects.count(), notes_count)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Автор может удалить заметку."""
        notes_count = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_other_user_cant_delete_note(self):
        """Другой пользователь не может удалить заметку."""
        notes_count = Note.objects.count()
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Note.objects.count(), notes_count)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
