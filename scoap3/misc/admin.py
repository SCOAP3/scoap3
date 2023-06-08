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
    pass


class ArticleArxivCategoryAdmin(admin.ModelAdmin):
    pass


class CopyrightAdmin(admin.ModelAdmin):
    pass


class CountryAdmin(admin.ModelAdmin):
    pass


class ExperimentalCollaborationAdmin(admin.ModelAdmin):
    pass


class FunderAdmin(admin.ModelAdmin):
    pass


class InstitutionIdentifierAdmin(admin.ModelAdmin):
    pass


class LicenseAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "url"]
    search_fields = ["name"]


class PublicationInfoAdmin(admin.ModelAdmin):
    pass


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
