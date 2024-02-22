import io
import json
import logging
import os
import re

import pycountry
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.files.storage import storages
from django.core.validators import URLValidator
from elasticsearch import ConnectionError, ConnectionTimeout, Elasticsearch
from sentry_sdk import capture_exception

from config import celery_app
from scoap3.articles.models import Article, ArticleFile, ArticleIdentifier
from scoap3.authors.models import Author, AuthorIdentifier
from scoap3.misc.models import (
    Affiliation,
    ArticleArxivCategory,
    Copyright,
    Country,
    ExperimentalCollaboration,
    License,
    PublicationInfo,
    Publisher,
)

logger = logging.getLogger(__name__)


def _rename_keys(data, replacements):
    for item in data:
        for old_key, new_key in replacements:
            if old_key in item:
                item[new_key] = item.pop(old_key)
    return data


def _create_licenses(data):
    licenses = []
    val = URLValidator()
    for license in _rename_keys(data, [("license", "name")]):
        try:
            val(license.get("url"))
        except ValidationError:
            if license.get("name") is None:
                license["name"] = license.get("url")
            license.pop("url")

        if (
            license["name"] == "CC-BY-4.0"
            or license["name"] == "CC-BY-4"
            or license["name"] == "Creative Commons Attribution 4.0 licence"
        ):
            license["name"] = "CC-BY-4.0"
            license["url"] = "http://creativecommons.org/licenses/by/4.0/"
        elif (
            license["name"] == "CC-BY-3.0"
            or license["name"] == "cc-by"
            or license["name"] == "Creative Commons Attribution 3.0 licence"
        ):
            license["name"] = "CC-BY-3.0"
            license["url"] = "http://creativecommons.org/licenses/by/3.0/"

        license, _ = License.objects.get_or_create(
            url=license.get("url", ""), name=license.get("name", "")
        )
        licenses.append(license)
    return licenses


def _create_article(data, licenses):
    article_data = {
        "publication_date": data["imprints"][0].get("date"),
        "title": data["titles"][0].get("title"),
        "subtitle": data["titles"][0].get("subtitle", ""),
        "abstract": data["abstracts"][0].get("value", ""),
    }
    doi = data.get("dois")[0].get("value")
    if (
        doi
        and ArticleIdentifier.objects.filter(
            identifier_type="DOI", identifier_value=doi
        ).exists()
    ):
        article = ArticleIdentifier.objects.get(
            identifier_type="DOI", identifier_value=doi
        ).article_id
        article.__dict__.update(**article_data)
    else:
        article = Article.objects.create(**article_data)
        article._created_at = data.get("_created") or data.get("record_creation_date")

    article.related_licenses.set(licenses)
    article.save()
    return article


def _create_article_file(data, article):
    for file in data.get("_files", []):
        article_id = article.id
        filename = file.get("key")
        file_path = f"files/{article_id}/{filename}"
        article = Article.objects.get(pk=article_id)
        article_file_data = {"article_id": article, "file": file_path}
        ArticleFile.objects.get_or_create(**article_file_data)


def _create_article_identifier(data, article):
    for doi in data.get("dois"):
        article_identifier_data = {
            "article_id": article,
            "identifier_type": "DOI",
            "identifier_value": doi.get("value"),
        }
        ArticleIdentifier.objects.get_or_create(**article_identifier_data)
    for arxiv in data.get("arxiv_eprints", []):
        article_identifier_data = {
            "article_id": article,
            "identifier_type": "arXiv",
            "identifier_value": arxiv.get("value"),
        }
        doi = data.get("dois")[0].get("value")
        if ArticleIdentifier.objects.filter(
            identifier_type="arXiv", article_id=article
        ).exists():
            article_identifier = ArticleIdentifier.objects.get(
                article_id=article, identifier_type="arXiv"
            )
            article_identifier.__dict__.update(**article_identifier_data)
        else:
            ArticleIdentifier.objects.get_or_create(**article_identifier_data)


