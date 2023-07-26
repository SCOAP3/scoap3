from factory import Faker
from factory.django import DjangoModelFactory

from scoap3.misc.models import License


class LicenseFactory(DjangoModelFactory):
    url = Faker("url")
    name = Faker("domain_word")

    class Meta:
        model = License
        django_get_or_create = ["url"]
