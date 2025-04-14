import logging
import os
from datetime import datetime

from celery import shared_task
from django.core.paginator import Paginator
from django_opensearch_dsl.registries import registry

from scoap3.articles.models import Article, ArticleFile, ComplianceReport
from scoap3.articles.util import is_string_in_pdf
from scoap3.authors.models import Author
from scoap3.misc.models import Affiliation, PublicationInfo
from scoap3.misc.utils import fetch_doi_registration_date

logger = logging.getLogger(__name__)


def check_license(obj):
    compliant_licenses = ["CC-BY-4.0", "CC-BY-3.0"]
    article_licenses = [license.name for license in obj.related_licenses.all()]

    if any(license in compliant_licenses for license in article_licenses):
        return True, "License check passed."
    else:
        return (
            False,
            f"Non-compliant licenses: {', '.join(article_licenses)}. Required: {', '.join(compliant_licenses)}.",
        )


def check_required_file_formats(obj):
    publication_info = PublicationInfo.objects.filter(article_id=obj).first()

    if not publication_info:
        return False, "No publication information found."

    journal_format_mapping = {
        "Acta Physica Polonica B": ["pdf", "pdf/a"],
        "Advances in High Energy Physics": ["pdf", "pdf/a", "xml"],
        "Progress of Theoretical and Experimental Physics": ["pdf", "pdf/a", "xml"],
        "European Physical Journal C": ["pdf/a", "xml"],
        "Journal of High Energy Physics": ["pdf/a", "xml"],
        "Nuclear Physics B": ["pdf", "pdf/a", "xml"],
        "Physics Letters B": ["pdf", "pdf/a", "xml"],
        "Physical Review Letters": ["pdf", "xml"],
        "Physical Review C": ["pdf", "xml"],
        "Physical Review D": ["pdf", "xml"],
        "Chinese Physics C": ["pdf", "xml"],
    }

    default_required_formats = ["pdf", "pdf/a", "xml"]

    required_formats = journal_format_mapping.get(
        publication_info.journal_title, default_required_formats
    )

    available_formats = []
    for file in obj.related_files.all():
        available_formats.append(file.filetype)

    missing_formats = [f for f in required_formats if f not in available_formats]

    if missing_formats:
        return False, f"Missing required file formats: {', '.join(missing_formats)}."
    return True, "All required file formats are present."


def check_article_type(obj):
    non_compliant_types = [
        "Erratum",
        "Addendum",
        "Corrigendum",
        "Editorial",
        "Obituaries",
    ]
    for type in non_compliant_types:
        if type.lower() in obj.title.lower():
            return (
                False,
                f"Article is of non-compliant type: {type}.",
            )
    return True, "Article type is compliant."


def check_arxiv_category(obj):
    partial_journals = [
        "Chinese Physics C",
        "Progress of Theoretical and Experimental Physics",
        "Advances in High Energy Physics",
        "Physical Review C",
        "Physical Review D",
        "Physical Review Letters",
        "Acta Physica Polonica B",
    ]
    journal_title = (
        obj.publication_info.first().journal_title
        if obj.publication_info.exists()
        else None
    )

    if journal_title in partial_journals:
        categories = obj.article_arxiv_category.all()
        if any(cat.primary and cat.category.startswith("hep") for cat in categories):
            return True, "ArXiv category is compliant for partial journal."
        return False, "Primary ArXiv category is not compliant for partial journal."
    return True, "ArXiv category compliance not applicable."


