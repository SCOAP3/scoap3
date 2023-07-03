import io
import json

import backoff
from django.core.files.storage import storages
from elasticsearch import ConnectionError, ConnectionTimeout, Elasticsearch

from config import celery_app


@celery_app.task()
@backoff.on_exception(backoff.expo, (ConnectionError, ConnectionTimeout))
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
