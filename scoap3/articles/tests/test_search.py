import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.usefixtures("rebuild_opensearch_index")
def test_article_search(user, client):
    client.force_login(user)
    response = client.get(reverse("search:article-list"))
    assert response.status_code == status.HTTP_200_OK
