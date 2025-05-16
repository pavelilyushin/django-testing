import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from news.forms import BAD_WORDS
from news.models import Comment

User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_cant_post_comment(client, news):
    """Проверяет, что анонимный пользователь не может оставлять комментарии."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.post(url, data={'text': 'Комментарий'})
    assert response.status_code == 302
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authorized_user_can_post_comment(author_client, author, news):
    """Проверяет возможность авторизованного пользователя оставлять коммент."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    text = 'Текст комментария'
    author_client.post(url, data={'text': text})
    assert Comment.objects.count() == 1
    comment = Comment.objects.first()
    assert comment.text == text
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_comment_with_bad_words_not_published(author_client, news):
    """Проверяет валидацию комментариев с запрещенными словами."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    bad_word = BAD_WORDS[0]
    response = author_client.post(url, data={'text': f'Текст с {bad_word}'})
    assert Comment.objects.count() == 0
    form = response.context['form']
    assert 'text' in form.errors
    assert 'Не ругайтесь!' in str(form.errors['text'])


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    """Проверяет возможность автора редактировать свои комментарии."""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    new_text = 'Обновленный комментарий'
    response = author_client.post(url, data={'text': new_text})
    assert response.status_code == 302
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    """Проверяет возможность автора удалять свои комментарии."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.post(url)
    assert response.status_code == 302
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_edit_others_comments(user_client, comment):
    """Проверяет запрет на редактирование чужих комментариев."""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    original_text = comment.text
    new_text = 'Обновленный комментарий'
    response = user_client.post(url, data={'text': new_text})
    assert response.status_code == 404
    comment.refresh_from_db()
    assert comment.text == original_text


@pytest.mark.django_db
def test_user_cant_delete_others_comments(user_client, comment):
    """Проверяет запрет на удаление чужих комментариев."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = user_client.post(url)
    assert response.status_code == 404
    assert Comment.objects.count() == 1
