import csv
import io

from django.contrib import admin
from django.http import HttpRequest
from django.test import RequestFactory, TestCase

from scoap3.articles.admin import ComplianceReportAdmin
from scoap3.articles.models import Article, ArticleIdentifier, ComplianceReport
from scoap3.misc.models import PublicationInfo, Publisher


class ExportAsCSVTest(TestCase):
    def setUp(self):
        article = Article.objects.create(
            title="Test Article",
            subtitle="Test Subtitle",
            abstract="Test Abstract",
        )
        ArticleIdentifier.objects.create(
            identifier_type="DOI",
            identifier_value="10.1000/000000",
            article_id=article,
        )
        publisher = Publisher.objects.create(
            name="Test Publisher",
        )

        PublicationInfo.objects.create(
            journal_title="Physical Review D",
            article_id=article,
            publisher=publisher,
        )

        self.report = ComplianceReport.objects.create(article=article)
        self.second_report = ComplianceReport.objects.create(article=article)

        self.factory = RequestFactory()
        self.model_admin = ComplianceReportAdmin(Article, admin.site)
        self.queryset = ComplianceReport.objects.all()
        self.request = HttpRequest()
        self.request.META = {
            "HTTP_HOST": "testserver",
        }

    def test_export_as_csv(self):
        response = self.model_admin.export_as_csv(self.request, self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(io.StringIO(content))
        rows = list(csv_reader)

        assert len(rows) == 2

        self.assertEqual(
            rows[0],
            [
                "Link to Article",
                "DOI",
                "Journal",
                "Check License",
                "Check File Formats",
                "Check Arxiv Category",
                "Check Article Type",
                "Check DOI Registration",
                "Check Author Affiliations",
                "Check Funded by SCOAP3",
                "Compliant",
            ],
        )
        self.assertEqual(
            rows[1],
            [
                "http://testserver/records/10.1000/000000",
                "10.1000/000000",
                "Physical Review D",
                "False",
                "False",
                "False",
                "False",
                "",
                "False",
                "False",
                "False",
            ],
        )
