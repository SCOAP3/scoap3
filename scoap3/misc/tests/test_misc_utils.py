import pytest
from django.test import TestCase

from scoap3.misc.utils import fetch_doi_registration_date


@pytest.mark.vcr
class TestFetchDOIRegistrationDate(TestCase):
    def test_fetch_doi_registration_date_happy_case(self):
        self.assertEqual(
            fetch_doi_registration_date("10.1007/JHEP11(2019)001"), "2019-11-11"
        )

    def test_fetch_doi_registration_date_invalid_doi(self):
        self.assertEqual(
            fetch_doi_registration_date("10.10232332/JHEP11(2019)0010"), None
        )
