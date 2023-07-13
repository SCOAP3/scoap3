import json

import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client
from rest_framework.authtoken.models import Token

pytestmark = pytest.mark.django_db
User = get_user_model()


@pytest.fixture
def admin_user_token(user):
    client = Client()
    password = "admin"
    my_admin = User.objects.create_superuser("admin", "myemail@test.com", password)
    client.login(username=my_admin.username, password="admin")
    user_token = Token.objects.create(user=user)
    return {"client": client, "user_token": user_token}


@pytest.fixture
def license_id(admin_user_token):
    license = {"url": "https://creativecommons.org/about/cclicenses/", "name": "cc"}
    response = admin_user_token["client"].post(
        "/api/license/",
        data=license,
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Token {admin_user_token['user_token']}",
    )
    return json.loads(response.content.decode("utf-8"))["id"]


def test_article_post_and_delete(admin_user_token, license_id):
    response = admin_user_token["client"].get(
        "/api/license/",
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Token {admin_user_token['user_token']}",
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
    response = admin_user_token["client"].post(
        url,
        data=article,
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Token {admin_user_token['user_token']}",
    )
    article_id = json.loads(response.content.decode("utf-8"))["id"]
    assert response.status_code == 201
    opensearch_url = f"http://localhost:8000/search/article/{article_id}/"
    response = admin_user_token["client"].get(
        opensearch_url,
        data=article,
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Token {admin_user_token['user_token']}",
    )
    assert response.status_code == 200
    url_delete_article = f"http://localhost:8000/api/articles/{article_id}/"
    response = admin_user_token["client"].delete(
        url_delete_article,
        data=article,
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Token {admin_user_token['user_token']}",
    )
    assert response.status_code == 204
