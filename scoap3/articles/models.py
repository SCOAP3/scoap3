from django.db import models


class ArticleIdentifierType(models.TextChoices):
    DOI = ("DOI",)
    ARXIV = ("arXiv",)


class Article(models.Model):
    reception_date = models.DateField(blank=True, null=True)
    acceptance_date = models.DateField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    first_online_date = models.DateField(blank=True, null=True)
    title = models.TextField()
    subtitle = models.CharField(max_length=255, blank=True, default="")
    abstract = models.TextField(blank=True, default="")
    related_licenses = models.ManyToManyField(
        "misc.License",
        related_name="related_licenses",
    )
    related_materials = models.ManyToManyField(
        "misc.RelatedMaterial", related_name="related_articles", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]


class ArticleIdentifier(models.Model):
    article_id = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
    )
    identifier_type = models.CharField(
        max_length=255,
        choices=ArticleIdentifierType.choices,
    )
    identifier_value = models.CharField(
        max_length=255,
    )

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["article_id", "identifier_type", "identifier_value"])
        ]
