from django.contrib import admin

from scoap3.misc.models import (
    Affiliation,
    ArticleArxivCategory,
    Copyright,
    Country,
    ExperimentalCollaboration,
    Funder,
    InstitutionIdentifier,
    License,
    PublicationInfo,
    Publisher,
    RelatedMaterial,
)


class AffiliationAdmin(admin.ModelAdmin):
    list_display = ["country", "value", "organization"]
    search_fields = ["value"]
    raw_id_fields = ["author_id"]


class ArticleArxivCategoryAdmin(admin.ModelAdmin):
    list_display = ["article_id", "category", "primary"]
    search_fields = ["category"]
    raw_id_fields = ["article_id"]


class CopyrightAdmin(admin.ModelAdmin):
    list_display = ["article_id", "statement", "holder", "year"]
    search_fields = ["statement"]
    raw_id_fields = ["article_id"]


class CountryAdmin(admin.ModelAdmin):
    list_display = ["code", "name"]
    search_fields = ["name"]


class ExperimentalCollaborationAdmin(admin.ModelAdmin):
    list_display = ["name", "experimental_collaboration_order"]
    search_fields = ["name"]
    raw_id_fields = ["article_id"]


class FunderAdmin(admin.ModelAdmin):
    pass


class InstitutionIdentifierAdmin(admin.ModelAdmin):
    pass


class LicenseAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "url"]
    search_fields = ["name"]


class PublicationInfoAdmin(admin.ModelAdmin):
    list_display = ["article_id", "journal_title", "volume_year", "publisher"]
    search_fields = ["journal_title"]
    raw_id_fields = ["article_id"]


class PublisherAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


class RelatedMaterialAdmin(admin.ModelAdmin):
    pass


admin.site.register(Affiliation, AffiliationAdmin)
admin.site.register(ArticleArxivCategory, ArticleArxivCategoryAdmin)
admin.site.register(Copyright, CopyrightAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(ExperimentalCollaboration, ExperimentalCollaborationAdmin)
admin.site.register(Funder, FunderAdmin)
admin.site.register(InstitutionIdentifier, InstitutionIdentifierAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(PublicationInfo, PublicationInfoAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(RelatedMaterial, RelatedMaterialAdmin)
