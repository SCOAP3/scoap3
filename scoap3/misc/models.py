from django.db import models


class Country(models.Model):
    code = models.CharField(
        max_length=2,
        primary_key=True,
        unique=True,
    )
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["code"]


class Affiliation(models.Model):
    author_id = models.ManyToManyField("authors.Author")
    country = models.ForeignKey("misc.Country", on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)

    class Meta:
        ordering = ["id"]


class InstitutionIdentifierType(models.TextChoices):
    ROR = ("ROR",)


class InstitutionIdentifier(models.Model):
    affiliation_id = models.ForeignKey(
        "misc.Affiliation",
        on_delete=models.CASCADE,
    )
    identifier_type = models.CharField(
        max_length=255,
        choices=InstitutionIdentifierType.choices,
    )
    identifier_value = models.CharField(
        max_length=255,
    )

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(
                fields=["affiliation_id", "identifier_type", "identifier_value"]
            )
        ]


class Publisher(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["id"]


class PublicationInfo(models.Model):
    article_id = models.ForeignKey("articles.Article", on_delete=models.CASCADE)
    journal_volume = models.CharField(max_length=255, blank=True)
    journal_title = models.CharField(max_length=255)
    journal_issue = models.CharField(max_length=255, blank=True)
    page_start = models.PositiveIntegerField()
    page_end = models.PositiveIntegerField()
    artid = models.CharField(max_length=255)
    volume_year = models.CharField(max_length=255)
    journal_issue_date = models.DateField()
    publisher = models.ForeignKey("misc.Publisher", on_delete=models.CASCADE)

    class Meta:
        ordering = ["id"]


class License(models.Model):
    url = models.URLField(blank=True)
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["id"]


class Copyright(models.Model):
    article_id = models.ForeignKey("articles.Article", on_delete=models.CASCADE)
    statement = models.CharField(max_length=255)
    holder = models.CharField(max_length=255)
    year = models.PositiveIntegerField()

    class Meta:
        ordering = ["id"]


class ArxivCategoryType(models.TextChoices):
    QUA223 = ("qua.223",)


class ArticleArxivCategory(models.Model):
    article_id = models.ForeignKey("articles.Article", on_delete=models.CASCADE)
    category = models.CharField(
        max_length=255,
        choices=ArxivCategoryType.choices,
    )
    primary = models.BooleanField(null=False)

    class Meta:
        ordering = ["id"]


class ExperimentalCollaboration(models.Model):
    article_id = models.ManyToManyField("articles.Article")
    name = models.CharField(max_length=255)
    experimental_collaboration_order = models.IntegerField()

    class Meta:
        ordering = ["id"]


class Funder(models.Model):
    article_id = models.ManyToManyField("articles.Article")
    funder_identifier = models.CharField(max_length=255)
    funder_name = models.CharField(max_length=255)
    award_number = models.CharField(max_length=255)

    class Meta:
        ordering = ["id"]


class RelatedMaterialType(models.TextChoices):
    DATASET = ("dataset",)
    SOFTWARE = ("software",)


class RelatedMaterial(models.Model):
    title = models.CharField(max_length=255)
    doi = models.CharField(max_length=255)
    related_material_type = models.CharField(
        max_length=255,
        choices=RelatedMaterialType.choices,
    )

    class Meta:
        ordering = ["id"]
