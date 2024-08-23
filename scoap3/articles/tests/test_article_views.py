import json

import pytest
from django.urls import reverse
from rest_framework import status

from scoap3.articles.models import Article
from scoap3.articles.util import parse_string_to_date_object
from scoap3.misc.models import PublicationInfo

pytestmark = pytest.mark.django_db


class TestArticleViewSet:
    def test_get_article(self, client):
        url = reverse("api:article-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_article_from_workflow(self, client, user, shared_datadir):
        client.force_login(user)
        contents = (shared_datadir / "workflow_record.json").read_text()
        data = json.loads(contents)

        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        assert (
            article.title
            == "The Effective QCD Running Coupling Constant and a Dirac Model for the Charmonium Spectrum"
        )

    def test_create_article_from_workflow_with_large_text(
        self, client, user, shared_datadir
    ):
        client.force_login(user)
        contents = (shared_datadir / "workflow_record_with_large_text.json").read_text()
        data = json.loads(contents)

        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        assert (
            article.title
            == "Functional renormalization group approach to dipolar fixed "
            "point which is scale invariant but nonconformal"
        )

    def test_create_article_from_legacy(self, client, user, shared_datadir):
        client.force_login(user)
        contents = (shared_datadir / "legacy_record.json").read_text()
        data = json.loads(contents)

        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id = response.data["id"]

        assert article_id == int(data["control_number"])
        assert response.data["title"] == data["titles"][0]["title"]

        contents = (shared_datadir / "legacy_record_update.json").read_text()
        data_updated = json.loads(contents)

        response = client.post(
            reverse("api:article-workflow-import-list"),
            data_updated,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id = response.data["id"]

        assert article_id == int(data_updated["control_number"])
        assert response.data["title"] == data_updated["titles"][0]["title"]

    def test_update_article_from_workflow(self, client, user, shared_datadir):
        client.force_login(user)
        contents = (shared_datadir / "workflow_record.json").read_text()
        data = json.loads(contents)

        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        assert (
            article.title
            == "The Effective QCD Running Coupling Constant and a Dirac Model for the Charmonium Spectrum"
        )
        search_article_detail_url = reverse(
            "search:article-detail", kwargs={"pk": article_id}
        )

        search_response = client.get(
            search_article_detail_url,
            content_type="application/json",
        )
        assert search_response.status_code == status.HTTP_200_OK
        assert search_response.data["doi"] == data["dois"][0]["value"]
        assert (
            search_response.data["copyright"][0]["statement"]
            == data["copyright"][0]["statement"]
        )
        assert (
            search_response.data["publication_info"][0]["publisher"]
            == data["imprints"][0]["publisher"]
        )
        assert (
            search_response.data["authors"][0]["affiliations"][0]["country"]["code"]
            == "GB"
        )
        assert (
            search_response.data["authors"][0]["affiliations"][0]["country"]["name"]
            == "United Kingdom"
        )
        assert (
            search_response.data["authors"][1]["affiliations"][0]["country"]["code"]
            == "-"
        )
        assert (
            search_response.data["authors"][1]["affiliations"][0]["country"]["name"]
            == "-"
        )

        data["titles"][0]["title"] = "New title"
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        expected_dois = [
            doi.identifier_value
            for doi in article.article_identifiers.filter(identifier_type="DOI").all()
        ]

        assert article.title == "New title"
        assert len(expected_dois) == 1
        assert "10.5506/APhysPolB.54.10-A3" in expected_dois

    def test_create_article_from_workflow_without_publication_date(
        self, client, user, shared_datadir
    ):
        client.force_login(user)
        contents = (shared_datadir / "workflow_record.json").read_text()
        data = json.loads(contents)

        del data["imprints"][0]["date"]
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["publication_date"] == response.data["_created_at"]

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        assert article.publication_date is None

    def test_create_update_from_workflow_without_publication_date(
        self, client, user, shared_datadir
    ):
        client.force_login(user)
        contents = (shared_datadir / "workflow_record.json").read_text()
        data = json.loads(contents)
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id_with_publication_date = response.data["id"]
        article_with_publication_date = Article.objects.get(
            id=article_id_with_publication_date
        )
        assert article_with_publication_date.publication_date is not None

        del data["imprints"][0]["date"]
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id_without_publication_date = response.data["id"]
        assert article_id_with_publication_date == article_id_without_publication_date
        article_without_publication_date = Article.objects.get(
            id=article_id_without_publication_date
        )
        assert article_without_publication_date.publication_date is not None

    def test_create_update_from_workflow_with_publication_date(
        self,
        client,
        user,
        shared_datadir,
    ):
        client.force_login(user)
        contents = (shared_datadir / "workflow_record.json").read_text()
        data = json.loads(contents)

        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id_with_publication_date = response.data["id"]
        article_with_publication_date = Article.objects.get(
            id=article_id_with_publication_date
        )
        assert (
            article_with_publication_date.publication_date.strftime("%Y-%m-%d")
            == "2023-10-31"
        )
        data["imprints"][0]["date"] = "2024-06-20"
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id_with_updated_publication_date = response.data["id"]
        assert (
            article_id_with_publication_date == article_id_with_updated_publication_date
        )
        article_with_updated_publication_date = Article.objects.get(
            id=article_id_with_updated_publication_date
        )
        assert (
            article_with_updated_publication_date.publication_date.strftime("%Y-%m-%d")
            == "2024-06-20"
        )

    def test_create_update_from_workflow_with_journal_year(
        self,
        client,
        user,
        shared_datadir,
    ):
        client.force_login(user)
        contents = (shared_datadir / "workflow_record.json").read_text()
        data = json.loads(contents)

        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id_with_journal_year = response.data["id"]
        publication_info_with_journal_year = PublicationInfo.objects.get(
            article_id=article_id_with_journal_year
        )
        assert publication_info_with_journal_year.volume_year == "2023"

        data["publication_info"][0]["year"] = "2024"
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        article_id_with_updated_journal_year = response.data["id"]
        assert article_id_with_journal_year == article_id_with_updated_journal_year
        journal_info_with_updated_journal_year = PublicationInfo.objects.get(
            article_id=article_id_with_updated_journal_year
        )
        assert journal_info_with_updated_journal_year.volume_year == "2024"

        del data["publication_info"][0]["year"]
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        journal_info_with_deleted_journal_year = PublicationInfo.objects.get(
            article_id=article_id_with_journal_year
        )
        assert journal_info_with_deleted_journal_year.volume_year == "2024"

    def test_create_update_from_workflow_without_journal_year(
        self,
        client,
        user,
        shared_datadir,
    ):
        client.force_login(user)
        contents = (shared_datadir / "workflow_record.json").read_text()
        data = json.loads(contents)

        del data["imprints"][0]
        del data["publication_info"][0]
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id_with_publication_date = response.data["id"]

        try:
            article_with_publication_date = PublicationInfo.objects.get(
                article_id=article_id_with_publication_date
            )
        except PublicationInfo.DoesNotExist:
            article_with_publication_date = None

        assert article_with_publication_date is None

        data = json.loads(contents)
        del data["publication_info"][0]["year"]

        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        assert (
            response.data["publication_info"][0]["volume_year"]
            == parse_string_to_date_object(response.data["_created_at"]).year
        )

        data["publication_info"][0]["year"] = "2024"
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id_with_updated_publication_date = response.data["id"]
        assert (
            article_id_with_publication_date == article_id_with_updated_publication_date
        )
        article_with_updated_publication_date = PublicationInfo.objects.get(
            article_id=article_id_with_updated_publication_date
        )
        assert article_with_updated_publication_date.volume_year == "2024"


class TestArticleIdentifierViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:articleidentifier-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:articleidentifier-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
