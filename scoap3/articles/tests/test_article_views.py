import pytest
from django.urls import reverse
from rest_framework import status

from scoap3.articles.models import Article

pytestmark = pytest.mark.django_db


class TestArticleViewSet:
    def test_get_article(self, client):
        url = reverse("api:article-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_create_article_from_workflow(self, client, user):
        client.force_login(user)
        data = {
            "license": [
                {
                    "url": "http://creativecommons.org/licenses/by/4.0/",
                    "license": "CC-BY-4.0",
                }
            ],
            "copyright": [{"statement": "The Author"}],
            "control_number": "81204",
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
                            "value": "Universidad Nacional de Colombia, Bogot\u00e1, Colombia",
                        }
                    ],
                    "full_name": "De Sanctis, M.",
                }
            ],
            "titles": [
                {
                    "title": "The Effective QCD Running Coupling Constant and a Dirac Model for the Charmonium Spectrum"
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
            "legacy": True,
        }
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

    def test_update_article_from_workflow(self, client, user):
        client.force_login(user)
        data = {
            "license": [
                {
                    "url": "http://creativecommons.org/licenses/by/4.0/",
                    "license": "CC-BY-4.0",
                }
            ],
            "copyright": [{"statement": "The Author"}],
            "control_number": "81204",
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
                            "value": "Universidad Nacional de Colombia, Bogot\u00e1, Colombia",
                        }
                    ],
                    "full_name": "De Sanctis, M.",
                }
            ],
            "titles": [
                {
                    "title": "The Effective QCD Running Coupling Constant and a Dirac Model for the Charmonium Spectrum"
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
            "legacy": True,
        }
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
        data["dois"].append({"value": "10.5506/APhysPolB.54.10-A5"})
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
