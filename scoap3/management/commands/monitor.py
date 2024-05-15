import json
import os
from datetime import datetime

import urllib3
from django.core.management.base import BaseCommand, CommandParser

from scoap3.management.commands.elastic_search_client import ElastiSearchClient
from scoap3.management.commands.utils import (
    get_countries_from_response,
    get_countries_from_response_legacy,
    get_dois_from_response,
    get_dois_from_response_legacy,
    get_mapped_dois_and_files_legacy,
    get_mapped_dois_and_files_new,
    get_new_added_files_new_scoap3,
    get_publishers_from_response,
    get_publishers_from_response_legacy,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Command(BaseCommand):
    help = "Get all records DOIs count and countries for for specific range of time"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            required=False,
            help="Batchsize for upload per task",
        )
        parser.add_argument(
            "--time-unit",
            type=str,
            required=True,
            help="h - hours, d - days, w - weeks, m - months, y- years ",
        )
        parser.add_argument(
            "--gte",
            type=str,
            required=True,
            help="Records not older than",
        )

    def handle(self, *args, **options):
        port = 443
        if "OPENSEARCH_HOST" not in os.environ:
            raise KeyError("Missing ES Host!")
        host = os.environ["OPENSEARCH_HOST"]
        if "OPENSEARCH_USER" not in os.environ:
            raise KeyError("Missing ES Username!")
        username = os.environ["OPENSEARCH_USER"]
        if "OPENSEARCH_PASSWORD" not in os.environ:
            raise KeyError("Missing ES password!")
        password = (os.environ["OPENSEARCH_PASSWORD"],)
        if "OPENSEARCH_INDEX_PREFIX" not in os.environ:
            raise KeyError("Missing new scoap3 index!")
        index_old_scoap3 = os.environ["OPENSEARCH_INDEX_PREFIX"]

        es = ElastiSearchClient(
            host=host,
            port=port,
            username=username,
            password=password,
            index="scoap3-records-record-1646666385",
        )

        dois_created = es.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_dois_from_response_legacy,
            action="_created",
        )

        dois_updated = es.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_dois_from_response_legacy,
            action="_updated",
        )

        countries = es.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_countries_from_response_legacy,
            action="_created",
        )

        es_new = ElastiSearchClient(
            index=index_old_scoap3,
            host=host,
            port=port,
            username=username,
            password=password,
        )
        dois_created_new = es_new.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_dois_from_response,
            action="_created_at",
        )

        dois_updated_new = es_new.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_dois_from_response,
            action="_updated_at",
        )

        countries_new = es_new.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_countries_from_response,
            action="_created_at",
        )
        summary = {
            "created_in_legacy_but_not_in_new": list(
                set(dois_created) - set(dois_created_new)
            ),
            "created_in_new_but_not_in_legacy": list(
                set(dois_created_new) - set(dois_created)
            ),
            "updated_in_legacy_but_not_in_new": list(
                set(dois_updated) - set(dois_updated_new)
            ),
            "updated_in_new_but_not_in_legacy": list(
                set(dois_updated_new) - set(dois_updated)
            ),
            "countries_in_legacy_but_not_in_new": list(
                set(countries) - set(countries_new)
            ),
            "countries_in_new_but_not_in_legacy": list(
                set(countries_new) - set(countries)
            ),
        }

        current_date = datetime.datetime.now().date()
        current_date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
        file_path = f"{current_date_str}_summary.txt"
        with open(file_path, "w") as file:
            json.dump(summary, file, indent=4)

        mapped_dois_and_files_legacy = es.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_mapped_dois_and_files_legacy,
            action="_created",
        )

        mapped_dois_and_files_new = es_new.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_mapped_dois_and_files_new,
            action="_created_at",
        )

        file_path = f"{current_date_str}_mapped_files_and_dois_legacy.txt"
        with open(file_path, "w") as file:
            json.dump({"records": mapped_dois_and_files_legacy}, file, indent=4)

        file_path = f"{current_date_str}_mapped_files_and_dois_new.txt"
        with open(file_path, "w") as file:
            json.dump({"records": mapped_dois_and_files_new}, file, indent=4)

        mapped_dois_and_added_files_on_update = es.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_new_added_files_new_scoap3,
            action="_updated_at",
        )

        file_path = f"{current_date_str}_mapped_dois_and_added_files_on_update.txt"
        with open(file_path, "w") as file:
            json.dump(
                {"records": mapped_dois_and_added_files_on_update}, file, indent=4
            )

        mapped_dois_and_publishers_created_legacy = es.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_publishers_from_response_legacy,
            action="_created_at",
        )

        file_path = f"{current_date_str}_mapped_dois_and_publishers_created_legacy.txt"
        with open(file_path, "w") as file:
            json.dump(
                {"records": mapped_dois_and_publishers_created_legacy}, file, indent=4
            )

        mapped_dois_and_publishers_created = es_new.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_publishers_from_response,
            action="_created_at",
        )

        file_path = f"{current_date_str}_mapped_dois_and_publishers_created.txt"
        with open(file_path, "w") as file:
            json.dump({"records": mapped_dois_and_publishers_created}, file, indent=4)

        mapped_dois_and_publishers_updated_legacy = es.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_publishers_from_response_legacy,
            action="_updated",
        )

        file_path = f"{current_date_str}_mapped_dois_and_publishers_updated_legacy.txt"
        with open(file_path, "w") as file:
            json.dump(
                {"records": mapped_dois_and_publishers_updated_legacy}, file, indent=4
            )
        mapped_dois_and_publishers_updated = es_new.get_items(
            batch_size=options["batch_size"],
            gte=options["gte"],
            time_unit=options["time_unit"],
            parse_function=get_publishers_from_response,
            action="_updated_at",
        )
        file_path = f"{current_date_str}_mapped_dois_and_publishers_updated.txt"
        with open(file_path, "w") as file:
            json.dump({"records": mapped_dois_and_publishers_updated}, file, indent=4)
