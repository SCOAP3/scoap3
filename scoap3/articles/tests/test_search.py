import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.usefixtures("rebuild_opensearch_index")
def test_article_search(user, client):
    client.force_login(user)
    response = client.get(reverse("search:article-list"))
    assert response.status_code == status.HTTP_200_OK


def test_article_search_ordering_default(user, client, license):
    client.force_login(user)

    articles = [
        {
            "title": "Article 1",
            "related_licenses": [license.id],
            "publication_date": "2014-01-01",
        },
        {
            "title": "Article 2",
            "related_licenses": [license.id],
            "publication_date": "2014-01-02",
        },
        {
            "title": "Article 3",
            "related_licenses": [license.id],
            "publication_date": "2014-01-03",
        },
    ]

    for article in articles:
        response = client.post(
            reverse("api:article-list"),
            data=article,
        )
        assert response.status_code == 201

    response = client.get(reverse("search:article-list"))
    data = response.json()

    publication_dates = []
    for result in data["results"]:
        publication_dates.append(result["publication_date"])

    assert publication_dates == sorted(
        publication_dates, reverse=True
    ), "Articles are not ordered by publication date in descending order"
