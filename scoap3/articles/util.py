import csv
import datetime

from django.http import HttpResponse

from scoap3.articles.models import ArticleIdentifierType


def get_first_doi(article_document):
    for identifier in article_document.article_identifiers:
        if identifier.identifier_type == ArticleIdentifierType.DOI.value:
            return identifier.identifier_value
    return None


def get_first_arxiv(article_document):
    for identifier in article_document.article_identifiers:
        if identifier.identifier_type == ArticleIdentifierType.ARXIV.value:
            return identifier.identifier_value
    return None


def get_arxiv_primary_category(article_document):
    for arxiv_category in article_document.article_arxiv_category:
        if arxiv_category.primary:
            return arxiv_category.category


def generate_compliance_csv(queryset, host):
    filename = f"article_compliance_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    field_names_mapping = {
        "DOI": "article_doi",
        "Journal": "article_journal",
        "Check License": "check_license",
        "Check File Formats": "check_file_formats",
        "Check Arxiv Category": "check_arxiv_category",
        "Check Article Type": "check_article_type",
        "Check DOI Registration": "check_doi_registration_time_description",
    }

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={filename}"
    writer = csv.writer(response)
    field_names = list(field_names_mapping.keys())
    rows_titles = ["Link to Article"] + field_names
    writer.writerow(rows_titles)

    for obj in queryset:
        article_doi = (
            obj.article.article_identifiers.filter(identifier_type="DOI")
            .first()
            .identifier_value
            if obj.article.article_identifiers.filter(identifier_type="DOI").exists()
            else "None"
        )
        article_journal = (
            obj.article.publication_info.all()[0].journal_title
            if obj.article.publication_info.exists()
            else "None"
        )
        values = [
            getattr(obj, field_names_mapping.get(field, field), None)
            for field in field_names
        ]
        values = [value for value in values if value is not None]
        row = [
            f"{host}records/{article_doi}",
            article_doi,
            article_journal,
        ] + values
        writer.writerow(row)

    return response
