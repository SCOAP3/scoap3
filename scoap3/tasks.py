import io
import json
import logging
import os
import re

import country_converter as coco
import requests
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage, storages
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
cc = coco.CountryConverter()


def get_default_storage_path():
    if hasattr(default_storage, "bucket"):
        bucket_name = default_storage.bucket.name
        media_path = default_storage.location
        return f"{bucket_name}/{media_path}"

    return ""


DEFAULT_STORAGE_PATH = get_default_storage_path()


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


def _create_article(data):
    article_data = {
        "title": data["titles"][0].get("title"),
        "subtitle": data["titles"][0].get("subtitle", ""),
    }
    try:
        article_data["abstract"] = data["abstracts"][0].get("value", "")
    except (KeyError, IndexError):
        pass

    doi_exists = False
    doi_value = data.get("dois")[0].get("value")
    if doi_value:
        doi_exists = ArticleIdentifier.objects.filter(
            identifier_type="DOI", identifier_value=data.get("dois")[0].get("value")
        ).exists()

    publication_date = None
    try:
        publication_date = data["imprints"][0].get("date")
    except (KeyError, IndexError):
        pass
    if publication_date:
        article_data["publication_date"] = publication_date

    # if "control_number" present, means it is a legacy record
    if data.get("control_number"):
        if doi_exists:
            logger.info(
                f"Creating article with id={data['control_number']} - "
                f"Article with DOI={doi_value} already exists."
            )
        control_number = int(data["control_number"])
        if Article.objects.filter(pk=control_number).exists():
            article = Article.objects.get(pk=control_number)
            article.__dict__.update(**article_data)
        else:
            article_data["id"] = control_number
            article = Article.objects.create(**article_data)
            article._created_at = data.get("_created") or data.get(
                "record_creation_date"
            )
    # else if "doi" present, check to update a already inserted article
    elif doi_exists:
        article = ArticleIdentifier.objects.get(
            identifier_type="DOI", identifier_value=doi_value
        ).article_id
        if publication_date:
            article_data["publication_date"] = publication_date
        article.__dict__.update(**article_data)
        if len(data.get("authors", [])) > 0:
            article.authors.all().delete()

    # else create new
    else:
        article_data["publication_date"] = publication_date
        article = Article.objects.create(**article_data)
        article._created_at = data.get("_created") or data.get("record_creation_date")

    licenses = _create_licenses(data["license"])
    article.related_licenses.set(licenses)
    article.save()
    return article


def _create_article_file(data, article, copy_files=False):
    for file in data.get("_files", []):
        article_id = article.id
        filename = file.get("key")
        file_path = f"files/{article_id}/{filename}"
        filetype = file.get("filetype", "")

        if filetype in ["pdfa", "pdf/a", "pdf_a"]:
            filetype = "pdf/a"

        article = Article.objects.get(pk=article_id)
        article_file_data = {
            "article_id": article,
            "file": file_path,
            "filetype": filetype,
        }
        ArticleFile.objects.get_or_create(**article_file_data)
        if copy_files:
            construct_legacy_filepath(article_id, file)

    for file in data.get("files", {}):
        article_id = article.id
        file_path = data["files"][file]["path"]
        filetype = file
        version_id = data["files"][file]["version_id"]

        if filetype in ["pdfa", "pdf/a", "pdf_a"]:
            filetype = "pdf/a"

        if DEFAULT_STORAGE_PATH:
            file_path = file_path.replace(DEFAULT_STORAGE_PATH, "")
        article = Article.objects.get(pk=article_id)
        article_file_data = {
            "article_id": article,
            "file": file_path,
            "filetype": filetype,
            "version_id": version_id
        }
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

        ArticleIdentifier.objects.get_or_create(**article_identifier_data)


