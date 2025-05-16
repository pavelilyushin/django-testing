import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone
from datetime import timedelta
from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def author():
    """Фикстура создает и возвращает тестового пользователя с ролью автора."""
    return User.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    """Фикстура создает клиент с авторизованным автором."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def user():
    """Фикстура создает обычного тестового пользователя."""
    return User.objects.create(username='Пользователь')


@pytest.fixture
def user_client(user):
    """Фикстура создает клиент с авторизованным пользователем."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def news():
    """Фикстура создает и возвращает одну тестовую новость."""
    return News.objects.create(title='Тестовая новость', text='Текст новости')


@pytest.fixture
def news_list():
    """Фикстура создает 15 тестовых новостей с разными датами публикации."""
    today = timezone.now().date()
    News.objects.all().delete()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=today - timedelta(days=index)
        )
        for index in range(15)
    )


@pytest.fixture
def comment(author, news):
    """Фикстура создает тестовый комментарий."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Тестовый комментарий'
    )


@pytest.fixture
def comments(news, author):
    """Фикстура создает 5 тестовых комментариев с разным временем создания."""
    now = timezone.now()
    Comment.objects.all().delete()
    for index in range(5):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}'
        )
        comment.created = now - timedelta(hours=index)
        comment.save()
