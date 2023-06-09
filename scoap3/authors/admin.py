from django.contrib import admin

from scoap3.authors.models import Author, AuthorIdentifier


class AuthorAdmin(admin.ModelAdmin):
    list_display = ["id", "article_id", "first_name", "last_name"]
    search_fields = ["article_id"]
    raw_id_fields = ["article_id"]


class AuthorIdentifierIdentifierAdmin(admin.ModelAdmin):
    list_display = ["author_id", "identifier_type", "identifier_value"]
    search_fields = ["author_id"]
    raw_id_fields = ["author_id"]


admin.site.register(Author, AuthorAdmin)
admin.site.register(AuthorIdentifier, AuthorIdentifierIdentifierAdmin)
