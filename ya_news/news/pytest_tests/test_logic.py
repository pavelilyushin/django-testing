import pytest

from news.forms import BAD_WORDS
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_post_comment(client, news, detail_url):
    """Проверяет запрет на создание комментариев анонимным пользователем."""
    comments_count_before = Comment.objects.count()
    client.post(detail_url, data={'text': 'Комментарий'})
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


@pytest.mark.django_db
def test_authorized_user_can_post_comment(author_client,
                                          author, news, detail_url):
    """Проверяет возможность создания комментария авторизованным."""
    comment_ids = set(Comment.objects.values_list('id', flat=True))
    comments_count_before = Comment.objects.count()
    text = 'Текст комментария'
    author_client.post(detail_url, data={'text': text})
    new_comment = Comment.objects.exclude(id__in=comment_ids)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before + 1
    comment = new_comment.first()
    assert comment.text == text
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_comment_with_bad_words_not_published(author_client, news, detail_url):
    """Проверяет валидацию комментариев с запрещенными словами."""
    comments_count_before = Comment.objects.count()
    bad_word = BAD_WORDS[0]
    response = author_client.post(
        detail_url,
        data={'text': f'Текст с {bad_word}'}
    )
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before
    form = response.context['form']
    assert 'text' in form.errors
    assert 'Не ругайтесь!' in str(form.errors['text'])


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, edit_url):
    """Проверяет возможность автора редактировать свои комментарии."""
    comments_count_before = Comment.objects.count()
    new_text = 'Обновленный комментарий'
    author_client.post(edit_url, data={'text': new_text})
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == new_text
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author
    assert updated_comment.created == comment.created


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, delete_url):
    """Проверяет возможность автора удалять свои комментарии."""
    comments_count_before = Comment.objects.count()
    author_client.post(delete_url)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before - 1
    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_user_cant_edit_others_comments(user_client, comment, edit_url):
    """Проверяет запрет на редактирование чужих комментариев."""
    comments_count_before = Comment.objects.count()
    original_text = comment.text
    comment_id = comment.id
    new_text = 'Обновленный комментарий'
    response = user_client.post(edit_url, data={'text': new_text})
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before
    assert response.status_code == 404
    reloaded_comment = Comment.objects.get(id=comment_id)
    assert reloaded_comment.text == original_text
    assert reloaded_comment.news == comment.news
    assert reloaded_comment.author == comment.author
    assert reloaded_comment.created == comment.created


@pytest.mark.django_db
def test_user_cant_delete_others_comments(user_client, comment, delete_url):
    """Проверяет запрет на удаление чужих комментариев."""
    comment_before = Comment.objects.get(id=comment.id)
    comments_count_before = Comment.objects.count()
    response = user_client.post(delete_url)
    comment_after = Comment.objects.get(id=comment.id)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before
    assert response.status_code == 404
    assert Comment.objects.filter(id=comment.id)
    assert comment_after.text == comment_before.text
    assert comment_after.author == comment_before.author
