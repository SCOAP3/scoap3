import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


class TestAuthorViewSet:
    def test_get_article(self, api_client):
        url = reverse("api:author-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK


class TestAuthorIdentifierViewSet:
    def test_get_article_identifier(self, api_client):
        url = reverse("api:authoridentifier-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:authoridentifier-detail", kwargs={"pk": 0})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
