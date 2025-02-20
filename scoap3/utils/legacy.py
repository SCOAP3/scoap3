import environ
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from elasticsearch import Elasticsearch

from scoap3.tasks import import_to_scoap3

env = environ.Env()


def get_legacy_es(es_config={}):
    if not es_config.get("username"):
        es_config["username"] = env("LEGACY_OPENSEARCH_USERNAME")
    if not es_config.get("password"):
        es_config["password"] = env("LEGACY_OPENSEARCH_PASSWORD")
    if not es_config.get("host"):
        es_config["host"] = env("LEGACY_OPENSEARCH_HOST")

    es_settings = [
        dict(
            host=es_config.get("host"),
            port=es_config.get("port", 443),
            http_auth=(es_config["username"], es_config["password"]),
            use_ssl=True,
            verify_certs=False,
            timeout=60,
            url_prefix="os",
            http_compress=True,
        )
    ]
    es = Elasticsearch(es_settings)
    es_index = es_config.get("index", "scoap3-records")
    es.indices.refresh(es_index)

    return es, es_index


def fetch_legacy_articles(es_config={}, dois=[], ids=[], batch_size=1000):
    es, es_index = get_legacy_es(es_config)

    es_body = {
        "query": {
            "bool": {
                "should": [
                    {"terms": {"dois.value": dois}},
                    {"terms": {"control_number": ids}},
                ],
                "minimum_should_match": 1,
            }
        }
    }

    scroll = "30s"
    response = es.search(
        index=es_index,
        scroll=scroll,
        size=batch_size,
        body=es_body,
    )
    scroll_id = response["_scroll_id"]
    total_docs = response["hits"]["total"]["value"]

    processed = 0
    all_docs = []
    while processed < total_docs:
        documents = response["hits"]["hits"]
        all_docs.extend(documents)
        processed += len(documents)
        response = es.scroll(scroll_id=scroll_id, scroll=scroll)
    es.clear_scroll(scroll_id=scroll_id)

    return all_docs


def migrate_legacy_records_by_id_or_doi(dois=[], ids=[], migrate_files=True):
    articles = fetch_legacy_articles(dois=dois, ids=ids)
    for article in articles:
        article_metadata = article.get("_source")
        import_to_scoap3(article_metadata, migrate_files, copy_files=True)


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
