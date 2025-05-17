import pytest
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone
from django.urls import reverse

from news.models import News, Comment

User = get_user_model()

NEWS_COUNT = 15
COMMENTS_COUNT = 5
NEWS_ON_HOME_PAGE = 10


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
    """Фикстура создает тестовые новости с разными датами публикации."""
    today = timezone.now().date()
    News.objects.all().delete()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=today - timedelta(days=index))
        for index in range(NEWS_COUNT)
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
    """Фикстура создает тестовые комментарии с разным временем создания."""
    now = timezone.now()
    Comment.objects.all().delete()
    for index in range(COMMENTS_COUNT):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}'
        )
        comment.created = now - timedelta(hours=index)
        comment.save()


@pytest.fixture
def home_url():
    """Фикстура возвращает URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    """Фикстура возвращает URL страницы новости."""
    return reverse('news:detail', kwargs={'pk': news.pk})


@pytest.fixture
def edit_url(comment):
    """Фикстура возвращает URL редактирования комментария."""
    return reverse('news:edit', kwargs={'pk': comment.pk})


@pytest.fixture
def delete_url(comment):
    """Фикстура возвращает URL удаления комментария."""
    return reverse('news:delete', kwargs={'pk': comment.pk})


@pytest.fixture
def login_url():
    """Фикстура возвращает URL страницы входа."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """Фикстура возвращает URL страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """Фикстура возвращает URL страницы регистрации."""
    return reverse('users:signup')
