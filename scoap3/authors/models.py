from django.db import models


class AuthorIdentifierType(models.TextChoices):
    ORCID = ("ORCID",)


class Author(models.Model):
    article_id = models.ForeignKey(
        "articles.Article", on_delete=models.CASCADE, blank=True
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    author_order = models.IntegerField(blank=True)

    class Meta:
        ordering = ["id"]


class AuthorIdentifier(models.Model):
    author_id = models.ForeignKey(
        "authors.Author",
        on_delete=models.CASCADE,
    )
    identifier_type = models.CharField(
        max_length=255,
        choices=AuthorIdentifierType.choices,
    )
    identifier_value = models.CharField(
        max_length=255,
    )

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["author_id", "identifier_type", "identifier_value"])
        ]
