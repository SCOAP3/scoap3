import json
import os
from pathlib import Path

import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from scoap3.articles.models import Article, ArticleIdentifier
from scoap3.users.tests.factories import UserFactory

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


pytestmark = pytest.mark.django_db


class TestArticleIdentifierViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:articleidentifier-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:articleidentifier-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


pytestmark = pytest.mark.django_db


class TestTheSameArticleCreationTwice(TestCase):
    @staticmethod
    def shared_datadir():
        return os.path.join(
            Path(__file__).parent.resolve(), "data", "record_failing_on_airflow.json"
        )

    def test_create_article_from_workflow(self):
        user = UserFactory()
        self.client.force_login(user)
        with open(self.shared_datadir()) as file:
            contents = file.read()
        data = json.loads(contents)
        response = self.client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        response = self.client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        doi = data.get("dois")[0].get("value")
        assert (
            len(
                ArticleIdentifier.objects.filter(
                    identifier_type="DOI", identifier_value=doi
                )
            )
            == 1
        )
