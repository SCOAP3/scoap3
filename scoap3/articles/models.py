from django.db import models
from django.db.models.fields.files import FieldFile


class ArticleIdentifierType(models.TextChoices):
    DOI = ("DOI",)
    ARXIV = ("arXiv",)


def article_file_upload_path(instance, filename):
    return f"files/{instance.article_id.id}/{filename}"


class CustomFieldFile(FieldFile):
    @property
    def size(self):
        if self.storage.exists(self.name):
            return super().size
        else:
            return "-"


class CustomFileField(models.FileField):
    attr_class = CustomFieldFile


class Article(models.Model):
    reception_date = models.DateField(blank=True, null=True)
    acceptance_date = models.DateField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    first_online_date = models.DateField(blank=True, null=True)
    title = models.TextField()
    subtitle = models.TextField(blank=True, default="")
    abstract = models.TextField(blank=True, default="")
    related_licenses = models.ManyToManyField(
        "misc.License",
        related_name="related_licenses",
    )
    related_materials = models.ManyToManyField(
        "misc.RelatedMaterial", related_name="related_articles", blank=True
    )
    _created_at = models.DateTimeField(auto_now_add=True)
    _updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]


class ArticleFile(models.Model):
    article_id = models.ForeignKey(
        "articles.Article", on_delete=models.CASCADE, related_name="related_files"
    )
    file = CustomFileField(upload_to=article_file_upload_path)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.file.name


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
