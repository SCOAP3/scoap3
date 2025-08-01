import pytest
from django.test import TestCase
from freezegun import freeze_time

from scoap3.articles.models import Article, ArticleIdentifier
from scoap3.articles.tasks import compliance_checks
from scoap3.misc.models import PublicationInfo, Publisher


@pytest.mark.django_db
@pytest.mark.vcr
class TestCheckDoiRegistrationTime(TestCase):
    def setUp(self):
        self.hindawi_publisher = Publisher.objects.create(name="Hindawi")
        self.aps_publisher = Publisher.objects.create(name="APS")

        self.article_data = {
            "title": "Test Article",
            "subtitle": "Test Subtitle",
            "abstract": "Test Abstract",
        }

        self.publication_data = {
            "journal_title": "Physical Review D",
        }

    def _create_test_article(self, publisher, doi_value):
        article = Article.objects.create(**self.article_data)

        PublicationInfo.objects.create(
            article_id=article, publisher=publisher, **self.publication_data
        )

        ArticleIdentifier.objects.create(
            identifier_type="DOI",
            identifier_value=doi_value,
            article_id=article,
        )

        article.save()
        return article

    def test_check_doi_registration_time_success(self):
        with freeze_time("2024-07-08"):
            article = self._create_test_article(
                self.hindawi_publisher, "10.1155/2024/6666609"
            )

            compliance_checks(article.id)
            report = article.report.first()
            self.assertEqual(report.check_doi_registration_time, True)

    def test_check_doi_registration_time_fail(self):
        with freeze_time("2024-07-10"):
            article = self._create_test_article(
                self.hindawi_publisher, "10.1155/2024/6666609"
            )

            compliance_checks(article.id)
            report = article.report.first()
            self.assertEqual(report.check_doi_registration_time, False)

    def test_check_doi_registration_time_aps_success(self):
        with freeze_time("2025-07-01"):
            article = self._create_test_article(self.aps_publisher, "10.1103/73rr-shyt")

            compliance_checks(article.id)
            report = article.report.first()
            self.assertEqual(report.check_doi_registration_time, True)

    def test_check_doi_registration_time_aps_fail(self):
        with freeze_time("2025-07-03"):
            article = self._create_test_article(self.aps_publisher, "10.1103/73rr-shyt")

            compliance_checks(article.id)
            report = article.report.first()
            self.assertEqual(report.check_doi_registration_time, False)
