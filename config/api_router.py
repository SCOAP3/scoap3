from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from scoap3.articles.api.views import (
    ArticleFileViewSet,
    ArticleIdentifierViewSet,
    ArticleStatsViewSet,
    ArticleViewSet,
    ArticleWorkflowImportView,
    LegacyArticleDocumentView,
    RecordViewSet,
)
from scoap3.authors.api.views import AuthorIdentifierViewSet, AuthorViewSet
from scoap3.misc.api.views import (
    AffiliationViewSet,
    ArticleArxivCategoryViewSet,
    CopyrightViewSet,
    CountryViewSet,
    ExperimentalCollaborationViewSet,
    FunderViewSet,
    InstitutionIdentifierViewSet,
    LicenseViewSet,
    PublicationInfoViewSet,
    PublisherViewSet,
    RelatedMaterialViewSet,
)
from scoap3.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)

# Articles
router.register("articles", ArticleViewSet)
router.register("article-identifier", ArticleIdentifierViewSet)
router.register("article-file", ArticleFileViewSet)
router.register("article-stats", ArticleStatsViewSet, basename="article-stats")
router.register(
    "article-workflow-import",
    ArticleWorkflowImportView,
    basename="article-workflow-import",
)

# Records
router.register("records", LegacyArticleDocumentView, basename="records-list")

# Authors
router.register("author", AuthorViewSet)
router.register("author-identifier", AuthorIdentifierViewSet)

# Misc
router.register("country", CountryViewSet)
router.register("affiliation", AffiliationViewSet)
router.register("institution-identifier", InstitutionIdentifierViewSet)
router.register("publisher", PublisherViewSet)
router.register("publication-info", PublicationInfoViewSet)
router.register("license", LicenseViewSet)
router.register("copyright", CopyrightViewSet)
router.register("article-arxiv-category", ArticleArxivCategoryViewSet)
router.register("experimental-collaboration", ExperimentalCollaborationViewSet)
router.register("funder", FunderViewSet)
router.register("related-material", RelatedMaterialViewSet)

app_name = "api"

urlpatterns = [
    path(
        "records/<int:pk>/",
        RecordViewSet.as_view({"get": "retrieve"}),
        name="records-detail",
    ),
]

urlpatterns += router.urls
