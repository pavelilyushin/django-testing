import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='Тестовая новость', text='Текст новости')


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Тестовый комментарий'
    )


@pytest.mark.django_db
def test_home_page_available_to_anonymous_user(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_news_detail_available_to_anonymous_user(client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_edit_delete_pages_available_to_author(author_client, comment):
    urls = [
        reverse('news:edit', kwargs={'pk': comment.pk}),
        reverse('news:delete', kwargs={'pk': comment.pk}),
    ]
    for url in urls:
        response = author_client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_redirected_to_login(client, comment):
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
    urls = [
        reverse('news:edit', kwargs={'pk': comment.pk}),
        reverse('news:delete', kwargs={'pk': comment.pk}),
    ]
    for url in urls:
        response = user_client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
def test_auth_pages_available_to_anonymous_user(client):
    urls = [
        reverse('users:login'),
        reverse('users:logout'),
        reverse('users:signup'),
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code == 200
