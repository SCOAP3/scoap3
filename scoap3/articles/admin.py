import csv
import datetime

from django.contrib import admin, messages
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from more_admin_filters import MultiSelectRelatedFilter
from rangefilter.filters import DateRangeQuickSelectListFilterBuilder

from scoap3.articles.models import (
    Article,
    ArticleFile,
    ArticleIdentifier,
    ComplianceReport,
)
from scoap3.articles.tasks import compliance_checks
from scoap3.authors.models import Author


class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = [
        "article_id",
        "article_publisher",
        "article_journal",
        "article_doi",
        "compliant",
        "check_license",
        "check_required_file_formats",
        "check_arxiv_category",
        "check_article_type",
        "check_doi_registration_time",
        "check_authors_affiliation",
        "check_contains_funded_by_scoap3",
        "report_date",
    ]
    search_fields = [
        "id",
        "article__id",
        "article__title",
        "article__publication_info__journal_title",
    ]
    fields = [
        "article",
        "report_date",
        "compliant",
        "check_license",
        "check_license_description",
        "check_required_file_formats",
        "check_required_file_formats_description",
        "check_arxiv_category",
        "check_arxiv_category_description",
        "check_article_type",
        "check_article_type_description",
        "check_doi_registration_time",
        "check_doi_registration_time_description",
        "check_authors_affiliation",
        "check_authors_affiliation_description",
        "check_contains_funded_by_scoap3",
        "check_contains_funded_by_scoap3_description",
    ]
    readonly_fields = [
        "article",
        "report_date",
        "compliant",
        "check_license",
        "check_license_description",
        "check_arxiv_category",
        "check_arxiv_category_description",
        "check_article_type",
        "check_article_type_description",
        "check_doi_registration_time",
        "check_doi_registration_time_description",
        "check_authors_affiliation",
        "check_authors_affiliation_description",
        "check_contains_funded_by_scoap3",
        "check_contains_funded_by_scoap3_description",
    ]

    list_filter = [
        ("report_date", DateRangeQuickSelectListFilterBuilder()),
        "article_id__publication_info__publisher",
        "article_id___updated_at",
        "article_id___created_at",
        "article_id__publication_info__journal_title",
        "article_id__publication_date",
        "article_id__report__check_license",
        "article_id__report__check_required_file_formats",
        "article_id__report__check_arxiv_category",
        "article_id__report__check_article_type",
        "article_id__report__check_doi_registration_time",
        "article_id__report__check_authors_affiliation",
        "article_id__report__check_contains_funded_by_scoap3",
    ]

    actions = ["export_as_csv"]

    @admin.display(description="ID")
    def article_id(self, obj):
        return obj.article.id

    @admin.display(description="DOI")
    def article_doi(self, obj):
        doi_identifier = obj.article.article_identifiers.filter(
            identifier_type="DOI"
        ).first()
        return [doi_identifier.identifier_value if doi_identifier else "None"]

    @admin.display(description="Publisher")
    def article_publisher(self, obj):
        return [info.publisher for info in obj.article.publication_info.all()]

    @admin.display(description="Journal")
    def article_journal(self, obj):
        return [info.journal_title for info in obj.article.publication_info.all()]

    @admin.action(description="Export as CSV")
    def export_as_csv(self, request, queryset):
        filename = f"article_compliance_{datetime.datetime.now()}.csv"
        base_url = f"{request.scheme}://{request.get_host()}/records"  # noqa
        field_names_mapping = {
            "DOI": "article_doi",
            "Journal": "article_journal",
            "Check License": "check_license",
            "Check File Formats": "check_required_file_formats",
            "Check Arxiv Category": "check_arxiv_category",
            "Check Article Type": "check_article_type",
            "Check DOI Registration": "check_doi_registration_time_description",
            "Check Author Affiliations": "check_authors_affiliation",
            "Check Funded by SCOAP3": "check_contains_funded_by_scoap3",
            "Compliant": "compliant",
        }

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={filename}"  # noqa
        writer = csv.writer(response)
        field_names = list(field_names_mapping.keys())
        rows_titles = ["Link to Article"] + field_names
        writer.writerow(rows_titles)

        for obj in queryset:
            article_doi = self.article_doi(obj)
            article_journal = self.article_journal(obj)
            values = [
                getattr(obj, field_names_mapping.get(field, field), None)
                for field in field_names
            ]
            values = [value for value in values if value is not None]
            row = [
                f"{base_url}/{article_doi[0]}",
                article_doi[0],
                article_journal[0],
            ] + values
            writer.writerow(row)
        return response


