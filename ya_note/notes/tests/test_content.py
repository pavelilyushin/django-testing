from django.urls import reverse
from notes.forms import NoteForm

from .common import NotesTestCase


class TestContent(NotesTestCase):
    """Класс для тестирования содержимого страниц."""

    def test_note_in_list_for_author(self):
        """Заметка отображается в списке для автора."""
        url = reverse('notes:list')
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        """Заметка не отображается в списке для другого пользователя."""
        url = reverse('notes:list')
        response = self.reader_client.get(url)
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
