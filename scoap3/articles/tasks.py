import logging
from datetime import datetime

from celery import shared_task

from scoap3.articles.models import Article, ComplianceReport
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


def check_file_formats(obj):
    required_formats = ["pdf", "pdf_a", "xml"]
    available_formats = [
        file.file.name.split(".")[-1] for file in obj.related_files.all()
    ]

    missing_formats = [f for f in required_formats if f not in available_formats]

    if missing_formats:
        return (
            False,
            f"Missing required file formats: {', '.join(missing_formats)}.",
        )
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
    partial_journals = ["CPC", "PTEP", "AHEP", "PRC", "PRL", "APPB"]
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


@shared_task(name="compliance_checks", acks_late=True)
def compliance_checks(article_id):
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
    check_file_formats_compliance, check_file_formats_description = check_file_formats(
        article
    )
    check_license_compliance, check_license_description = check_license(article)

    article.report.all().delete()

    report = ComplianceReport.objects.create(
        article=article,
        check_article_type=check_article_type_compliance,
        check_article_type_description=check_article_type_description,
        check_arxiv_category=check_arxiv_category_compliance,
        check_arxiv_category_description=check_arxiv_category_description,
        check_doi_registration_time=check_doi_registration_compliance,
        check_doi_registration_time_description=check_doi_registration_description,
        check_file_formats=check_file_formats_compliance,
        check_file_formats_description=check_file_formats_description,
        check_license=check_license_compliance,
        check_license_description=check_license_description,
    )
    report.save()
    logger.info("Compliance checks completed for article %s", article_id)
    return f"Compliance checks completed for article {article_id}"
