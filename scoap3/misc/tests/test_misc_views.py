import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestCountryViewSet:
    def test_get_article(self, client):
        url = reverse("api:country-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:country-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAffiliationViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:affiliation-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:affiliation-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestInstitutionIdentifierViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:institutionidentifier-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:institutionidentifier-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPublisherViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:publisher-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:publisher-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPublicationInfoViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:publicationinfo-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:publicationinfo-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestLicenseViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:license-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:license-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCopyrightViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:copyright-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:copyright-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestArticleArxivCategoryViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:articlearxivcategory-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:articlearxivcategory-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestExperimentalCollaborationViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:experimentalcollaboration-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:experimentalcollaboration-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestFunderViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:funder-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:funder-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRelatedMaterialViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:relatedmaterial-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:relatedmaterial-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
