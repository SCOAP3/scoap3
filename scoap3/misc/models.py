from django.db import models


class Country(models.Model):
    code = models.CharField(
        max_length=10,
        primary_key=True,
        unique=True,
    )
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["code"]
        verbose_name_plural = "Countries"


class Affiliation(models.Model):
    author_id = models.ManyToManyField("authors.Author", blank=True)
    country = models.ForeignKey("misc.Country", on_delete=models.CASCADE, null=True)
    value = models.TextField(blank=True, default="")
    organization = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.value} ({self.organization}) - {self.country.name if self.country else '-'}"


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
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["id"]


class PublicationInfo(models.Model):
    article_id = models.ForeignKey(
        "articles.Article", on_delete=models.CASCADE, related_name="publication_info"
    )
    journal_volume = models.CharField(max_length=255, blank=True, default="")
    journal_title = models.CharField(max_length=255)
    journal_issue = models.CharField(max_length=255, blank=True, default="")
    page_start = models.CharField(blank=True)
    page_end = models.CharField(blank=True)
    artid = models.CharField(max_length=255, blank=True, default="")
    volume_year = models.CharField(max_length=255, blank=True, null=True)
    journal_issue_date = models.DateField(blank=True, null=True)
    publisher = models.ForeignKey("misc.Publisher", on_delete=models.CASCADE)

    class Meta:
        ordering = ["id"]


class License(models.Model):
    url = models.URLField(blank=True, default="")
    name = models.CharField(max_length=255, blank=True, default="")

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["id"]
        unique_together = (("url", "name"),)


class Copyright(models.Model):
    article_id = models.ForeignKey(
        "articles.Article", on_delete=models.CASCADE, related_name="copyright"
    )
    statement = models.CharField(max_length=255, blank=True, default="")
    holder = models.CharField(max_length=255, blank=True, default="")
    year = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ["id"]


class ArxivCategoryType(models.TextChoices):
    QUA223 = ("qua.223",)
    hep_lat = ("hep-lat",)
    math_AG = ("math.AG",)
    nucl_ex = ("nucl-ex",)
    astro_ph_IM = ("astro-ph.IM",)
    math_RT = ("math.RT",)
    math_QA = ("math.QA",)
    math_ph = ("math-ph",)
    cond_mat_mtrl_sci = ("cond-mat.mtrl-sci",)
    astro_ph_GA = ("astro-ph.GA",)
    astro_ph_CO = ("astro-ph.CO",)
    cond_mat_mes_hall = ("cond-mat.mes-hall",)
    math_DG = ("math.DG",)
    cond_mat_soft = ("cond-mat.soft",)
    hep_ex = ("hep-ex",)
    nucl_th = ("nucl-th",)
    math_AT = ("math.AT",)
    math_MP = ("math.MP",)
    cond_mat_stat_mech = ("cond-mat.stat-mech",)
    cond_mat_other = ("cond-mat.other",)
    quant_ph = ("quant-ph",)
    nlin_PS = ("nlin.PS",)
    hep_ph = ("hep-ph",)
    physics_ins_det = ("physics.ins-det",)
    cond_mat_str_el = ("cond-mat.str-el",)
    gr_qc = ("gr-qc",)
    hep_th = ("hep-th",)
    astro_ph_HE = ("astro-ph.HE",)
    cs_LG = ("cs.LG",)
    astro_ph_SR = ("astro-ph.SR",)


class ArticleArxivCategory(models.Model):
    article_id = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="article_arxiv_category",
    )
    category = models.CharField(
        max_length=255,
        choices=ArxivCategoryType.choices,
    )
    primary = models.BooleanField()

    class Meta:
        ordering = ["id"]


class ExperimentalCollaboration(models.Model):
    article_id = models.ManyToManyField("articles.Article", blank=True)
    name = models.TextField(blank=True, default="")

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