def _create_copyright(data, article):
    for copyright in data.get("copyright", []):
        copyright_data = {
            "article_id": article,
            "statement": copyright.get("statement", ""),
            "holder": copyright.get("holder", ""),
            "year": copyright.get("year"),
        }
        if Copyright.objects.filter(article_id=article).exists():
            copyright = Copyright.objects.get(article_id=article)
            copyright.__dict__.update(**copyright_data)
        else:
            Copyright.objects.get_or_create(**copyright_data)


def _create_article_arxiv_category(data, article):
    if "arxiv_eprints" in data.keys():
        for idx, arxiv_category in enumerate(
            data["arxiv_eprints"][0].get("categories", [])
        ):
            article_arxiv_category_data = {
                "article_id": article,
                "category": arxiv_category,
                "primary": True if idx == 0 else False,
            }
            if ArticleArxivCategory.objects.filter(article_id=article).exists():
                article_arxiv_category = ArticleArxivCategory.objects.get(
                    article_id=article
                )
                article_arxiv_category.__dict__.update(**article_arxiv_category_data)
            else:
                ArticleArxivCategory.objects.get_or_create(
                    **article_arxiv_category_data
                )


def _create_publisher(data):
    publishers = []
    for imprint in data.get("imprints"):
        publisher_data = {
            "name": imprint.get("publisher"),
        }
        publisher, _ = Publisher.objects.get_or_create(**publisher_data)
        publishers.append(publisher)
    return publishers


def _create_publication_info(data, article, publishers):
    for idx, publication_info in enumerate(data.get("publication_info", [])):
        publication_info_data = {
            "article_id": article,
            "journal_volume": publication_info.get("journal_volume", ""),
            "journal_title": publication_info.get("journal_title", ""),
            "journal_issue": publication_info.get("journal_issue", ""),
            "page_start": publication_info.get("page_start", ""),
            "page_end": publication_info.get("page_end", ""),
            "artid": publication_info.get("artid", ""),
            "volume_year": publication_info.get("year"),
            "journal_issue_date": publication_info.get("journal_issue_date"),
            "publisher_id": publishers[idx].id,
        }
        if PublicationInfo.objects.filter(article_id=article).exists():
            publication_info = PublicationInfo.objects.get(article_id=article)
            publication_info.__dict__.update(**publication_info_data)
        else:
            PublicationInfo.objects.get_or_create(**publication_info_data)


def _create_experimental_collaborations(data):
    if "collaborations" in data.keys():
        for experimental_collaboration in data.get("collaborations", []):
            experimental_collaboration_data = {
                "name": experimental_collaboration.get("value")
            }
            (
                experimental_collaboration,
                _,
            ) = ExperimentalCollaboration.objects.get_or_create(
                **experimental_collaboration_data
            )


def _create_author(data, article):
    authors = []
    for idx, author in enumerate(data.get("authors", [])):
        name_match = re.match(r"(.*),(.*)", author.get("full_name", ""))
        if name_match and len(name_match.groups()) == 2:
            first_name = name_match.group(2)
            last_name = name_match.group(1)
        else:
            first_name = author.get("given_names", "")
            last_name = author.get("surname", "")
        author_data = {
            "article_id": article,
            "first_name": first_name,
            "last_name": last_name,
            "email": author.get("email", ""),
            "author_order": idx,
        }
        author_obj, _ = Author.objects.get_or_create(**author_data)
        authors.append(author_obj)
    return authors


def _create_author_identifier(data, authors):
    for idx, author in enumerate(data.get("authors", [])):
        if "orcid" in author.keys():
            author_identifier_data = {
                "author_id": authors[idx],
                "identifier_type": "ORCID",
                "identifier_value": author.get("orcid"),
            }
            AuthorIdentifier.objects.get_or_create(**author_identifier_data)


