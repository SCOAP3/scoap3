import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

pytestmark = pytest.mark.django_db


class TestAuthorViewSet(APITestCase):
    def test_get_article(self):
        url = reverse("api:author-list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK


class TestAuthorIdentifierViewSet(APITestCase):
    def test_get_article_identifier(self):
        url = reverse("api:authoridentifier-list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:authoridentifier-detail", kwargs={"pk": 0})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
