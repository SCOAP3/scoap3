import io
import json
import time

import environ
import urllib3
from django.core.files.storage import storages
from django.core.management.base import BaseCommand, CommandParser
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

env = environ.Env()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Command(BaseCommand):
    help = "Import records from elasticsearch index."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--host",
            type=str,
            required=True,
            help="URL of the elastic search instance.",
        )
        parser.add_argument(
            "--port",
            type=int,
            required=True,
            help="Port of the elastic search instance.",
        )
        parser.add_argument(
            "--index",
            type=str,
            required=True,
            help="Elasticsearch index to export from.",
        )
        parser.add_argument(
            "--username",
            type=str,
            required=False,
            help="Username for Elasticsearch. Uses OPENSEARCH_USER if empty.",
        )
        parser.add_argument(
            "--password",
            type=str,
            required=False,
            help="Password for Elasticsearch. Uses OPENSEARCH_PASSWORD if empty.",
        )

    def handle(self, *args, **options):
        if not options["username"]:
            options["username"] = env("OPENSEARCH_USER")
        if not options["password"]:
            options["password"] = env("OPENSEARCH_PASSWORD")

        storage = storages["legacy-records"]
        timestamp = round(time.time() * 1000)
        es = Elasticsearch(
            [
                dict(
                    host=options["host"],
                    port=options["port"],
                    http_auth=(options["username"], options["password"]),
                    use_ssl=True,
                    verify_certs=False,
                    timeout=60,
                    url_prefix="es",
                    http_compress=True,
                )
            ]
        )
        es.indices.refresh(options["index"])
        total_records = es.cat.count(options["index"], params={"format": "json"})[0][
            "count"
        ]

        self.stdout.write(f"Found {total_records} records.")
        query = {"query": {"type": {"value": "_doc"}}}
        counter = 0
        unknown_counter = 0
        for data in scan(es, index=options["index"], query=query):
            data = data["_source"]
            if "control_number" in data:
                file_name = data["control_number"]
            else:
                file_name = "UNKNOWN_" + str(unknown_counter)
                self.stdout.write(f"Found record without control_number, {file_name}")
                unknown_counter += 1

            json_data = io.BytesIO(
                json.dumps(data, ensure_ascii=False, indent=4).encode("UTF-8")
            )
            storage.save(f"{timestamp}/{file_name}.json", json_data)
            counter += 1
            if counter % 1000 == 0:
                self.stdout.write(f"Loaded {counter}/{total_records}")
