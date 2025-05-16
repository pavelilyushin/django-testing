import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from news.models import News, Comment
from news.forms import CommentForm


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
def news():
    """Фикстура создает и возвращает одну тестовую новость с базовыми данными."""
    return News.objects.create(title='Тестовая новость', text='Текст новости')


@pytest.fixture
def author(django_user_model):
    """Фикстура создает и возвращает тестового пользователя с ролью автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def comments(news, author):
    """Фикстура создает 5 тестовых комментариев с разным временем создания."""
    now = timezone.now()
    Comment.objects.all().delete()
    for index in range(5):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}')
        comment.created = now - timedelta(hours=index)
        comment.save()


@pytest.mark.django_db
def test_news_count_on_home_page(client, news_list):
    """Проверяет, что на главной странице отображается не более 10 новостей."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) <= 10


@pytest.mark.django_db
def test_news_order(client, news_list):
    """Проверяет правильность сортировки новостей на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, news, comments):
    """Проверяет правильность сортировки комментариев на странице новости."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    for i in range(len(all_comments) - 1):
        assert all_comments[i].created <= all_comments[i+1].created


@pytest.mark.django_db
def test_anonymous_user_has_no_form(client, news):
    """Проверяет отсутствие формы комментария для анонимного пользователя."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_user_has_form(client, django_user_model, news):
    """Проверяет наличие формы комментария для авторизованного пользователя."""
    user = django_user_model.objects.create(username='testuser')
    client.force_login(user)
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
