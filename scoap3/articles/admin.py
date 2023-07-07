from django.contrib import admin

from scoap3.articles.models import Article, ArticleFile, ArticleIdentifier


class ArticleAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "subtitle", "_updated_at", "_created_at"]
    search_fields = ["title"]


class ArticleIdentifierAdmin(admin.ModelAdmin):
    list_display = ["article_id", "identifier_type", "identifier_value"]
    search_fields = ["article_id"]
    raw_id_fields = ["article_id"]


class ArticleFileAdmin(admin.ModelAdmin):
    list_display = ["id", "article_id", "file", "file_size", "updated", "created"]
    search_fields = ["article_id"]

    @admin.display(description="Size (bytes)")
    def file_size(self, obj):
        file_size = obj.file.size
        return f"{file_size}"


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleIdentifier, ArticleIdentifierAdmin)
admin.site.register(ArticleFile, ArticleFileAdmin)
