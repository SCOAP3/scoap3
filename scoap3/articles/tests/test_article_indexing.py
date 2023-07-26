import json

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_article_post_and_delete(client, user, license):
    client.force_login(user)
    article = {
        "title": "string",
        "related_licenses": [license.id],
    }
    response = client.post(
        reverse("api:article-list"),
        data=article,
    )
    assert response.status_code == 201

    article_id = json.loads(response.content)["id"]
    article_detail_url = reverse("api:article-detail", kwargs={"pk": article_id})

    response = client.get(article_detail_url)
    assert response.status_code == 200

    response = client.delete(article_detail_url)
    assert response.status_code == 204
