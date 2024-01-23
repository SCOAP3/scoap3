import pytest
from django.core.management import call_command

from scoap3.misc.models import License
from scoap3.misc.tests.factories import LicenseFactory
from scoap3.users.models import User
from scoap3.users.tests.factories import UserFactory


@pytest.fixture
def rebuild_opensearch_index():
    call_command("opensearch", "index", "rebuild", "--force")
    yield
    call_command("opensearch", "index", "delete", "--force")


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def license(db) -> License:
    return LicenseFactory()


@pytest.fixture(scope="session")
def vcr_config():
    return {
        "ignore_localhost": True,
        "decode_compressed_response": True,
        "filter_headers": ("Authorization", "User-Agent"),
        "record_mode": "once",
        "ignore_hosts": ["127.0.0.1", "localhost", "opensearch"],
    }
