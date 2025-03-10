import datetime
import mimetypes
import os
from datetime import date

from django.db import models
from django.db.models.fields.files import FieldFile
from django_lifecycle import AFTER_CREATE, AFTER_UPDATE, LifecycleModelMixin, hook
from simple_history.models import HistoricalRecords


class ArticleIdentifierType(models.TextChoices):
    DOI = ("DOI",)
    ARXIV = ("arXiv",)


def article_file_upload_path(instance, filename):
    return f"files/{instance.article_id.id}/{filename}"


class CustomFieldFile(FieldFile):
    @property
    def size(self):
        if self.storage.exists(self.name):
            return super().size
        else:
            return "-"

    @property
    def type(self):
        mime_type, _ = mimetypes.guess_type(self.path)

        if mime_type:
            return mime_type.split("/")[-1]
        return "-"


class CustomFileField(models.FileField):
    attr_class = CustomFieldFile


class Article(LifecycleModelMixin, models.Model):
    reception_date = models.DateField(blank=True, null=True)
    acceptance_date = models.DateField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    first_online_date = models.DateField(blank=True, null=True)
    title = models.TextField()
    subtitle = models.TextField(blank=True, default="")
    abstract = models.TextField(blank=True, default="")
    related_licenses = models.ManyToManyField(
        "misc.License",
        related_name="related_licenses",
    )
    related_materials = models.ManyToManyField(
        "misc.RelatedMaterial", related_name="related_articles", blank=True
    )
    _created_at = models.DateTimeField(auto_now_add=True)
    _updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["id"]

    @hook(AFTER_UPDATE, on_commit=True)
    @hook(AFTER_CREATE, on_commit=True)
    def on_save(self):
        from scoap3.articles.tasks import compliance_checks

        if os.getenv("COMPLIANCE_DISABLED", "0") == "1":
            return

        compliance_checks.delay(self.id)


class ArticleFile(models.Model):
    article_id = models.ForeignKey(
        "articles.Article", on_delete=models.CASCADE, related_name="related_files"
    )
    file = CustomFileField(upload_to=article_file_upload_path)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    filetype = models.TextField(blank=True, default="")
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.file.name


class ArticleIdentifier(models.Model):
    article_id = models.ForeignKey(
        "articles.Article", on_delete=models.CASCADE, related_name="article_identifiers"
    )
    identifier_type = models.CharField(
        max_length=255,
        choices=ArticleIdentifierType.choices,
    )
    identifier_value = models.CharField(
        max_length=255,
    )

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["article_id", "identifier_type", "identifier_value"])
        ]


class ComplianceReport(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="report"
    )
    report_date = models.DateTimeField(auto_now_add=True)

    check_license = models.BooleanField(default=False)
    check_license_description = models.TextField(blank=True, default="")
    check_required_file_formats = models.BooleanField(default=False)
    check_required_file_formats_description = models.TextField(blank=True, default="")
    check_arxiv_category = models.BooleanField(default=False)
    check_arxiv_category_description = models.TextField(blank=True, default="")
    check_article_type = models.BooleanField(default=False)
    check_article_type_description = models.TextField(blank=True, default="")
    check_doi_registration_time = models.BooleanField(default=False)
    check_doi_registration_time_description = models.TextField(blank=True, default="")
    check_authors_affiliation = models.BooleanField(default=False)
    check_authors_affiliation_description = models.TextField(blank=True, default="")
    check_contains_funded_by_scoap3 = models.BooleanField(default=False)
    check_contains_funded_by_scoap3_description = models.TextField(
        blank=True, default=""
    )
    compliant = models.BooleanField(default=False)

    def __str__(self):
        return f"Compliance Report for {self.article.title} on {self.report_date.strftime('%Y-%m-%d')}"

    def is_compliant(self):
        # If article is part of the following jouranls list, we
        # should not take into account the ARXIV category compliance
        JOURNALS_SKIP_COMPLIANCE = [
            "Physics Letters B",
            "Nuclear Physics B",
            "Journal of High Energy Physics",
            "European Physical Journal C",
        ]
        pub_info = self.article.publication_info.all()
        _check_arxiv_category = True
        if len(pub_info) and not (
            pub_info[0].journal_title in JOURNALS_SKIP_COMPLIANCE
        ):
            _check_arxiv_category = self.check_arxiv_category

        if isinstance(
            self.article.publication_date, datetime.date
        ) and self.article.publication_date < date(2023, 1, 1):
            return True

        return all(
            [
                self.check_license,
                self.check_required_file_formats,
                _check_arxiv_category,
                self.check_article_type,
                self.check_doi_registration_time,
            ]
        )
