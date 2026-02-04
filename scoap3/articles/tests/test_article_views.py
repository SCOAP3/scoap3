import contextlib
import json
from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status

from scoap3.articles.documents import ArticleDocument
from scoap3.articles.models import Article
from scoap3.articles.util import parse_string_to_date_object
from scoap3.authors.models import Author
from scoap3.misc.models import PublicationInfo, Publisher

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
            == "The Effective QCD Running Coupling Constant and a Dirac Model for the "
            "Charmonium Spectrum"
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

    @pytest.mark.parametrize(
        "file_name",
        [
            "workflow_record_with_large_text_pdfa.json",
            "workflow_record_with_large_text_pdf_a.json",
            "workflow_record_with_large_text_pdf_slash_a.json",
        ],
    )
    def test_create_article_from_workflow_pdfa_behaviour(
        self, client, user, shared_datadir, file_name
    ):
        client.force_login(user)

        contents = (shared_datadir / file_name).read_text()
        data = json.loads(contents)

        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        assert article.related_files.first().filetype == "pdf/a"

    @pytest.mark.parametrize(
        "file_name",
        [
            "legacy_record_pdfa.json",
            "legacy_record_pdf_a.json",
            "legacy_record_pdf_slash_a.json",
        ],
    )
    def test_create_article_from_legacy_pdfa_behaviour(
        self, client, user, shared_datadir, file_name
    ):
        client.force_login(user)
        contents = (shared_datadir / file_name).read_text()
        data = json.loads(contents)

        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        assert article.related_files.first().filetype == "pdf/a"

    def test_create_article_from_workflow_ror(self, client, user, shared_datadir):
        client.force_login(user)

        contents = (shared_datadir / "workflow_article.json").read_text()
        data = json.loads(contents)

        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        ror = response.data["authors"][0]["affiliations"][0]["ror"]
        assert ror == "00x194q47"

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
        assert article.title == (
            "The Effective QCD Running Coupling Constant "
            "and a Dirac Model for the Charmonium Spectrum"
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

    def test_create_article_from_workflow_without_abstract(
        self, client, user, shared_datadir
    ):
        client.force_login(user)
        contents = (shared_datadir / "workflow_record.json").read_text()
        data = json.loads(contents)

        del data["abstracts"]
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "abstract" in response.data
        assert response.data["abstract"] == ""

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        assert article.abstract == ""

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

    def test_create_update_from_workflow_with_material(
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

        article_id_with_material = response.data["id"]
        publication_info_with_material = PublicationInfo.objects.get(
            article_id=article_id_with_material
        )
        assert publication_info_with_material.material == "article"

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

    def test_articles_from_workflows_duplicates(self, client, user):
        client.force_login(user)
        data = {
            "license": [
                {
                    "url": "http://creativecommons.org/licenses/by/4.0/",
                    "license": "CC-BY-4.0",
                }
            ],
            "copyright": [{"statement": "The Author"}],
            "_oai": {
                "updated": "2023-10-31T08:21:45Z",
                "id": "oai:repo.scoap3.org:81204",
                "sets": ["APPB"],
            },
            "dois": [{"value": "10.5506/APhysPolB.54.10-A3"}],
            "_files": [
                {
                    "checksum": "md5:2ff0ee8af466b72271926bcfed748017",
                    "filetype": "pdf",
                    "bucket": "e8c24dab-4bf6-403d-848a-fdafe0b62042",
                    "version_id": "9bdb249d-4805-4faa-b784-41b8a599ca74",
                    "key": "10.5506/APhysPolB.54.10-A3.pdf",
                    "size": 505407,
                },
                {
                    "checksum": "md5:b215d3b2e0697ac47c98c90f8c5a51f7",
                    "filetype": "pdfa",
                    "bucket": "e8c24dab-4bf6-403d-848a-fdafe0b62042",
                    "version_id": "69e24af7-3785-472b-80cc-948ff155e406",
                    "key": "10.5506/APhysPolB.54.10-A3.pdfa",
                    "size": 977378,
                },
            ],
            "record_creation_date": "2023-10-31T08:20:22.109303",
            "authors": [
                {
                    "affiliations": [
                        {
                            "country": "Colombia",
                            "value": (
                                "Universidad Nacional de Colombia, "
                                "Bogot\u00e1, Colombia"
                            ),
                        }
                    ],
                    "full_name": "De Sanctis, M.",
                }
            ],
            "titles": [
                {
                    "title": (
                        "The Effective QCD Running Coupling Constant "
                        "and a Dirac Model for the Charmonium Spectrum"
                    )
                }
            ],
            "arxiv_eprints": [{"categories": ["hep-ph"], "value": "2310.16258"}],
            "publication_info": [
                {
                    "page_end": "13",
                    "journal_title": "Acta Physica Polonica B",
                    "material": "article",
                    "journal_volume": "54",
                    "year": 2023,
                    "page_start": "A3.1",
                    "journal_issue": "10",
                }
            ],
            "$schema": "http://repo.scoap3.org/schemas/hep.json",
            "abstracts": [
                {
                    "value": 'The QCD <span class="it">effective charge</span> extracted from the experimental data is used to construct the vector interaction of a Dirac relativistic model for the charmonium spectrum. The process required to fit the spectrum is discussed and the relationship with a previous study of the vector interaction is analyzed.'  # noqa: E501
                }
            ],
            "imprints": [
                {"date": "2023-10-31", "publisher": "Jagiellonian University"}
            ],
            "acquisition_source": {
                "date": "2023-10-31T08:20:22.109321",
                "source": "Jagiellonian University",
                "method": "scroap3_push",
            },
        }
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        response2 = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response2.status_code == status.HTTP_200_OK

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        assert (
            article.title
            == "The Effective QCD Running Coupling Constant and a Dirac Model for the "
            "Charmonium Spectrum"
        )

        data2 = data.copy()
        data["titles"][0]["title"] = "New title"
        data["dois"].append({"value": "10.5506/APhysPolB.54.10-A5"})
        data["authors"] = [
            {
                "affiliations": [
                    {
                        "country": "Colombia",
                        "value": (
                            "Universidad Nacional de Colombia, Bogot\u00e1, Colombia"
                        ),
                    }
                ],
                "full_name": "De Sanctis, M.",
            },
            {
                "affiliations": [
                    {
                        "country": "Brazil",
                        "value": "Universidad Nacional de Brazil, Sao\u00e1, Brazil",
                    }
                ],
                "full_name": "Authorius, M.",
            },
        ]
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        all_authors = Author.objects.all()
        assert len(all_authors) == 2

        data2["authors"] = [
            {
                "affiliations": [
                    {
                        "country": "Colombia",
                        "value": (
                            "Universidad Nacional de Colombia, Bogot\u00e1, Colombia"
                        ),
                    }
                ],
                "full_name": "De Sanccctis, M.",
            },
            {
                "affiliations": [
                    {
                        "country": "Brazil",
                        "value": "Universidad Nacional de Brazil, Sao\u00e1, Brazil",
                    }
                ],
                "full_name": "Authorius, M.",
            },
        ]
        response = client.post(
            reverse("api:article-workflow-import-list"),
            data2,
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK

        all_authors = Author.objects.all()
        assert len(all_authors) == 2

        article_id = response.data["id"]
        article = Article.objects.get(id=article_id)
        expected_dois = [
            doi.identifier_value
            for doi in article.article_identifiers.filter(identifier_type="DOI").all()
        ]

        assert article.title == "New title"
        assert len(expected_dois) == 2
        assert "10.5506/APhysPolB.54.10-A5" in expected_dois
        assert "10.5506/APhysPolB.54.10-A3" in expected_dois


class TestArticleIdentifierViewSet:
    def test_get_article_identifier(self, client):
        url = reverse("api:articleidentifier-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("api:articleidentifier-detail", kwargs={"pk": 0})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestArticleStatsViewSet:
    @freeze_time("2022-03-16")
    def test_get_article_stats(self, client, user):
        client.force_login(user)

        with contextlib.suppress(Exception):
            ArticleDocument._index.delete(ignore=404)
        ArticleDocument.init()

        today = datetime.now().date()

        publisher = Publisher.objects.create(name="Test Publisher")

        article1 = Article.objects.create(
            publication_date=today - timedelta(days=1), title="Article 1"
        )
        PublicationInfo.objects.create(
            article_id=article1,
            journal_title="Journal A",
            journal_volume="1",
            journal_issue="1",
            page_start="1",
            page_end="10",
            artid="A1",
            volume_year="2022",
            journal_issue_date=today - timedelta(days=1),
            publisher=publisher,
        )

        article2 = Article.objects.create(
            publication_date=today - timedelta(days=10), title="Article 2"
        )
        PublicationInfo.objects.create(
            article_id=article2,
            journal_title="Journal B",
            journal_volume="1",
            journal_issue="1",
            page_start="1",
            page_end="10",
            artid="A2",
            volume_year="2022",
            journal_issue_date=today - timedelta(days=10),
            publisher=publisher,
        )

        article3 = Article.objects.create(
            publication_date=today - timedelta(days=5), title="Article 3"
        )
        PublicationInfo.objects.create(
            article_id=article3,
            journal_title="Journal A",
            journal_volume="1",
            journal_issue="1",
            page_start="1",
            page_end="10",
            artid="A3",
            volume_year="2022",
            journal_issue_date=today - timedelta(days=5),
            publisher=publisher,
        )

        article4 = Article.objects.create(
            publication_date=today - timedelta(days=40), title="Article 4"
        )
        PublicationInfo.objects.create(
            article_id=article4,
            journal_title="Journal C",
            journal_volume="1",
            journal_issue="1",
            page_start="1",
            page_end="10",
            artid="A4",
            volume_year="2022",
            journal_issue_date=today - timedelta(days=40),
            publisher=publisher,
        )

        ArticleDocument().update(article1, action="index")
        ArticleDocument().update(article2, action="index")
        ArticleDocument().update(article3, action="index")
        ArticleDocument().update(article4, action="index")

        ArticleDocument._index.refresh()

        url = reverse("api:article-stats-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        expected_other = {
            "yesterday": 1,
            "last_30_days": 3,
            "this_year": 4,
            "all": 4,
        }
        assert data.get("other") == expected_other

        expected_journals = {
            "Journal A": 2,
            "Journal B": 1,
            "Journal C": 1,
        }
        assert data.get("journals") == expected_journals
