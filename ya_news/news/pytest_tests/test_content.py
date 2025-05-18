import pytest

from news.constants import NEWS_ON_HOME_PAGE

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count_on_home_page(client, news_list, home_url):
    """Проверяет количество новостей на главной странице."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert len(object_list) == NEWS_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list, home_url):
    """Проверяет правильность сортировки новостей на главной странице."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, news, comments, detail_url):
    """Проверяет правильность сортировки комментариев на странице новости."""
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    for i in range(len(all_comments) - 1):
        assert all_comments[i].created <= all_comments[i + 1].created


@pytest.mark.django_db
def test_anonymous_user_has_no_form(client, news, detail_url):
    """Проверяет отсутствие формы комментария для анонимного пользователя."""
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_user_has_form(author_client, news, detail_url):
    """Проверяет наличие формы комментария для авторизованного пользователя."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
