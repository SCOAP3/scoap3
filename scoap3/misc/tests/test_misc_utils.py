import pytest
from django.test import TestCase

from scoap3.misc.utils import (
    fetch_doi_registration_date,
    fetch_doi_registration_date_aps,
)


@pytest.mark.vcr
class TestFetchDOIRegistrationDate(TestCase):
    def test_fetch_doi_registration_date_happy_case(self):
        assert fetch_doi_registration_date("10.1007/JHEP11(2019)001") == "2019-11-11"

    def test_fetch_doi_registration_date_invalid_doi(self):
        assert fetch_doi_registration_date("10.10232332/JHEP11(2019)0010") is None


@pytest.mark.vcr
class TestFetchDoiRegistrationDateAPS(TestCase):
    def test_fetch_doi_registration_date_aps_happy_case(self):
        assert fetch_doi_registration_date_aps("10.1103/923l-yxkc") == "2025-06-26"

    def test_fetch_doi_registration_date_invalid_doi(self):
        assert fetch_doi_registration_date_aps("10.1103/923l-yxkc-invalid") is None
