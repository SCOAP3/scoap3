import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestAuthorViewSet:
    def test_get_article(self, client):
        url = reverse("api:author-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK


class TestAuthorIdentifierViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:authoridentifier-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:authoridentifier-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
