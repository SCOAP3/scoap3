from django.db import models


class AuthorIdentifierType(models.TextChoices):
    ORCID = ("ORCID",)


class Author(models.Model):
    article_id = models.ForeignKey("articles.Article", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, blank=True, default="")
    last_name = models.CharField(max_length=255, blank=True, default="")
    email = models.EmailField(blank=True, null=True)
    author_order = models.IntegerField()

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
