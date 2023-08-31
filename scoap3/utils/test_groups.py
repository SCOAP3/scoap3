from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.test import Client
import json

import json
import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client
from rest_framework.authtoken.models import Token
from scoap3.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

class TestGroupPermissions:
    @pytest.fixture
    def group_delete_add(self):
        group_name = "test_group_with_delete_and_add_permissions"
        article_content_type = ContentType.objects.get(app_label='articles', model='article')
        add_permission = Permission.objects.get(codename='add_article', content_type=article_content_type)
        delete_permission = Permission.objects.get(codename='delete_article', content_type=article_content_type)
        group, created = Group.objects.get_or_create(name=group_name)
        group.permissions.add(add_permission, delete_permission)
        group.save()
        return group

    @pytest.fixture
    def user_with_a_group_token(self, group_delete_add):
        User = get_user_model()
        user = UserFactory()
        client = Client()
        password = "userWithAGroup"
        user_with_a_group = User.objects.create_user("userWithAGroup", "myemail@test.com", password)
        user_with_a_group.groups.add(group_delete_add)
        client.login(username=user_with_a_group.username, password=password)
        user_token = Token.objects.create(user=user)
        return {"client": client, "user_token": user_token}

    @pytest.fixture
    def license_id(self, user_with_a_group_token):
        license = {"url": "https://creativecommons.org/about/cclicenses/", "name": "cc"}
        response = user_with_a_group_token["client"].post(
            "/api/license/",
            data=license,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        license_id_value = json.loads(response.content.decode("utf-8"))["id"]
        return license_id_value

    @pytest.fixture
    def article_id(self, user_with_a_group_token, license_id):
        response = user_with_a_group_token["client"].get(
            "/api/license/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        article = {
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
        url = "http://localhost:8000/api/articles/"
        response = user_with_a_group_token["client"].post(
            url,
            data=article,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        assert response.status_code == 201
        article_id = json.loads(response.content.decode("utf-8"))["id"]
        return article_id

    @pytest.fixture
    def user_without_a_group_token(self):
        User = get_user_model()
        user = UserFactory()
        client = Client()
        password = "userWithoutAGroup"
        user_without_a_group = User.objects.create_user("userWithoutAGroup", "myemail@test.com", password)
        client.login(username=user_without_a_group.username, password=password)
        user_token = Token.objects.create(user=user)
        return {"client": client, "user_token": user_token}

    def test_article_add_without_permissions(self, user_without_a_group_token, license_id):
        response = user_without_a_group_token["client"].get(
            "/api/license/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {user_without_a_group_token['user_token']}",
        )
        article = {
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
        url = "http://localhost:8000/api/articles/"
        response = user_without_a_group_token["client"].post(
            url,
            data=article,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {user_without_a_group_token['user_token']}",
        )
        assert response.status_code == 403

    def test_article_add_delete_with_permissions(self, license_id, user_with_a_group_token):
        response = user_with_a_group_token["client"].get(
            "/api/license/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        article = {
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
        url = "http://localhost:8000/api/articles/"
        response = user_with_a_group_token["client"].post(
            url,
            data=article,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        assert response.status_code == 201
        article_id = json.loads(response.content.decode("utf-8"))["id"]

        url_delete_article = f"http://localhost:8000/api/articles/{article_id}/"
        response = user_with_a_group_token["client"].get(
            url_delete_article,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        response.status_code == 200

        url_delete_article = f"http://localhost:8000/api/articles/{article_id}/"
        response = user_with_a_group_token["client"].delete(
            url_delete_article,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {user_with_a_group_token['user_token']}",
        )
        assert response.status_code == 204

    def test_article_delete_without_permissions(self, user_without_a_group_token, article_id):
        url_delete_article = f"http://localhost:8000/api/articles/{article_id}/"
        response = user_without_a_group_token["client"].delete(
            url_delete_article,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {user_without_a_group_token['user_token']}",
        )
        assert response.status_code == 403

