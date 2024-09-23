from django.contrib import admin

from scoap3.authors.models import Author, AuthorIdentifier
from scoap3.misc.models import Affiliation


class AuthorAffiliationInline(admin.StackedInline):
    model = Affiliation.author_id.through
    extra = 0


class AuthorIdentifierInline(admin.StackedInline):
    model = AuthorIdentifier
    extra = 0


class AuthorAdmin(admin.ModelAdmin):
    list_display = ["id", "article_id", "first_name", "last_name"]
    search_fields = ["article_id"]
    raw_id_fields = ["article_id"]
    fields = [
        "article_id",
        "first_name",
        "last_name",
        "email",
    ]


class AuthorIdentifierIdentifierAdmin(admin.ModelAdmin):
    list_display = ["author_id", "identifier_type", "identifier_value"]
    search_fields = ["author_id"]
    raw_id_fields = ["author_id"]


admin.site.register(Author, AuthorAdmin)
admin.site.register(AuthorIdentifier, AuthorIdentifierIdentifierAdmin)
