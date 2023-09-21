import logging
from collections import Counter

from opensearchpy import Q

from scoap3.articles.documents import ArticleDocument
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
        search = search.filter(
            "nested",
            path="authors.affiliations.country",
            query=Q("match", authors__affiliations__country__code=search_country),
        )

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
        search = search.filter(
            "nested",
            path="authors.affiliations.country",
            query=Q("match", authors__affiliations__country__code=search_country),
        )

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
