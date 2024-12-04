import logging
from collections import Counter
from datetime import datetime

from django.db import connection
from django.db.models import Max

from scoap3.articles.documents import ArticleDocument
from scoap3.articles.models import Article
from scoap3.articles.util import (
    get_arxiv_primary_category,
    get_first_arxiv,
    get_first_doi,
)

logger = logging.getLogger(__name__)


def affiliation_export(search_year, search_country):
    result_headers = [
        "year",
        "journal",
        "doi",
        "arxiv number",
        "primary arxiv category",
        "country",
        "affiliation",
        "authors with affiliation",
        "total number of authors",
    ]
    result_data = []

    search = ArticleDocument.search()

    if search_year:
        search = search.filter("match", publication_date=f"{search_year}-01-01||/y")

    if search_country:
        search = search.filter("term", countries=search_country)

    for article in search.scan():
        year = article.publication_date.year
        journal = article.publication_info[0].journal_title
        doi = get_first_doi(article)
        arxiv = get_first_arxiv(article)
        arxiv_category = get_arxiv_primary_category(article)
        authors = article.authors
        total_authors = len(authors)
        missing_author_affiliations = 0

        extracted_affiliations = Counter()
        for author in authors:
            # if there are no affiliations, we cannot add this author
            # (this also means the record is not valid according to the schema)
            if not author.affiliations:
                missing_author_affiliations += 1
                continue

            # aggregate affiliations
            for aff in author.affiliations:
                aff_country = aff.get("country", "UNKNOWN")
                if search_country in (None, "") or aff_country.code == search_country:
                    value = ((aff.value, aff_country.code),)
                    extracted_affiliations.update(value)

        if not extracted_affiliations:
            logger.warn(f"Article with DOI: {doi} had no extracted affiliations")

        if missing_author_affiliations:
            logger.warn(
                "Article with DOI: {} had missing affiliations in {} / {} authors".format(
                    doi, missing_author_affiliations, total_authors
                )
            )

        # add extracted information to result list
        for meta, count in extracted_affiliations.items():
            aff_value, aff_country = meta
            result_data.append(
                [
                    year,
                    journal,
                    doi,
                    arxiv,
                    arxiv_category,
                    aff_country,
                    aff_value,
                    count,
                    total_authors,
                ]
            )
    return {"header": result_headers, "data": result_data}


def author_export(search_year, search_country):
    result_headers = [
        "year",
        "journal",
        "doi",
        "arxiv number",
        "primary arxiv category",
        "author",
        "country",
        "affiliation",
        "total number of authors",
    ]
    result_data = []

    search = ArticleDocument.search()

    if search_year:
        search = search.filter("match", publication_date=f"{search_year}-01-01||/y")

    if search_country:
        search = search.filter("term", countries=search_country)

    for article in search.scan():
        year = article.publication_date.year
        journal = article.publication_info[0].journal_title
        doi = get_first_doi(article)
        arxiv = get_first_arxiv(article)
        arxiv_category = get_arxiv_primary_category(article)
        authors = article.authors
        total_authors = len(authors)
        missing_author_affiliations = 0

        for author in authors:
            # if there are no affiliations, we cannot add this author
            # (this also means the record is not valid according to the schema)
            if not author.affiliations:
                missing_author_affiliations += 1
                continue

            author_first_name = author.get("first_name", "UNKNOWN")
            author_last_name = author.get("last_name", "UNKNOWN")
            # add extracted information to result list
            for affiliation in author.affiliations:
                if not affiliation.country:
                    aff_country = "UNKNOWN"
                else:
                    aff_country = affiliation.country.code
                aff_value = affiliation.get("value", "UNKNOWN")
                result_data.append(
                    [
                        year,
                        journal,
                        doi,
                        arxiv,
                        arxiv_category,
                        author_first_name + " " + author_last_name,
                        aff_country,
                        aff_value,
                        total_authors,
                    ]
                )

        if missing_author_affiliations:
            logger.warn(
                "Article with DOI: {} had missing affiliations in {} / {} authors".format(
                    doi, missing_author_affiliations, total_authors
                )
            )
    return {"header": result_headers, "data": result_data}


def year_export(start_date=None, end_date=None):
    result_headers = [
        "year",
        "journal",
        "doi",
        "arxiv number",
        "primary arxiv category",
        "total number of authors",
        "total number of ORCIDs linked to the authors",
        "total number of affiliations",
        "total number of ROR linked with the affiliations",
        "total number of related materials, type dataset",
        "total number of related materials, type software",
    ]
    result_data = []

    search = ArticleDocument.search()

    if start_date or end_date:
        date_range = {}
        if start_date:
            date_range["gte"] = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            date_range["lte"] = datetime.strptime(end_date, "%Y-%m-%d")

        search = search.filter("range", publication_date=date_range)

    for article in search.scan():
        year = article.publication_date.year
        journal = article.publication_info[0].journal_title
        doi = get_first_doi(article)
        arxiv = get_first_arxiv(article)
        arxiv_category = get_arxiv_primary_category(article)

        article_data = article.to_dict()
        authors = article_data.get("authors", [])
        total_authors = len(authors)

        total_orcid = sum(1 for author in authors if author.get("orcid"))

        total_affiliations = 0
        total_ror = 0
        for author in authors:
            affiliations = author.get("affiliations", [])
            total_affiliations += len(affiliations)

            for affiliation in affiliations:
                if affiliation.get("ror"):
                    total_ror += 1

        total_related_materials_dataset = 0
        total_related_materials_software = 0
        for related_material in article.related_materials:
            if related_material.related_material_type == "dataset":
                total_related_materials_dataset += 1
            elif related_material.related_material_type == "software":
                total_related_materials_software += 1

        result_data.append(
            [
                year,
                journal,
                doi,
                arxiv,
                arxiv_category,
                total_authors,
                total_orcid,
                total_affiliations,
                total_ror,
                total_related_materials_dataset,
                total_related_materials_software,
            ]
        )

    return {"header": result_headers, "data": result_data}


def update_article_db_model_sequence(new_start_sequence):
    max_id = Article.objects.aggregate(max_id=Max("id"))["max_id"] or 0
    if new_start_sequence <= max_id:
        print(
            f"New sequence start ({new_start_sequence}) must be higher than current max ID ({max_id})."
        )
        return False

    app_label = Article._meta.app_label
    model_name = Article._meta.model_name

    with connection.cursor() as cursor:
        command = f"ALTER SEQUENCE {app_label}_{model_name}_id_seq RESTART WITH {new_start_sequence};"
        cursor.execute(command)
    print(
        f"Sequence for {app_label}_{model_name} updated to start with {new_start_sequence}."
    )
    return True
