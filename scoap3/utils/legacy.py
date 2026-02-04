import environ
from elasticsearch import Elasticsearch

from scoap3.tasks import import_to_scoap3

env = environ.Env()


def get_legacy_es(es_config=None):
    if es_config is None:
        es_config = {}
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


def fetch_legacy_articles(es_config=None, dois=None, ids=None, batch_size=1000):
    if ids is None:
        ids = []
    if dois is None:
        dois = []
    if es_config is None:
        es_config = {}
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


def migrate_legacy_records_by_id_or_doi(dois=None, ids=None, migrate_files=True):
    if ids is None:
        ids = []
    if dois is None:
        dois = []
    articles = fetch_legacy_articles(dois=dois, ids=ids)
    for article in articles:
        article_metadata = article.get("_source")
        import_to_scoap3(article_metadata, migrate_files, copy_files=True)
