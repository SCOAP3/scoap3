import pytest

from scoap3.users.models import User
from scoap3.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture(scope="function")
def user(db) -> User:
    return UserFactory()