def _create_country(affiliation):
    country = affiliation.get("country", "")
    logger.info("Creating country:%s for affiliation:%s", country, affiliation)
    try:
        if not country or country == "HUMAN CHECK":
            return None
        country = country.lower()
        if country == "cern":
            country_data = {
                "code": "CERN",
                "name": "CERN",
            }
        elif country == "jinr":
            country_data = {
                "code": "JINR",
                "name": "JINR",
            }
        elif country == "niger":
            country_data = {
                "code": "NE",
                "name": "Niger",
            }
        elif country == "turkiye" or country == "turkey":
            country_data = {
                "code": "TR",
                "name": "Türkiye",
            }
        else:
            country_data = {
                "code": pycountry.countries.search_fuzzy(country)[0].alpha_2,
                "name": pycountry.countries.search_fuzzy(country)[0].name,
            }
        country_obj, _ = Country.objects.get_or_create(**country_data)
        logger.info("Country:%s created.", country_obj.name)
        return country_obj
    except LookupError as e:
        capture_exception(e)
        return None


def _create_affiliation(data, authors):
    affiliations = []
    for idx, author in enumerate(data.get("authors", [])):
        for affiliation in author.get("affiliations", []):
            country = _create_country(affiliation)
            affiliation_data = {
                "country": country,
                "value": affiliation.get("value", ""),
                "organization": affiliation.get("organization", ""),
            }
            logger.info(
                "Created country:%s for author:%s affiliation:%s",
                country.name if country else "No Country",
                author.get("full_name", "No author name"),
                affiliation.get("value", "No affiliation value"),
            )
            try:
                affiliation, _ = Affiliation.objects.get_or_create(**affiliation_data)
                affiliation.author_id.add(authors[idx].id)
                affiliations.append(affiliation)

            except MultipleObjectsReturned:
                print(affiliation_data)
    return affiliations


def import_to_scoap3(data, migrate_files):
    licenses = _create_licenses(data["license"])
    article = _create_article(data, licenses)
    if migrate_files:
        _create_article_file(data, article)
    _create_article_identifier(data, article)
    _create_copyright(data, article)
    _create_article_arxiv_category(data, article)
    publishers = _create_publisher(data)
    _create_publication_info(data, article, publishers)
    _create_experimental_collaborations(data)
    authors = _create_author(data, article)
    _create_author_identifier(data, authors)
    _create_affiliation(data, authors)
    return article


def update_affiliations(data):
    licenses = _create_licenses(data["license"])
    article = _create_article(data, licenses)
    authors = _create_author(data, article)
    _create_affiliation(data, authors)


@celery_app.task(
    acks_late=True,
    max_retries=5,
    retry_backoff=60,
    autoretry_for=(ConnectionError, ConnectionTimeout),
)
def upload_index_range(es_settings, search_index, doc_ids, folder_name):
    es = Elasticsearch(es_settings)
    response = es.mget(index=search_index, body={"ids": doc_ids})
    documents = response["docs"]
    storage = storages["legacy-records"]

    for document in documents:
        data = document["_source"]
        file_name = data["control_number"]
        json_data = io.BytesIO(json.dumps(data, ensure_ascii=False).encode("UTF-8"))
        storage.save(f"{folder_name}/{file_name}.json", json_data)


@celery_app.task(acks_late=True)
def migrate_legacy_records(folder_name, index_range, migrate_files):
    storage = storages["legacy-records"]
    index_slice = slice(index_range[0], index_range[1])
    for filename in storage.listdir(folder_name)[1][index_slice]:
        if storage.exists(os.path.join(folder_name, filename)) and filename.endswith(
            ".json"
        ):
            with storage.open(os.path.join(folder_name, filename)) as file:
                json_data = json.load(file)
                import_to_scoap3(json_data, migrate_files)


@celery_app.task(acks_late=True)
def link_affiliations(folder_name, index_range):
    storage = storages["legacy-records"]
    index_slice = slice(index_range[0], index_range[1])
    for filename in storage.listdir(folder_name)[1][index_slice]:
        if storage.exists(os.path.join(folder_name, filename)):
            with storage.open(os.path.join(folder_name, filename)) as file:
                json_data = json.load(file)
                update_affiliations(json_data)
