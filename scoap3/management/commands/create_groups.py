from django.core.management.base import BaseCommand

from scoap3.utils.create_goups import create_custom_groups


class Command(BaseCommand):
    help = "Create custom groups with permissions"

    def handle(self, *args, **options):
        create_custom_groups()
        self.stdout.write(self.style.SUCCESS("Custom groups created successfully."))
