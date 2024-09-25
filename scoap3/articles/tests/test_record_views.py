import json

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

        assert "_files" in metadata
        assert "abstracts" in metadata
        assert "arxiv_eprints" in metadata
        assert "authors" in metadata
        assert "collections" in metadata
        assert "control_number" in metadata
        assert "copyright" in metadata
        assert "dois" in metadata
        assert "imprints" in metadata
        assert "license" in metadata
        assert "page_nr" in metadata
        assert "publication_info" in metadata
        assert "record_creation_date" in metadata
        assert "titles" in metadata

    def test_get_record_json_structure_nested(self, client, license, user):
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

        assert "_files" in metadata
        _files = metadata["_files"]
        assert isinstance(_files, list)
        if _files:
            for file in _files:
                assert "filetype" in file
                assert "size" in file
                assert "key" in file

        assert "abstracts" in metadata
        abstracts = metadata["abstracts"]
        assert isinstance(abstracts, list)
        if abstracts:
            for abstract in abstracts:
                assert "source" in abstract
                assert "value" in abstract

        assert "arxiv_eprints" in metadata
        arxiv_eprints = metadata["arxiv_eprints"]
        assert isinstance(arxiv_eprints, list)
        if arxiv_eprints:
            for eprint in arxiv_eprints:
                assert "categories" in eprint
                assert isinstance(eprint["categories"], list)
                assert "value" in eprint
                assert isinstance(eprint["value"], list)

        assert "authors" in metadata
        authors = metadata["authors"]
        assert isinstance(authors, list)
        if authors:
            for author in authors:
                assert "full_name" in author
                assert "given_names" in author
                assert "surname" in author
                assert "orcid" in author
                assert isinstance(author["orcid"], list)

                assert "affiliations" in author
                affiliations = author["affiliations"]
                assert isinstance(affiliations, list)
                if affiliations:
                    for affiliation in affiliations:
                        assert "country" in affiliation
                        assert "organization" in affiliation
                        assert "value" in affiliation
                        assert "ror" in affiliation

        assert "collections" in metadata
        collections = metadata["collections"]
        assert isinstance(collections, list)
        if collections:
            for collection in collections:
                assert "primary" in collection

        assert "copyright" in metadata
        copyright = metadata["copyright"]
        assert isinstance(copyright, list)
        if copyright:
            for item in copyright:
                assert "statement" in item
                assert "holder" in item
                assert "year" in item

        assert "dois" in metadata
        dois = metadata["dois"]
        assert isinstance(dois, list)
        if dois:
            for doi in dois:
                assert "value" in doi

        assert "imprints" in metadata
        imprints = metadata["imprints"]
        assert isinstance(imprints, list)
        if imprints:
            for imprint in imprints:
                assert "date" in imprint
                assert "publisher" in imprint

        assert "license" in metadata
        licenses = metadata["license"]
        assert isinstance(licenses, list)
        if licenses:
            for license in licenses:
                assert "license" in license
                assert "url" in license

        assert "page_nr" in metadata
        assert isinstance(metadata["page_nr"], list)

        assert "publication_info" in metadata
        publication_info = metadata["publication_info"]
        assert isinstance(publication_info, list)
        if publication_info:
            for info in publication_info:
                assert "artid" in info
                assert "journal_issue" in info
                assert "journal_title" in info
                assert "journal_volume" in info
                assert "page_end" in info
                assert "page_start" in info
                assert "year" in info

        assert "record_creation_date" in metadata

        assert "titles" in metadata
        titles = metadata["titles"]
        assert isinstance(titles, list)
        if titles:
            for title in titles:
                assert "source" in title
                assert "title" in title

    def test_page_nr_is_int(self, client, license, user, shared_datadir):
        try:
            client.force_login(user)
            contents = (shared_datadir / "workflow_article.json").read_text()
            data = json.loads(contents)

            response = client.post(
                reverse("api:article-workflow-import-list"),
                data,
                content_type="application/json",
            )
            assert response.status_code == status.HTTP_200_OK
            article_data = response.json()
            print(article_data)

            url = reverse("api:records-detail", kwargs={"pk": article_data["id"]})
            response = client.get(url)
            record_data = response.json()
            print(record_data)

        except ValueError:
            pytest.fail("Conversion from string to integer failed")
