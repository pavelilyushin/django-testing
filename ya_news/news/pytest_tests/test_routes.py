import pytest

from http import HTTPStatus


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name, client_fixture, expected_status',
    [
        ('home_url', 'client', HTTPStatus.OK),
        ('detail_url', 'client', HTTPStatus.OK),
        ('edit_url', 'author_client', HTTPStatus.OK),
        ('delete_url', 'author_client', HTTPStatus.OK),
        ('login_url', 'client', HTTPStatus.OK),
        ('signup_url', 'client', HTTPStatus.OK),
        ('logout_url', 'client', HTTPStatus.METHOD_NOT_ALLOWED),
        ('edit_url', 'client', HTTPStatus.FOUND),
        ('delete_url', 'client', HTTPStatus.FOUND),
        ('edit_url', 'user_client', HTTPStatus.NOT_FOUND),
        ('delete_url', 'user_client', HTTPStatus.NOT_FOUND),
    ]
)
def test_pages_availability(
    request, url_name, client_fixture, expected_status
):
    """Проверяет доступность страниц для разных пользователей."""
    client = request.getfixturevalue(client_fixture)
    url = request.getfixturevalue(url_name)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name',
    ['edit_url', 'delete_url']
)
def test_redirects(client, url_name, login_url, request):
    """Проверяет редиректы для анонимного пользователя."""
    url = request.getfixturevalue(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert login_url in response.url
