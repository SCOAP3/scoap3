from django.db import models


class AffiliationExportModel(models.Model):
    country_code = models.CharField(max_length=2, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Affiliation Export"
        app_label = "exports"
        managed = False


class AuthorExportModel(models.Model):
    country_code = models.CharField(max_length=2, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Author Export"
        app_label = "exports"
        managed = False
