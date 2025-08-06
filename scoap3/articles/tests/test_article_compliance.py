from datetime import date

import pytest
from django.test import TestCase
from freezegun import freeze_time

from scoap3.articles.admin import make_compliant
from scoap3.articles.models import (
    Article,
    ArticleFile,
    ArticleIdentifier,
    ComplianceReport,
)
from scoap3.articles.tasks import compliance_checks
from scoap3.authors.models import Author
from scoap3.misc.models import (
    Affiliation,
    ArticleArxivCategory,
    Country,
    License,
    PublicationInfo,
    Publisher,
)


@pytest.mark.django_db
@pytest.mark.vcr
class TestArticleCompliance(TestCase):
    def setUp(self):
        self.license = License.objects.create(
            name="CC-BY-3.0", url="https://creativecommons.org/licenses/by/3.0/"
        )
        self.publisher = Publisher.objects.create(
            name="Elsevier",
        )
        self.file_formats = ["pdf", "pdf/a", "xml"]
        with freeze_time("2023-09-29"):
            self.article = Article.objects.create(
                title="Test Article",
                subtitle="Test Subtitle",
                abstract="Test Abstract",
            )

        self.article_with_not_compliant_doi = Article.objects.create(
            title="Test Article",
            subtitle="Test Subtitle",
            abstract="Test Abstract",
        )

        self.article_with_not_compliant_title = Article.objects.create(
            title="Test editorial Article",
            subtitle="Test Subtitle",
            abstract="Test Abstract",
        )

        self.article_published_before_2023 = Article.objects.create(
            title="Test Article",
            subtitle="Test Subtitle",
            abstract="Test Abstract",
            publication_date=date(2022, 1, 1),
        )

    def test_create_article(self):
        self.publication_info = PublicationInfo.objects.create(
            journal_title="Physical Review D",
            article_id=self.article,
            publisher=self.publisher,
        )
        ArticleIdentifier.objects.create(
            identifier_type="DOI",
            identifier_value="10.1016/j.ijheatmasstransfer.2023.124726",
            article_id=self.article,
        )
        ArticleIdentifier.objects.create(
            identifier_type="arxiv",
            identifier_value=" hep-th/9711200",
            article_id=self.article,
        )
        ArticleArxivCategory.objects.create(
            primary=True,
            category="hep-th",
            article_id=self.article,
        )

        for file_format in self.file_formats:
            ArticleFile.objects.create(
                file=f"test.{file_format}",
                article_id=self.article,
                filetype=file_format,
            )
        self.article.related_licenses.add(self.license)
        self.article.save()
        compliance_checks(self.article.id)

        article = Article.objects.get(id=self.article.id)
        report = article.report.first()

        self.assertEqual(report.check_license, True)
        self.assertEqual(report.check_required_file_formats, True)
        self.assertEqual(report.check_article_type, True)
        self.assertEqual(report.check_arxiv_category, True)
        self.assertEqual(report.check_doi_registration_time, True)

    def test_create_article_with_not_compliant_doi(self):
        ArticleIdentifier.objects.create(
            identifier_type="DOI",
            identifier_value="10.1016/j.ijheatmasstransfer.2023.124726",
            article_id=self.article_with_not_compliant_doi,
        )

        compliance_checks(self.article_with_not_compliant_doi.id)
        article = Article.objects.get(id=self.article_with_not_compliant_doi.id)
        report = article.report.first()

        self.assertEqual(report.check_doi_registration_time, False)

    def test_create_article_with_missing_compliant_doi(self):
        compliance_checks(self.article_with_not_compliant_doi.id)
        article = Article.objects.get(id=self.article_with_not_compliant_doi.id)
        report = article.report.first()

        self.assertEqual(report.check_doi_registration_time, False)

    def test_create_article_with_not_compliant_title(self):
        compliance_checks(self.article_with_not_compliant_title.id)
        article = Article.objects.get(id=self.article_with_not_compliant_title.id)
        report = article.report.first()

        self.assertEqual(report.check_article_type, False)

    def test_create_article_with_not_compliant_file_format_no_publication_info(self):
        for file_format in self.file_formats:
            ArticleFile.objects.create(
                file=f"test.{file_format}",
                article_id=self.article,
                filetype=file_format,
            )

        compliance_checks(self.article.id)
        article = Article.objects.get(id=self.article.id)
        report = article.report.first()

        self.assertEqual(report.check_required_file_formats, False)
        self.assertEqual(
            report.check_required_file_formats_description,
            "No publication information found.",
        )

    def test_create_article_with_compliant_file_format(self):
        PublicationInfo.objects.create(
            journal_title="Adv. High Energy Phys.",
            article_id=self.article,
            publisher=self.publisher,
        )

        for file_format in self.file_formats:
            ArticleFile.objects.create(
                file=f"test.{file_format}",
                article_id=self.article,
                filetype=file_format,
            )

        compliance_checks(self.article.id)
        article = Article.objects.get(id=self.article.id)
        report = article.report.first()
        self.assertEqual(report.check_required_file_formats, True)
        self.assertEqual(
            report.check_required_file_formats_description,
            "All required file formats are present.",
        )

    def test_create_article_with_not_compliant_file_format(self):
        PublicationInfo.objects.create(
            journal_title="Adv. High Energy Phys.",
            article_id=self.article,
            publisher=self.publisher,
        )

        for file_format in self.file_formats[:1]:
            ArticleFile.objects.create(
                file=f"test.{file_format}",
                article_id=self.article,
                filetype=file_format,
            )

        compliance_checks(self.article.id)
        article = Article.objects.get(id=self.article.id)
        report = article.report.first()
        self.assertEqual(report.check_required_file_formats, False)

    def test_create_article_with_not_compliant_arxiv_category(self):
        ArticleIdentifier.objects.create(
            identifier_type="arxiv",
            identifier_value="eess.AS/9711200",
            article_id=self.article,
        )
        PublicationInfo.objects.create(
            journal_title="Physical Review D",
            article_id=self.article,
            publisher=self.publisher,
        )
        ArticleArxivCategory.objects.create(
            primary=True,
            category="eess-as",
            article_id=self.article,
        )
        compliance_checks(self.article.id)
        article = Article.objects.get(id=self.article.id)
        report = article.report.first()
        self.assertEqual(report.check_arxiv_category, False)

    def test_create_author_with_no_affiliation(self):
        Author.objects.create(
            article_id=self.article,
            last_name="ExampleSurname",
            first_name="ExampleName",
            email="ExampleName.ExampleSurname@gmail.com",
            author_order=100,
        )
        compliance_checks(self.article.id)
        article = Article.objects.get(id=self.article.id)
        report = article.report.first()
        self.assertEqual(report.check_authors_affiliation, False)

    def test_create_author_with_affiliation(self):
        Author.objects.create(
            article_id=self.article,
            last_name="ExampleSurname",
            first_name="ExampleName",
            email="ExampleName.ExampleSurname@gmail.com",
            author_order=100,
        )
        Country.objects.create(
            code="BE",
            name="Belgium",
        )
        author_id = (
            Author.objects.get(last_name="ExampleSurname", first_name="ExampleName"),
        )
        affiliation = Affiliation.objects.create(
            country=Country.objects.get(code="BE", name="Belgium"),
            value="Example",
            organization="Example Organization",
        )
        affiliation.author_id.set(author_id)

        compliance_checks(self.article.id)
        article = Article.objects.get(id=self.article.id)
        report = article.report.first()
        self.assertEqual(report.check_authors_affiliation, True)

    def test_create_article_with_not_compliant_category_having_not_partial_journal(
        self,
    ):
        ArticleIdentifier.objects.create(
            identifier_type="arxiv",
            identifier_value="eess.AS/9711200",
            article_id=self.article,
        )
        PublicationInfo.objects.create(
            journal_title="Some other journal",
            article_id=self.article,
            publisher=self.publisher,
        )
        ArticleArxivCategory.objects.create(
            primary=True,
            category="hep-th",
            article_id=self.article,
        )
        compliance_checks(self.article.id)
        article = Article.objects.get(id=self.article.id)
        report = article.report.first()
        self.assertEqual(report.check_arxiv_category, True)

    def test_create_article_published_before_2023(self):
        compliance_checks(self.article_published_before_2023.id)
        report = self.article_published_before_2023.report.first()

        self.assertEqual(report.compliant, True)

    def test_update_non_compliant_article_published_before_2023(self):
        compliance_checks(
            self.article_published_before_2023.id,
        )
        report = self.article_published_before_2023.report.first()
        self.assertEqual(report.compliant, True)

        compliance_checks(self.article_published_before_2023.id, after_update=True)
        report = self.article_published_before_2023.report.first()
        self.assertEqual(report.compliant, False)

    def test_mark_article_with_reports_as_compliant(self):
        compliance_checks(self.article.id)
        make_compliant(Article.objects.all())
        report = self.article.report.first()

        self.assertEqual(report.compliant, True)

    def test_mark_article_without_reports_as_compliant(self):
        ids = make_compliant(Article.objects.all())

        self.assertEqual(list(ids), [])

    def tearDown(self):
        ArticleIdentifier.objects.all().delete()
        ArticleFile.objects.all().delete()
        ComplianceReport.objects.all().delete()
        PublicationInfo.objects.all().delete()
        ArticleArxivCategory.objects.all().delete()