class ArticleComplianceReportInline(admin.StackedInline):
    model = ComplianceReport
    readonly_fields = [
        "check_license",
        "check_license_description",
        "check_required_file_formats",
        "check_required_file_formats_description",
        "check_arxiv_category",
        "check_arxiv_category_description",
        "check_article_type",
        "check_article_type_description",
        "check_doi_registration_time",
        "check_doi_registration_time_description",
        "check_authors_affiliation",
        "check_authors_affiliation_description",
        "check_contains_funded_by_scoap3",
        "check_contains_funded_by_scoap3_description",
    ]
    can_delete = False
    can_create = False
    extra = 0
    max_num = 1
    fieldsets = (
        (
            None,
            {
                "fields": [
                    ("check_license", "check_license_description"),
                    (
                        "check_required_file_formats",
                        "check_required_file_formats_description",
                    ),
                    ("check_arxiv_category", "check_arxiv_category_description"),
                    ("check_article_type", "check_article_type_description"),
                    (
                        "check_doi_registration_time",
                        "check_doi_registration_time_description",
                    ),
                    (
                        "check_authors_affiliation",
                        "check_authors_affiliation_description",
                    ),
                    (
                        "check_contains_funded_by_scoap3",
                        "check_contains_funded_by_scoap3_description",
                    ),
                ]
            },
        ),
    )


class ArticleAuthorsInline(admin.StackedInline):
    model = Author
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = [
        "first_name",
        "last_name",
        "email",
        "get_countries",
        "get_affiliations",
        "get_identifiers",
    ]
    fields = readonly_fields

    @admin.display(description="Countries")
    def get_countries(self, obj):
        return ", ".join(
            [affiliation.country.name for affiliation in obj.affiliations.all()]
        )

    @admin.display(description="Affiliations")
    def get_affiliations(self, obj):
        return ", ".join([affiliation.value for affiliation in obj.affiliations.all()])

    @admin.display(description="Identifiers")
    def get_identifiers(self, obj):
        return ", ".join(
            [
                f"{_id.identifier_type}: {_id.identifier_value}"
                for _id in obj.identifiers.all()
            ]
        )


def make_compliant(article_queryset):
    article_ids = article_queryset.values_list("id", flat=True)

    reports = ComplianceReport.objects.filter(article_id__in=article_ids)
    reports.update(compliant=True)

    ids = map(str, reports.values_list("article_id", flat=True))
    return ids


