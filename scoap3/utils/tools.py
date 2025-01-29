import logging
import xml.etree.ElementTree as ET
from collections import Counter

from django.db import connection
from django.db.models import Max

from scoap3.articles.documents import ArticleDocument
from scoap3.articles.models import Article, ArticleFile
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


# article: ArticleDocument
# publisher: string
# example usage:
# > authors, affiliations = parse_article_xml(article_doc, publisher)
def parse_article_xml(article, publisher):
    files = article.related_files
    xml_files = [f for f in files if f.file.endswith(".xml")]

    for file in xml_files:
        url = file.file
        file_obj = ArticleFile.objects.filter(
            file__contains=url.split("ch/media/")[-1]
        )[0]
        parsed_authors, parsed_affiliations = parse_xml_from_s3(file_obj, publisher)

    return parsed_authors, parsed_affiliations


def parse_xml_from_s3(file_path, publisher):
    with file_path.file.open() as file:
        xml_content = file.read()
        xml_content = xml_content.decode("utf8")

    root = ET.fromstring(xml_content)

    if publisher in ["APS", "Hindawi"]:
        authors, affiliation_map = parse_aps_hindawi_xml(root)

    elif publisher == "Springer":
        authors, affiliation_map = parse_springer_xml(root)

    return authors, affiliation_map


def parse_aps_hindawi_xml(root):
    authors_data = []
    affiliations_list = []
    affiliations = {}

    for aff_element in root.findall(".//aff"):
        aff_id = aff_element.get("id")
        institution = (
            aff_element.find("institution-wrap/institution").text
            if aff_element.find("institution-wrap/institution") is not None
            else None
        )
        ror = (
            aff_element.find(
                "institution-wrap/institution-id[@institution-id-type='ror']"
            ).text
            if aff_element.find(
                "institution-wrap/institution-id[@institution-id-type='ror']"
            )
            is not None
            else None
        )

        affiliations[aff_id] = {"name": institution, "ror": ror}
        affiliations_list.append({"id": aff_id, "name": institution, "ror": ror})

    for author in root.findall(".//contrib-group/contrib[@contrib-type='author']"):
        author_info = {
            "given_name": f"{author.find('./name/given-names').text}",
            "family_name": f"{author.find('./name/surname').text}",
            "orcid": author.find("./contrib-id[@contrib-id-type='orcid']").text
            if author.find("./contrib-id[@contrib-id-type='orcid']") is not None
            else None,
            "affiliations": [],
        }
        for aff_ref in author.findall("xref[@ref-type='aff']"):
            aff_id = aff_ref.get("rid")
            if aff_id in affiliations:
                author_info["affiliations"].append(affiliations[aff_id])

        authors_data.append(author_info)

    return authors_data, affiliations_list


def parse_springer_xml(root):
    affiliation_map = {}
    affiliations_list = []
    for affiliation in root.findall(".//Affiliation"):
        aff_id = affiliation.get("ID")
        institution_name = affiliation.findtext("OrgName")
        ror_id = affiliation.findtext("OrgID[@Type='ROR']")

        if aff_id:
            affiliation_map[aff_id] = {
                "InstitutionName": institution_name,
                "ror": ror_id,
            }
            affiliations_list.append(
                {"id": aff_id, "name": institution_name, "ror": ror_id}
            )

    authors = []
    for author in root.findall(".//AuthorGroup/Author"):
        given_name = author.findtext("AuthorName/GivenName")
        family_name = author.findtext("AuthorName/FamilyName")
        orcid = author.get("ORCID")
        affiliation_ids = author.get("AffiliationIDS", "").split()

        author_data = {
            "given_name": f"{given_name}",
            "family_name": f"{family_name}",
            "orcid": orcid,
            "Affiliations": [
                affiliation_map.get(aff_id, {}) for aff_id in affiliation_ids
            ],
        }

        authors.append(author_data)

    return authors, affiliation_map
