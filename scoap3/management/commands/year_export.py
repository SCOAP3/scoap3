import csv
import datetime
import logging

from django.core.files.storage import storages
from django.core.management.base import BaseCommand, CommandParser

from scoap3.utils.tools import year_export

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Export article information by year"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--start",
            type=str,
            required=False,
            help="Start date.",
        )

        parser.add_argument(
            "--end",
            type=str,
            required=False,
            help="End date.",
        )

        parser.add_argument(
            "--publisher",
            type=str,
            required=False,
            help="Publisher Name",
        )

    def handle(self, *args, **options):
        storage = storages["default"]
        result = year_export(options["start"], options["end"], options["publisher"])

        with storage.open(
            f"scoap3_export_years_{datetime.datetime.now()}.csv", "w"
        ) as f:
            writer = csv.writer(f)
            writer.writerow(result["header"])
            writer.writerows(result["data"])
