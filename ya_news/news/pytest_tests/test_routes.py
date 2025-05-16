import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_page_available_to_anonymous_user(client):
    """Проверяет доступность главной страницы для анонимного пользователя."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_news_detail_available_to_anonymous_user(client, news):
    """Проверяет доступность страницы деталей новости для анонимов."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_edit_delete_pages_available_to_author(author_client, comment):
    """Проверяет доступность страниц редактирования и удаления комментария."""
    urls = [
        reverse('news:edit', kwargs={'pk': comment.pk}),
        reverse('news:delete', kwargs={'pk': comment.pk}),
    ]
    for url in urls:
        response = author_client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_redirected_to_login(client, comment):
    """Проверяет перенаправление анонимного пользователя на страницу входа."""
    urls = [
        reverse('news:edit', kwargs={'pk': comment.pk}),
        reverse('news:delete', kwargs={'pk': comment.pk}),
    ]
    login_url = reverse('users:login')
    for url in urls:
        response = client.get(url)
        assert response.status_code == 302
        assert login_url in response.url


@pytest.mark.django_db
def test_authenticated_user_cant_access_others_comments(user_client, comment):
    """Проверяет, что у пользователь нет доступа к чужим комментам."""
    urls = [
        reverse('news:edit', kwargs={'pk': comment.pk}),
        reverse('news:delete', kwargs={'pk': comment.pk}),
    ]
    for url in urls:
        response = user_client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
def test_auth_pages_available_to_anonymous_user(client):
    """Проверяет доступность страниц аутентификации для анонимов."""
    urls = [
        reverse('users:login'),
        reverse('users:signup'),
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code == 200

    logout_url = reverse('users:logout')

    response = client.get(logout_url)
    assert response.status_code in [200, 405]

    if response.status_code != 405:
        response = client.post(logout_url)
        assert response.status_code == 302
