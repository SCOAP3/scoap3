import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestRecordViewSet:
    def test_get_record(self, client):
        url = reverse("api:records-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
