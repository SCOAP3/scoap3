import pytest
from django.urls import reverse
from rest_framework import status

from scoap3.articles.models import Article

pytestmark = pytest.mark.django_db


class TestRobotUploadViewSet:
    def test_create_article_from_xml(self, client, user, shared_datadir):
        client.force_login(user)
        data = (shared_datadir / "test.xml").read_text()

        post_response = client.post(
            reverse("api:robot-upload-list"),
            data,
            content_type="application/xml",
        )
        assert post_response.status_code == status.HTTP_200_OK

        article = Article.objects.get(title="Robotupload test")

        get_response = client.get(
            reverse("api:article-detail", kwargs={"pk": article.id})
        )
        assert post_response.status_code == status.HTTP_200_OK

        # Title assertion
        assert get_response.data.get("title") == "Robotupload test"

        # Related files assertion (empty list)
        assert get_response.data.get("related_files") == []

        # Article identifiers
        article_identifiers = get_response.data.get("article_identifiers")
        assert len(article_identifiers) == 2
        assert article_identifiers[0]["identifier_type"] == "DOI"
        assert (
            article_identifiers[0]["identifier_value"] == "10.5506/APhysPolB.55.12-A2"
        )
        assert article_identifiers[0]["article_id"] == article.id

        assert article_identifiers[1]["identifier_type"] == "arXiv"
        assert article_identifiers[1]["identifier_value"] == "2411.02330"
        assert article_identifiers[1]["article_id"] == article.id

        # Publication info assertion
        publication_info = get_response.data.get("publication_info")
        assert len(publication_info) == 1
        pub_info = publication_info[0]
        assert pub_info["publisher"] == "Jagiellonian University"
        assert pub_info["journal_volume"] == "55"
        assert pub_info["journal_title"] == "Acta Physica Polonica B"
        assert pub_info["journal_issue"] == "12"
        assert pub_info["volume_year"] == "2024"

        # Authors assertion
        authors = get_response.data.get("authors")
        assert len(authors) == 4
        assert authors[0]["first_name"] == " J."
        assert authors[0]["last_name"] == "Ambjørn"
        assert (
            authors[0]["affiliations"][0]["value"]
            == "The Niels Bohr Institute, Copenhagen University, Denmark"
        )
        assert authors[0]["affiliations"][0]["country"] == "DK"

        assert authors[1]["first_name"] == " J."
        assert authors[1]["last_name"] == "Gizbert-Studnicki"
        assert (
            authors[1]["affiliations"][0]["value"]
            == "Institute of Theoretical Physics, Jagiellonian University, Kraków, Poland"
        )
        assert authors[1]["affiliations"][0]["country"] == "PL"

        assert authors[2]["first_name"] == " A."
        assert authors[2]["last_name"] == "Görlich"
        assert (
            authors[2]["affiliations"][0]["value"]
            == "Institute of Theoretical Physics, Jagiellonian University, Kraków, Poland"
        )
        assert authors[2]["affiliations"][0]["country"] == "PL"

        assert authors[3]["first_name"] == " D."
        assert authors[3]["last_name"] == "Németh"
        assert (
            authors[3]["affiliations"][0]["value"]
            == "IMAPP, Radboud University Nijmegen, The Netherlands"
        )
        assert authors[3]["affiliations"][0]["country"] == "NL"

        # Dates assertions
        assert get_response.data.get("publication_date") == "2025-01-07"

        # Abstract assertion
        abstract = get_response.data.get("abstract")
        assert abstract == (
            "<p>Causal Dynamical Triangulations (CDT) is a lattice theory of quantum gravity. "
            "It is shown how to identify the IR and the UV limits of this lattice theory with similar "
            "limits studied using the continuum, functional renormalization group (FRG) approach. "
            "The main technical tool in this study will be the so-called two-point function. "
            "It will allow us to identify a correlation length not directly related to the propagation "
            "of physical degrees of freedom.</p>"
        )
