import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestRecordViewSet:
    def test_get_record(self, client):
        url = reverse("api:records-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_post_record_not_allowed(self, client):
        url = reverse("api:records-list")
        response = client.post(url, data={})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_record_not_allowed(self, client):
        url = reverse("api:records-list")
        response = client.put(url, data={})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_patch_record_not_allowed(self, client):
        url = reverse("api:records-list")
        response = client.patch(url, data={})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_record_not_allowed(self, client):
        url = reverse("api:records-list")
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_record_json_structure(self, client, license, user):
        client.force_login(user)
        article = {
            "title": "string",
            "related_licenses": [license.id],
        }
        response = client.post(
            reverse("api:article-list"),
            data=article,
        )
        assert response.status_code == 201

        url = reverse("api:records-list")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert "id" in data["results"][0]
        assert "metadata" in data["results"][0]
        assert "updated" in data["results"][0]
        assert "created" in data["results"][0]

        metadata = data["results"][0]["metadata"]
        assert "control_number" in metadata
        assert "abstracts" in metadata
        assert "arxiv_eprints" in metadata
        assert "authors" in metadata
        assert "collections" in metadata
        assert "dois" in metadata
        assert "imprints" in metadata
        assert "license" in metadata
        assert "publication_info" in metadata
        assert "titles" in metadata

        authors = metadata["authors"]
        assert isinstance(authors, list)
        if authors:
            for author in authors:
                assert "full_name" in author
                assert "affiliations" in author
                affiliations = author["affiliations"]
                if affiliations:
                    for affiliation in affiliations:
                        assert "country" in affiliation
                        assert "organization" in affiliation
