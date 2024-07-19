import json

import pytest
from django.urls import reverse
from rest_framework import status

from scoap3.articles.models import Article
from scoap3.articles.util import parse_string_to_date_object
from scoap3.misc.models import PublicationInfo

pytestmark = pytest.mark.django_db


@pytest.fixture
def record(shared_datadir):
    contents = (shared_datadir / "workflow_record.json").read_text()
    return json.loads(contents)


class TestArticleViewSet:
    def test_get_article(self, client):
        url = reverse("api:article-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_article_from_workflow(self, client, user, record):
        client.force_login(user)

        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        assert (
            article.title
            == "The Effective QCD Running Coupling Constant and a Dirac Model for the Charmonium Spectrum"
        )

    def test_update_article_from_workflow(self, client, user, record):
        client.force_login(user)
        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        assert (
            article.title
            == "The Effective QCD Running Coupling Constant and a Dirac Model for the Charmonium Spectrum"
        )

        record["titles"][0]["title"] = "New title"
        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
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
        self, client, user, record
    ):
        client.force_login(user)
        del record["imprints"][0]["date"]
        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["publication_date"] == response.data["_created_at"]

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        assert article.publication_date is None

    def test_create_update_from_workflow_without_publication_date(
        self, client, user, record
    ):
        client.force_login(user)
        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id_with_publication_date = response.data["id"]
        article_with_publication_date = Article.objects.get(
            id=article_id_with_publication_date
        )
        assert article_with_publication_date.publication_date is not None

        del record["imprints"][0]["date"]
        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
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
        record,
    ):
        client.force_login(user)

        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
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
        record["imprints"][0]["date"] = "2024-06-20"
        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
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
        record,
    ):
        client.force_login(user)
        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id_with_journal_year = response.data["id"]
        publication_info_with_journal_year = PublicationInfo.objects.get(
            article_id=article_id_with_journal_year
        )
        assert publication_info_with_journal_year.volume_year == "2023"

        record["publication_info"][0]["year"] = "2024"
        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
            content_type="application/json",
        )
        article_id_with_updated_journal_year = response.data["id"]
        assert article_id_with_journal_year == article_id_with_updated_journal_year
        journal_info_with_updated_journal_year = PublicationInfo.objects.get(
            article_id=article_id_with_updated_journal_year
        )
        assert journal_info_with_updated_journal_year.volume_year == "2024"

        del record["publication_info"][0]["year"]
        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
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
        record,
    ):
        client.force_login(user)
        del record["publication_info"][0]["year"]
        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id_with_publication_date = response.data["id"]
        article_with_publication_date = PublicationInfo.objects.get(
            article_id=article_id_with_publication_date
        )
        assert article_with_publication_date.volume_year is None

        assert (
            response.data["publication_info"][0]["volume_year"]
            == parse_string_to_date_object(response.data["_created_at"]).year
        )

        record["publication_info"][0]["year"] = "2024"
        response = client.post(
            reverse("api:article-workflow-import-list"),
            record,
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
