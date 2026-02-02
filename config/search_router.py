from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from scoap3.articles.api.views import ArticleDocumentView

router = DefaultRouter() if settings.DEBUG else SimpleRouter()


# Articles
router.register("article", ArticleDocumentView, basename="article")

app_name = "search"
urlpatterns = router.urls
