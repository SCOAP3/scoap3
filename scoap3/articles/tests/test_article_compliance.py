import pytest
from django.test import TestCase
from freezegun import freeze_time

from scoap3.articles.models import (
    Article,
    ArticleFile,
    ArticleIdentifier,
    ComplianceReport,
)
from scoap3.articles.tasks import compliance_checks
from scoap3.misc.models import ArticleArxivCategory, License, PublicationInfo, Publisher


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
        self.file_formats = ["pdf", "pdf_a", "xml"]
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
            )
        self.article.related_licenses.add(self.license)
        self.article.save()
        compliance_checks(self.article.id)

        article = Article.objects.get(id=self.article.id)
        report = article.report.first()

        self.assertEqual(report.check_license, True)
        self.assertEqual(report.check_file_formats, True)
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

    def test_create_article_with_not_compliant_file_format(self):
        for file_format in self.file_formats[:2]:
            ArticleFile.objects.create(
                file=f"test.{file_format}",
                article_id=self.article,
            )

        compliance_checks(self.article.id)
        article = Article.objects.get(id=self.article.id)
        report = article.report.first()

        self.assertEqual(report.check_file_formats, False)
        self.assertEqual(
            report.check_file_formats_description,
            f"Missing required file formats: {self.file_formats[-1]}.",
        )

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
        self.assertEqual(report.check_arxiv_category, False)

    def tearDown(self):
        ArticleIdentifier.objects.all().delete()
        ArticleFile.objects.all().delete()
        ComplianceReport.objects.all().delete()
        PublicationInfo.objects.all().delete()
        ArticleArxivCategory.objects.all().delete()
