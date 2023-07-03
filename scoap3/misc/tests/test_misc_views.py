import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


class TestCountryViewSet:
    def test_get_article(self, api_client):
        url = reverse("api:country-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:country-detail", kwargs={"pk": 0})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAffiliationViewSet:
    def test_get_article_identifier(self, api_client):
        url = reverse("api:affiliation-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:affiliation-detail", kwargs={"pk": 0})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestInstitutionIdentifierViewSet:
    def test_get_article_identifier(self, api_client):
        url = reverse("api:institutionidentifier-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:institutionidentifier-detail", kwargs={"pk": 0})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPublisherViewSet:
    def test_get_article_identifier(self, api_client):
        url = reverse("api:publisher-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:publisher-detail", kwargs={"pk": 0})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPublicationInfoViewSet:
    def test_get_article_identifier(self, api_client):
        url = reverse("api:publicationinfo-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:publicationinfo-detail", kwargs={"pk": 0})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestLicenseViewSet:
    def test_get_article_identifier(self, api_client):
        url = reverse("api:license-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:license-detail", kwargs={"pk": 0})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCopyrightViewSet:
    def test_get_article_identifier(self, api_client):
        url = reverse("api:copyright-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:copyright-detail", kwargs={"pk": 0})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestArticleArxivCategoryViewSet:
    def test_get_article_identifier(self, api_client):
        url = reverse("api:articlearxivcategory-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:articlearxivcategory-detail", kwargs={"pk": 0})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestExperimentalCollaborationViewSet:
    def test_get_article_identifier(self, api_client):
        url = reverse("api:experimentalcollaboration-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:experimentalcollaboration-detail", kwargs={"pk": 0})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestFunderViewSet:
    def test_get_article_identifier(self, api_client):
        url = reverse("api:funder-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:funder-detail", kwargs={"pk": 0})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRelatedMaterialViewSet:
    def test_get_article_identifier(self, api_client):
        url = reverse("api:relatedmaterial-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:relatedmaterial-detail", kwargs={"pk": 0})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
