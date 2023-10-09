import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db
User = get_user_model()


class TestGroupPermissions(TestCase):
    fixtures = ["custom_groups_and_permissions.json"]

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.admin_user_group = Group.objects.get(name="Admin")
        self.user.groups.add(self.admin_user_group)
        user_token = Token.objects.create(user=self.user)
        self.token = user_token

        client = APIClient()
        client.force_authenticate(user=self.user)

        license_data = {
            "url": "https://creativecommons.org/about/cclicenses/",
            "name": "cc",
        }
        url = reverse("api:license-list")

        response_license = client.post(
            url,
            data=license_data,
            format="json",
            HTTP_AUTHORIZATION=f"Token {self.token}",
        )
        self.license_id = response_license.data["id"]
        article_data = {
            "reception_date": "2023-07-11",
            "acceptance_date": "2023-07-11",
            "publication_date": "2023-07-11",
            "first_online_date": "2023-07-11",
            "title": "string",
            "subtitle": "string",
            "abstract": "string",
            "related_licenses": [self.license_id],
            "related_materials": [],
            "_files": [],
        }
        url = reverse("api:article-list")
        response_article = self.client.post(
            url,
            data=article_data,
            format="json",
            HTTP_AUTHORIZATION=f"Token {self.token}",
        )
        self.article_id = response_article.data["id"]

    def test_user_belongs_to_group(self):
        user = User.objects.get(username="testuser")
        self.assertTrue(user.groups.filter(name="Admin").exists())

    def test_delete_article(self):
        url_delete_article = reverse("api:article-detail", args=[self.article_id])
        response = self.client.delete(
            url_delete_article,
            format="json",
            HTTP_AUTHORIZATION=f"Token {self.token}",
        )

        assert response.status_code == 204