def check_doi_registration_time(obj):
    doi_identifier = obj.article_identifiers.filter(identifier_type="DOI").first()
    if doi_identifier:
        doi_registration_date = fetch_doi_registration_date(
            doi_identifier.identifier_value
        )
        if doi_registration_date and obj._created_at:
            doi_registration_date = datetime.strptime(
                doi_registration_date, "%Y-%m-%d"
            ).date()
            hours_difference = (obj._created_at.date() - doi_registration_date).days
            if hours_difference > 1:
                logger.info(
                    "Article %s: DOI:%s registration date is more that 24 hours.",
                    obj.id,
                    doi_identifier.identifier_value,
                )
                return (
                    False,
                    f"DOI registration time exceeded 24 hours. {hours_difference} passed.",
                )
            else:
                logger.info(
                    "Article %s: DOI:%s is created within 24 hours.",
                    obj.id,
                    doi_identifier.identifier_value,
                )
                return (
                    True,
                    f"DOI registration time is within acceptable range. {hours_difference} passed.",
                )
        else:
            logger.warning(
                "Article %s: DOI (%s) registration date not found.",
                obj.id,
                doi_identifier.identifier_value,
            )
            return False, "DOI registration date not found."
    logger.warning("Article %s: DOI not found in our system.", obj.id)
    return False, "DOI not found in our system."


def check_authors_affiliation(article):
    authors = Author.objects.filter(article_id=article)
    for author in authors:
        affiliations = Affiliation.objects.filter(author_id=author)
        if len(affiliations) < 1:
            return False, "Author does not have affiliations"
    return True, "Authors' affiliations are compliant"


def check_contains_funded_by_scoap3(article):
    try:
        article_files = ArticleFile.objects.filter(article_id=article)

        if not article_files.exists():
            return False, "No files found for the given article."

        for article_file in article_files:
            if article_file.filetype in ["pdf", "pdf/a"]:
                try:
                    if is_string_in_pdf(article_file, "Funded by SCOAP"):
                        return (
                            True,
                            f"Files contain the required text: 'Funded by SCOAP3'. File: {article_file.file.url}",
                        )
                except FileNotFoundError:
                    return False, f"File not found: {article_file.file.url}"

        return False, "Files do not contain the required text: 'Funded by SCOAP3'"
    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}"


@shared_task(name="compliance_checks", acks_late=True)
def compliance_checks(article_id):
    if os.getenv("COMPLIANCE_DISABLED", "0") == "1":
        return f"compliance disabled:: article {str(article_id)}"

    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        logger.error("Article %s not found.", article_id)
        return "Article not found"

    (
        check_doi_registration_compliance,
        check_doi_registration_description,
    ) = check_doi_registration_time(article)
    check_article_type_compliance, check_article_type_description = check_article_type(
        article
    )
    (
        check_arxiv_category_compliance,
        check_arxiv_category_description,
    ) = check_arxiv_category(article)
    (
        check_required_file_formats_compliance,
        check_required_file_formats_description,
    ) = check_required_file_formats(article)
    check_license_compliance, check_license_description = check_license(article)
    (
        check_affiliations_compliance,
        check_affiliations_description,
    ) = check_authors_affiliation(article)
    (
        check_funded_by_scoap3_compliance,
        check_funded_by_scoap3_description,
    ) = check_contains_funded_by_scoap3(article)

    article.report.all().delete()

    report = ComplianceReport.objects.create(
        article=article,
        check_article_type=check_article_type_compliance,
        check_article_type_description=check_article_type_description,
        check_arxiv_category=check_arxiv_category_compliance,
        check_arxiv_category_description=check_arxiv_category_description,
        check_doi_registration_time=check_doi_registration_compliance,
        check_doi_registration_time_description=check_doi_registration_description,
        check_required_file_formats=check_required_file_formats_compliance,
        check_required_file_formats_description=check_required_file_formats_description,
        check_license=check_license_compliance,
        check_license_description=check_license_description,
        check_authors_affiliation=check_affiliations_compliance,
        check_authors_affiliation_description=check_affiliations_description,
        check_contains_funded_by_scoap3=check_funded_by_scoap3_compliance,
        check_contains_funded_by_scoap3_description=check_funded_by_scoap3_description,
    )
    report.compliant = report.is_compliant()
    report.save()
    logger.info("Compliance checks completed for article %s", article_id)
    return f"Compliance checks completed for article {article_id}"


@shared_task
def index_article_batch(article_ids):
    articles = Article.objects.filter(id__in=article_ids)
    for article in articles:
        registry.update(article)


def index_all_articles(batch_size=100):
    all_articles = Article.objects.all().values_list("id", flat=True)
    paginator = Paginator(all_articles, batch_size)

    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        index_article_batch.delay(list(page.object_list))
