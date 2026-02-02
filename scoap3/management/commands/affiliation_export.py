import csv
import datetime

from django.core.files.storage import storages
from django.core.management.base import BaseCommand, CommandParser

from scoap3.utils.tools import affiliation_export


class Command(BaseCommand):
    help = "Link affiliations to authors"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--country",
            type=str,
            required=False,
            help="Country Code.",
        )

        parser.add_argument(
            "--year",
            type=int,
            required=False,
            help="Year.",
        )

    def handle(self, *args, **options):
        storage = storages["default"]
        result = affiliation_export(options["year"], options["country"])

        with storage.open(f"scoap3_export_affiliations_{datetime.datetime.now()}.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(result["header"])
            writer.writerows(result["data"])
