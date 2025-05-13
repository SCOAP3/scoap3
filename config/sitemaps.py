from django.contrib.sitemaps import Sitemap

from scoap3.articles.models import Article


class ArticleSitemap(Sitemap):
    limit = 10000

    def items(self):
        return Article.objects.filter()

    def lastmod(self, obj):
        return obj._updated_at

    def location(self, obj):
        return f"/records/{obj.id}/"