def _create_copyright(data, article):
    for copyright in data.get("copyright", []):
        copyright_data = {
            "article_id": article,
            "statement": copyright.get("statement", ""),
            "holder": copyright.get("holder", ""),
            "year": copyright.get("year"),
        }
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
            ArticleArxivCategory.objects.get_or_create(**article_arxiv_category_data)


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
            "journal_volume": publication_info.get("journal_volume", ""),
            "journal_title": publication_info.get("journal_title", ""),
            "journal_issue": publication_info.get("journal_issue", ""),
            "page_start": publication_info.get("page_start", ""),
            "page_end": publication_info.get("page_end", ""),
            "artid": publication_info.get("artid", ""),
            "journal_issue_date": publication_info.get("journal_issue_date"),
            "publisher_id": publishers[idx].id,
        }
        volume_year = publication_info.get("year", "")
        if PublicationInfo.objects.filter(article_id=article.id).exists():
            if volume_year:
                publication_info_data["volume_year"] = volume_year
            publication_info_obj = PublicationInfo.objects.filter(
                article_id=article.id
            ).first()
            publication_info_obj.__dict__.update(**publication_info_data)
        else:
            if volume_year:
                publication_info_data["volume_year"] = volume_year
            publication_info_data["article_id"] = article
            publication_info_obj = PublicationInfo.objects.create(
                **publication_info_data
            )
        publication_info_obj.save()


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
                "code": cc.convert(country, to="iso2"),
                "name": cc.convert(country, to="name_short"),
            }
        country_obj, created = Country.objects.get_or_create(**country_data)
        if created:
            logger.info("Created country:%s for affiliation:%s", country, affiliation)
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
            try:
                affiliation, _ = Affiliation.objects.get_or_create(**affiliation_data)
                affiliation.author_id.add(authors[idx].id)
                affiliations.append(affiliation)

            except MultipleObjectsReturned:
                logger.error(
                    "While creating author:%s affiliation:%s",
                    author.get("full_name", "No author name"),
                    affiliation.get("value", "No affiliation value"),
                )
    return affiliations


def get_articles_by_doi(dois):
    articles = Article.objects.filter(
        article_identifiers__identifier_type="DOI",
        article_identifiers__identifier_value__in=dois,
    ).distinct()

    return articles


def import_to_scoap3(data, migrate_files, copy_files=False):
    article = _create_article(data)
    if migrate_files:
        _create_article_file(data, article, copy_files)
    _create_article_identifier(data, article)
    _create_copyright(data, article)
    _create_article_arxiv_category(data, article)
    publishers = _create_publisher(data)
    _create_publication_info(data, article, publishers)
    _create_experimental_collaborations(data)
    authors = _create_author(data, article)
    _create_author_identifier(data, authors)
    _create_affiliation(data, authors)
    article.save()
    return article


def update_affiliations(data):
    article = _create_article(data)
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
        try:
            data = document["_source"]
            file_name = data["control_number"]
            json_data = io.BytesIO(json.dumps(data, ensure_ascii=False).encode("UTF-8"))
            storage.save(f"{folder_name}/{file_name}.json", json_data)
        except Exception as e:
            logger.error(f"upload_index_range::error processing document: {e}")
            continue


def fetch_file_and_save_to_s3(url, s3_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise error for HTTP status codes >= 400

        file_content = ContentFile(response.content)

        s3_file = default_storage.save(s3_path, file_content)

        s3_url = default_storage.url(s3_file)

        print(f"File successfully saved to {s3_url}")
        return s3_url
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch file from URL: {e}")
        return None
    except Exception as e:
        print(f"Failed to save file to S3: {e}")
        return None


def construct_legacy_filepath(article_id, f):
    bucket_id = f.get("bucket")
    file_key = f.get("key")
    file_url = f"https://repo.scoap3.org/api/files/{bucket_id}/{file_key}"
    s3path = f"files/{article_id}/{file_key}"
    fetch_file_and_save_to_s3(file_url, s3path)


@celery_app.task(acks_late=True)
def migrate_legacy_records(folder_name, index_range, migrate_files):
    storage = storages["legacy-records"]
    index_slice = slice(index_range[0], index_range[1])
    for filename in storage.listdir(folder_name)[1][index_slice]:
        if filename.endswith(".json"):
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
