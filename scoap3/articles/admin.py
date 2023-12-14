from django.contrib import admin, messages

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
        "check_license",
        "check_file_formats",
        "check_arxiv_category",
        "check_article_type",
        "check_doi_registration_time",
        "get_is_compliant",
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
        "get_is_compliant",
        "check_license",
        "check_license_description",
        "check_file_formats",
        "check_file_formats_description",
        "check_arxiv_category",
        "check_arxiv_category_description",
        "check_article_type",
        "check_article_type_description",
        "check_doi_registration_time",
        "check_doi_registration_time_description",
    ]
    readonly_fields = [
        "article",
        "report_date",
        "get_is_compliant",
        "check_license",
        "check_license_description",
        "check_file_formats",
        "check_file_formats_description",
        "check_arxiv_category",
        "check_arxiv_category_description",
        "check_article_type",
        "check_article_type_description",
        "check_doi_registration_time",
        "check_doi_registration_time_description",
    ]

    @admin.display(description="ID")
    def article_id(self, obj):
        return obj.article.id

    @admin.display(boolean=True, description="Compliant")
    def get_is_compliant(self, obj):
        return obj.is_compliant()

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


class ArticleComplianceReportInline(admin.StackedInline):
    model = ComplianceReport
    readonly_fields = [
        "check_license",
        "check_license_description",
        "check_file_formats",
        "check_file_formats_description",
        "check_arxiv_category",
        "check_arxiv_category_description",
        "check_article_type",
        "check_article_type_description",
        "check_doi_registration_time",
        "check_doi_registration_time_description",
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
                    ("check_file_formats", "check_file_formats_description"),
                    ("check_arxiv_category", "check_arxiv_category_description"),
                    ("check_article_type", "check_article_type_description"),
                    (
                        "check_doi_registration_time",
                        "check_doi_registration_time_description",
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
            [affiliation.country.name for affiliation in obj.affiliation_set.all()]
        )

    @admin.display(description="Affiliations")
    def get_affiliations(self, obj):
        return ", ".join(
            [affiliation.value for affiliation in obj.affiliation_set.all()]
        )

    @admin.display(description="Identifiers")
    def get_identifiers(self, obj):
        return ", ".join(
            [
                f"{_id.identifier_type}: {_id.identifier_value}"
                for _id in obj.identifiers.all()
            ]
        )


class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "journal_title",
        "doi",
        "check_license",
        "check_file_formats",
        "check_arxiv_category",
        "check_article_type",
        "check_doi_registration_time",
        "_updated_at",
        "_created_at",
    ]
    search_fields = [
        "title",
        "id",
        "publication_info__journal_title",
        "article_identifiers__identifier_value",
    ]
    actions = ["make_compliance_check"]
    list_filter = [
        "_updated_at",
        "_created_at",
        "publication_info__journal_title",
        "report__check_license",
        "report__check_file_formats",
        "report__check_arxiv_category",
        "report__check_article_type",
        "report__check_doi_registration_time",
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

    @admin.action(description="Run compliance checks")
    def make_compliance_check(self, request, queryset):
        ids = []
        for obj in queryset:
            compliance_checks.delay(obj.id)
            ids.append(str(obj.id))
        messages.success(
            request,
            f"""
            Selected articles are being processed, it might take some time before seeing
            the results in the reports. {', '.join(ids)}.
            """,
        )

    @admin.display(boolean=True, description="License")
    def check_license(self, obj):
        report = obj.report.first()
        if report:
            return report.check_license
        return False

    @admin.display(description="File formats", boolean=True)
    def check_file_formats(self, obj):
        report = obj.report.first()
        if report:
            return report.check_file_formats
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


class ArticleIdentifierAdmin(admin.ModelAdmin):
    list_display = ["article_id", "identifier_type", "identifier_value"]
    search_fields = ["article_id"]
    raw_id_fields = ["article_id"]


class ArticleFileAdmin(admin.ModelAdmin):
    list_display = ["id", "article_id", "file", "file_size", "updated", "created"]
    search_fields = ["article_id"]

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
