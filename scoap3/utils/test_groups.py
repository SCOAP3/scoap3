import json

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


class TestGroupPermissions:
    @pytest.fixture
    def group_delete_add(self):
        group_name = "test_group_with_delete_and_add_permissions"
        article_content_type = ContentType.objects.get(
            app_label="articles", model="article"
        )
        add_permission = Permission.objects.get(
            codename="add_article", content_type=article_content_type
        )
        delete_permission = Permission.objects.get(
            codename="delete_article", content_type=article_content_type
        )
        change_permission = Permission.objects.get(
            codename="change_article", content_type=article_content_type
        )
        group, created = Group.objects.get_or_create(name=group_name)
        group.permissions.add(add_permission, delete_permission, change_permission)
        group.save()
        return group

    @pytest.fixture
    def user_with_a_group_token(self, group_delete_add):
        User = get_user_model()
        user = User.objects.create_user(
            username="userWithAGroup",
            email="myemail@test.com",
            password="userWithAGroup",
        )
        user.groups.add(group_delete_add)
        client = APIClient()
        client.force_authenticate(user=user)
        user_token = Token.objects.create(user=user)
        return {"client": client, "user_token": user_token}

    @pytest.fixture
    def license_id(self, user_with_a_group_token):
        license_data = {
            "url": "https://creativecommons.org/about/cclicenses/",
            "name": "cc",
        }
        url = reverse("api:license-list")
        response = user_with_a_group_token["client"].post(
            url,
            data=license_data,
            format="json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        return response.data["id"]

    @pytest.fixture
    def article_id(self, user_with_a_group_token, license_id):
        article_data = {
            "reception_date": "2023-07-11",
            "acceptance_date": "2023-07-11",
            "publication_date": "2023-07-11",
            "first_online_date": "2023-07-11",
            "title": "string",
            "subtitle": "string",
            "abstract": "string",
            "related_licenses": [license_id],
            "related_materials": [],
            "_files": [],
        }
        url = reverse("api:article-list")
        response = user_with_a_group_token["client"].post(
            url,
            data=article_data,
            format="json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        return response.data["id"]

    @pytest.fixture
    def user_without_a_group_token(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="userWithoutAGroup",
            email="myemail@test.com",
            password="userWithoutAGroup",
        )
        client = APIClient()
        client.force_authenticate(user=user)
        user_token = Token.objects.create(user=user)
        return {"client": client, "user_token": user_token}

    def test_article_add_without_permissions(
        self, user_without_a_group_token, license_id
    ):
        url = reverse("api:article-list")
        article_data = {
            "reception_date": "2023-07-11",
            "acceptance_date": "2023-07-11",
            "publication_date": "2023-07-11",
            "first_online_date": "2023-07-11",
            "title": "string",
            "subtitle": "string",
            "abstract": "string",
            "related_licenses": [license_id],
            "related_materials": [],
            "_files": [],
        }
        response = user_without_a_group_token["client"].post(
            url,
            data=article_data,
            format="json",
            HTTP_AUTHORIZATION=f"Token {user_without_a_group_token['user_token']}",
        )
        assert response.status_code == 403

    def test_article_add_delete_with_permissions(
        self, license_id, user_with_a_group_token
    ):
        url_add_article = reverse("api:article-list")
        article_data = {
            "reception_date": "2023-07-11",
            "acceptance_date": "2023-07-11",
            "publication_date": "2023-07-11",
            "first_online_date": "2023-07-11",
            "title": "string",
            "subtitle": "string",
            "abstract": "string",
            "related_licenses": [license_id],
            "related_materials": [],
            "_files": [],
        }
        response = user_with_a_group_token["client"].post(
            url_add_article,
            data=article_data,
            format="json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        assert response.status_code == 201
        article_id = response.data["id"]

        url_get_article = reverse("api:article-detail", args=[article_id])
        response = user_with_a_group_token["client"].get(
            url_get_article,
            format="json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        assert response.status_code == 200

        url_get_article = reverse("api:article-detail", args=[article_id])
        response = user_with_a_group_token["client"].put(
            url_get_article,
            data={"subtitle": "changed subtitle"},
            format="json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        assert response.status_code == 200
        url_get_article = reverse("api:article-detail", args=[article_id])
        response = user_with_a_group_token["client"].get(
            url_get_article,
            format="json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        assert json.loads(response.content)["subtitle"] == "changed subtitle"

        url_delete_article = reverse("api:article-detail", args=[article_id])
        response = user_with_a_group_token["client"].delete(
            url_delete_article,
            format="json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )

        assert response.status_code == 204

        response = user_with_a_group_token["client"].get(
            url_get_article,
            format="json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        assert response.status_code == 404

    def test_article_delete_without_permissions(
        self, user_without_a_group_token, article_id
    ):
        url_delete_article = reverse("api:article-detail", args=[article_id])
        response = user_without_a_group_token["client"].delete(
            url_delete_article,
            format="json",
            HTTP_AUTHORIZATION=f"Token {user_without_a_group_token['user_token']}",
        )
        assert response.status_code == 403