class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "preview_link",
        "title",
        "journal_title",
        "publisher",
        "doi",
        "check_compliance",
        "check_license",
        "check_required_file_formats",
        "check_arxiv_category",
        "check_article_type",
        "check_doi_registration_time",
        "check_authors_affiliation",
        "_updated_at",
        "_created_at",
    ]
    search_fields = [
        "title",
        "id",
        "publication_info__journal_title",
        "article_identifiers__identifier_value",
    ]
    actions = ["make_compliance_check", "mark_as_compliant"]
    list_filter = [
        "report__compliant",
        ("_updated_at", DateRangeQuickSelectListFilterBuilder()),
        ("_created_at", DateRangeQuickSelectListFilterBuilder()),
        ("publication_date", DateRangeQuickSelectListFilterBuilder()),
        ("publication_info__publisher", MultiSelectRelatedFilter),
        "publication_info__journal_title",
        "report__check_license",
        "report__check_required_file_formats",
        "report__check_arxiv_category",
        "report__check_article_type",
        "report__check_doi_registration_time",
        "report__check_authors_affiliation",
    ]
    readonly_fields = [
        "_created_at",
        "_updated_at",
    ]
    inlines = [ArticleAuthorsInline, ArticleComplianceReportInline]

    @admin.display(description="Journal")
    def journal_title(self, obj):
        return [info.journal_title for info in obj.publication_info.all()]

    @admin.display(description="DOI")
    def doi(self, obj):
        return [
            identifier.identifier_value
            for identifier in obj.article_identifiers.filter(identifier_type="DOI")
        ]

    @admin.display(description="Publisher")
    def publisher(self, obj):
        return [info.publisher for info in obj.publication_info.all()]

    @admin.display(description="Link")
    def preview_link(self, obj):
        url = reverse("api:article-detail", args=[obj.id])
        web_url = url.replace("/api/articles", "/records")
        return format_html(
            '<a href="{}" target="_blank">JSON</a>|<a href="{}" target="_blank">Web</a>',
            url,
            web_url,
        )

    @admin.action(description="Run compliance checks")
    def make_compliance_check(self, request, queryset):
        ids = []
        for obj in queryset:
            compliance_checks.apply_async(args=[obj.id, True], priority=9)
            ids.append(str(obj.id))
        messages.success(
            request,
            f"""
            Selected articles are being processed, it might take some time before seeing
            the results in the reports. {', '.join(ids)}.
            """,
        )

    @admin.action(description="Mark as compliant")
    def mark_as_compliant(self, request, queryset):
        ids = make_compliant(queryset)
        messages.success(
            request,
            f"""
            Selected articles are being processed, it might take some time before seeing
            the results in the reports. {', '.join(ids)}.
            """,
        )

    @admin.display(boolean=True, description="Compliant")
    def check_compliance(self, obj):
        report = obj.report.first()
        if report:
            return report.compliant
        return False

    @admin.display(boolean=True, description="License")
    def check_license(self, obj):
        report = obj.report.first()
        if report:
            return report.check_license
        return False

    @admin.display(description="File formats", boolean=True)
    def check_required_file_formats(self, obj):
        report = obj.report.first()
        if report:
            return report.check_required_file_formats
        return False

    @admin.display(description="ArXiv category", boolean=True)
    def check_arxiv_category(self, obj):
        report = obj.report.first()
        if report:
            return report.check_arxiv_category
        return False

    @admin.display(description="Article type", boolean=True)
    def check_article_type(self, obj):
        report = obj.report.first()
        if report:
            return report.check_article_type
        return False

    @admin.display(description="DOI registration time", boolean=True)
    def check_doi_registration_time(self, obj):
        report = obj.report.first()
        if report:
            return report.check_doi_registration_time
        return False

    @admin.display(description="Author affiliations", boolean=True)
    def check_authors_affiliation(self, obj):
        report = obj.report.first()
        if report:
            return report.check_authors_affiliation
        return False


class ArticleIdentifierAdmin(admin.ModelAdmin):
    list_display = ["article_id", "identifier_type", "identifier_value"]
    search_fields = ["article_id__id", "identifier_value"]
    raw_id_fields = ["article_id"]


class ArticleFileAdmin(admin.ModelAdmin):
    list_display = ["id", "article_id", "file", "file_size", "updated", "created"]
    search_fields = ["article_id__id"]

    @admin.display(description="Size (bytes)")
    def file_size(self, obj):
        try:
            file_size = obj.file.size
        except FileNotFoundError:
            file_size = "-"
        return f"{file_size}"


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleIdentifier, ArticleIdentifierAdmin)
admin.site.register(ArticleFile, ArticleFileAdmin)
admin.site.register(ComplianceReport, ComplianceReportAdmin)

# Disable Delete action from all admin sites
# This can be overriden specifically from each ModelAdmin class
admin.site.disable_action("delete_selected")
