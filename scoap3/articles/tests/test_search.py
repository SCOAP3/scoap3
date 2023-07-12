import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def test_search_article(user, api_client):
    user_token = Token.objects.create(user=user)
    response = api_client.get(
        "/search/article",
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Token {user_token}",
        follow=True,
    )

    assert response.status_code == status.HTTP_200_OK
