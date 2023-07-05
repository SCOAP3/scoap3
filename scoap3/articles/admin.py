from django.contrib import admin

from scoap3.articles.models import Article, ArticleIdentifier


class ArticleAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "subtitle", "_updated_at", "_created_at"]
    search_fields = ["title"]


class ArticleIdentifierAdmin(admin.ModelAdmin):
    list_display = ["article_id", "identifier_type", "identifier_value"]
    search_fields = ["article_id"]
    raw_id_fields = ["article_id"]


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleIdentifier, ArticleIdentifierAdmin)
