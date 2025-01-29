import pytest
from django.test import TestCase

from scoap3.articles.models import Article, ArticleIdentifier
from scoap3.authors.models import Author, AuthorIdentifier
from scoap3.misc.models import (
    Affiliation,
    Country,
    InstitutionIdentifier,
    PublicationInfo,
    Publisher,
    RelatedMaterial,
)
from scoap3.utils.tools import year_export


@pytest.mark.django_db
@pytest.mark.vcr
class TestYearExport(TestCase):
    def setUp(self):
        self.publisher_1 = Publisher.objects.create(name="Elsevier")
        self.publisher_2 = Publisher.objects.create(name="Springer")

        self.country_gb = Country.objects.create(code="GB", name="United Kingdom")
        self.country_fr = Country.objects.create(code="FR", name="France")
        self.country_jp = Country.objects.create(code="JP", name="Japan")
        self.country_be = Country.objects.create(code="BE", name="Belgium")
        self.country_br = Country.objects.create(code="BR", name="Brazil")
        self.country_it = Country.objects.create(code="IT", name="Italy")
        self.country_es = Country.objects.create(code="ES", name="Spain")

        self.publisher_1.save()
        self.publisher_2.save()

        self.country_gb.save()
        self.country_fr.save()
        self.country_jp.save()
        self.country_be.save()
        self.country_br.save()
        self.country_it.save()
        self.country_es.save()

    def create_article(
        self,
        title,
        subtitle,
        abstract,
        publication_date,
        doi_value,
        publisher,
        journal_title,
        author_data,
        country,
        affiliation_value,
    ):
        related_material_software_type = RelatedMaterial.objects.create(
            title="Test Software material",
            doi="TestMatSoftDOI",
            related_material_type="software",
        )

        related_material_dataset_type = RelatedMaterial.objects.create(
            title="Test Dataset material",
            doi="TestMatDataDOI",
            related_material_type="dataset",
        )

        article = Article.objects.create(
            title=title,
            subtitle=subtitle,
            abstract=abstract,
            publication_date=publication_date,
        )
        article.related_materials.add(related_material_software_type)
        article.related_materials.add(related_material_dataset_type)

        doi = ArticleIdentifier.objects.create(
            article_id=article,
            identifier_type="DOI",
            identifier_value=doi_value,
        )

        publication_info = PublicationInfo.objects.create(
            journal_title=journal_title,
            article_id=article,
            publisher=publisher,
        )

        author = Author.objects.create(article_id=article, **author_data)

        orcid = AuthorIdentifier.objects.create(
            author_id=author, identifier_type="ORCID", identifier_value="1000-1000-1000"
        )

        affiliation = Affiliation.objects.create(
            country=country,
            value=affiliation_value,
            organization="Example Organization",
        )
        affiliation.author_id.add(author)

        ror = InstitutionIdentifier.objects.create(
            affiliation_id=affiliation,
            identifier_type="ROR",
            identifier_value="123",
        )

        doi.save()
        publication_info.save()
        author.save()
        affiliation.save()
        ror.save()
        related_material_software_type.save()
        related_material_dataset_type.save()
        orcid.save()
        article.save()

        return article

    def test_year_export_multiple(self):
        self.create_article(
            title="Test Article",
            subtitle="Test Subtitle",
            abstract="Test Abstract",
            publication_date="2024-01-01",
            doi_value="TestDOI6",
            publisher=self.publisher_1,
            journal_title="Adv. High Energy Phys.",
            author_data={
                "last_name": "ExampleSurname",
                "first_name": "ExampleName",
                "email": "ExampleName.ExampleSurname@gmail.com",
                "author_order": 100,
            },
            country=self.country_it,
            affiliation_value="Example",
        )

        self.create_article(
            title="Test Article 2",
            subtitle="Test Subtitle 2",
            abstract="Test Abstract 2",
            publication_date="2024-02-02",
            doi_value="TestDOI7",
            publisher=self.publisher_1,
            journal_title="Adv. High Energy Phys.",
            author_data={
                "last_name": "ExampleSurname2",
                "first_name": "ExampleName2",
                "email": "ExampleName2.ExampleSurname2@gmail.com",
                "author_order": 100,
            },
            country=self.country_it,
            affiliation_value="Example2",
        )

        self.create_article(
            title="Test Article 3",
            subtitle="Test Subtitle 3",
            abstract="Test Abstract 3",
            publication_date="2024-03-03",
            doi_value="TestDOI8",
            publisher=self.publisher_2,
            journal_title="Adv. High Energy Phys.",
            author_data={
                "last_name": "ExampleSurname3",
                "first_name": "ExampleName3",
                "email": "ExampleName3.ExampleSurname3@gmail.com",
                "author_order": 100,
            },
            country=self.country_it,
            affiliation_value="Example3",
        )

        result = year_export("2024-01-01", "2024-05-05", "Elsevier")
        expected_result = {
            "header": [
                "year",
                "journal",
                "doi",
                "publication_date",
                "arxiv number",
                "primary arxiv category",
                "total number of authors",
                "total number of ORCIDs linked to the authors",
                "total number of affiliations",
                "total number of ROR linked with the affiliations",
                "total number of related materials, type dataset",
                "total number of related materials, type software",
            ],
            "data": [
                [
                    2024,
                    "Adv. High Energy Phys.",
                    "TestDOI6",
                    "2024-01-01",
                    None,
                    None,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                ],
                [
                    2024,
                    "Adv. High Energy Phys.",
                    "TestDOI7",
                    "2024-02-02",
                    None,
                    None,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                ],
            ],
        }

        result["data"].sort(key=lambda x: x[2])
        expected_result["data"].sort(key=lambda x: x[2])

        assert result == expected_result

    def test_year_export_no_data(self):
        result = year_export("2024-01-01", "2024-05-05", "Springer")
        expected_result = {
            "header": [
                "year",
                "journal",
                "doi",
                "publication_date",
                "arxiv number",
                "primary arxiv category",
                "total number of authors",
                "total number of ORCIDs linked to the authors",
                "total number of affiliations",
                "total number of ROR linked with the affiliations",
                "total number of related materials, type dataset",
                "total number of related materials, type software",
            ],
            "data": [],
        }

        assert result == expected_result

    def tearDown(self):
        Publisher.objects.all().delete()
        ArticleIdentifier.objects.all().delete()
        Article.objects.all().delete()
        PublicationInfo.objects.all().delete()
        Author.objects.all().delete()
        Affiliation.objects.all().delete()
        Country.objects.all().delete()
        AuthorIdentifier.objects.all().delete()
        RelatedMaterial.objects.all().delete()
        InstitutionIdentifier.objects.all().delete()
