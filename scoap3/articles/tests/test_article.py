from datetime import date

import pytest
from django.db.utils import IntegrityError
from django.test import TestCase

from scoap3.articles.models import Article, ArticleIdentifier
from scoap3.utils.tools import update_article_db_model_sequence


@pytest.mark.django_db()
class ArticleModelTest(TestCase):
    def test_save(self):
        update_article_db_model_sequence(1)
        article = Article.objects.create(title="Test Article", abstract="Test Content")
        article.save()
        self.assertEqual(article.id, 1)

        new_article = Article.objects.create(
            id=1000, title="Test Article 2", abstract="Test Content 2"
        )
        new_article.save()
        self.assertEqual(new_article.id, 1000)

        update_article_db_model_sequence(1001)
        new_article = Article.objects.create(
            title="Test Article 2", abstract="Test Content 2"
        )
        new_article.save()
        self.assertEqual(new_article.id, 1001)

    def test_save_and_update(self):
        article = Article.objects.create(title="Test Article", abstract="Test Content")
        article.save()

        new_article = Article.objects.get(id=article.id)
        new_article.title = "Test Article 2"
        new_article.save()
        self.assertEqual(new_article.title, "Test Article 2")

    def test_unique_doi_constraint(self):
        article1 = Article.objects.create(
            title="Test Article 1",
            publication_date=date(2023, 5, 19),
        )

        article2 = Article.objects.create(
            title="Test Article 2",
            publication_date=date(2023, 5, 20),
        )

        doi_value = "10.1234/test.12345"

        ArticleIdentifier.objects.create(
            article_id=article1, identifier_type="DOI", identifier_value=doi_value
        )

        with self.assertRaises(IntegrityError):
            ArticleIdentifier.objects.create(
                article_id=article2, identifier_type="DOI", identifier_value=doi_value
            )
