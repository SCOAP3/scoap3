import pytest
from django.test import TestCase

from scoap3.articles.models import Article, ArticleIdentifier
from scoap3.authors.models import Author
from scoap3.misc.models import Affiliation, Country, PublicationInfo, Publisher
from scoap3.utils.tools import author_export


@pytest.mark.django_db
@pytest.mark.vcr
@pytest.mark.usefixtures("rebuild_opensearch_index")
class TestAuthorExport(TestCase):
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
        article = Article.objects.create(
            title=title,
            subtitle=subtitle,
            abstract=abstract,
            publication_date=publication_date,
        )

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

        affiliation = Affiliation.objects.create(
            country=country,
            value=affiliation_value,
            organization="Example Organization",
        )
        affiliation.author_id.add(author)

        doi.save()
        publication_info.save()
        author.save()
        affiliation.save()
        article.save()

        return article

    def test_author_export_no_data(self):
        result = author_export("2024", "IN")
        expected_result = {
            "header": [
                "year",
                "journal",
                "doi",
                "arxiv number",
                "primary arxiv category",
                "author",
                "country",
                "affiliation",
                "total number of authors",
            ],
            "data": [],
        }

        assert result == expected_result

    def test_author_export_correct_year_wrong_country(self):
        self.create_article(
            title="Test Article",
            subtitle="Test Subtitle",
            abstract="Test Abstract",
            publication_date="2024-01-01",
            doi_value="TestDOI2",
            publisher=self.publisher_1,
            journal_title="Adv. High Energy Phys.",
            author_data={
                "last_name": "ExampleSurname",
                "first_name": "ExampleName",
                "email": "ExampleName.ExampleSurname@gmail.com",
                "author_order": 100,
            },
            country=self.country_fr,
            affiliation_value="Example",
        )

        result = author_export("2024", "JP")
        expected_result = {
            "header": [
                "year",
                "journal",
                "doi",
                "arxiv number",
                "primary arxiv category",
                "author",
                "country",
                "affiliation",
                "total number of authors",
            ],
            "data": [],
        }

        assert result == expected_result

    def test_author_export_wrong_year_correct_country(self):
        self.create_article(
            title="Test Article",
            subtitle="Test Subtitle",
            abstract="Test Abstract",
            publication_date="2024-01-01",
            doi_value="TestDOI3",
            publisher=self.publisher_1,
            journal_title="Adv. High Energy Phys.",
            author_data={
                "last_name": "ExampleSurname",
                "first_name": "ExampleName",
                "email": "ExampleName.ExampleSurname@gmail.com",
                "author_order": 100,
            },
            country=self.country_be,
            affiliation_value="Example",
        )

        result = author_export("2023", "BE")
        expected_result = {
            "header": [
                "year",
                "journal",
                "doi",
                "arxiv number",
                "primary arxiv category",
                "author",
                "country",
                "affiliation",
                "total number of authors",
            ],
            "data": [],
        }

        assert result == expected_result

    def test_author_export_filtering(self):
        self.create_article(
            title="Test Article",
            subtitle="Test Subtitle",
            abstract="Test Abstract",
            publication_date="2024-01-01",
            doi_value="TestDOI4",
            publisher=self.publisher_1,
            journal_title="Adv. High Energy Phys.",
            author_data={
                "last_name": "ExampleSurname",
                "first_name": "ExampleName",
                "email": "ExampleName.ExampleSurname@gmail.com",
                "author_order": 100,
            },
            country=self.country_br,
            affiliation_value="Example",
        )

        self.create_article(
            title="Test Article 2",
            subtitle="Test Subtitle 2",
            abstract="Test Abstract 2",
            publication_date="2024-02-02",
            doi_value="TestDOI5",
            publisher=self.publisher_2,
            journal_title="Adv. High Energy Phys.",
            author_data={
                "last_name": "ExampleSurname2",
                "first_name": "ExampleName2",
                "email": "ExampleName2.ExampleSurname2@gmail.com",
                "author_order": 100,
            },
            country=self.country_es,
            affiliation_value="Example2",
        )

        result = author_export("2024", "BR")
        expected_result = {
            "header": [
                "year",
                "journal",
                "doi",
                "arxiv number",
                "primary arxiv category",
                "author",
                "country",
                "affiliation",
                "total number of authors",
            ],
            "data": [
                [
                    2024,
                    "Adv. High Energy Phys.",
                    "TestDOI4",
                    None,
                    None,
                    "ExampleName ExampleSurname",
                    "BR",
                    "Example",
                    1,
                ]
            ],
        }

        assert result == expected_result

    def test_author_export_multiple(self):
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
            publisher=self.publisher_2,
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

        result = author_export("2024", "IT")
        result["data"].sort(key=lambda x: x[2])

        expected_result = {
            "header": [
                "year",
                "journal",
                "doi",
                "arxiv number",
                "primary arxiv category",
                "author",
                "country",
                "affiliation",
                "total number of authors",
            ],
            "data": sorted(
                [
                    [
                        2024,
                        "Adv. High Energy Phys.",
                        "TestDOI6",
                        None,
                        None,
                        "ExampleName ExampleSurname",
                        "IT",
                        "Example",
                        1,
                    ],
                    [
                        2024,
                        "Adv. High Energy Phys.",
                        "TestDOI7",
                        None,
                        None,
                        "ExampleName2 ExampleSurname2",
                        "IT",
                        "Example2",
                        1,
                    ],
                ],
                key=lambda x: x[2],
            ),
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
