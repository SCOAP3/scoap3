from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestsAPIThrottle(APITestCase):
    def setUp(self):
        cache.clear()

    @pytest.mark.xfail(reason="Not implemented")
    @patch("rest_framework.throttling.AnonRateThrottle.get_rate")
    def test_throttling(self, mock):
        mock.return_value = "1/day"
        _url = reverse("api:article-list")
        self.client.get(_url)
        response = self.client.get(_url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
