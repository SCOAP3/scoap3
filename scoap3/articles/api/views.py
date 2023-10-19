from django_elasticsearch_dsl_drf.constants import LOOKUP_FILTER_RANGE, LOOKUP_QUERY_IN
from django_elasticsearch_dsl_drf.filter_backends import (
    FacetedSearchFilterBackend,
    FilteringFilterBackend,
    SearchFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet
from opensearch_dsl import DateHistogramFacet, TermsFacet
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet

from scoap3.articles.api.serializers import (
    ArticleDocumentSerializer,
    ArticleFileSerializer,
    ArticleIdentifierSerializer,
    ArticleSerializer,
    SearchCSVSerializer,
)
from scoap3.articles.documents import ArticleDocument
from scoap3.articles.models import Article, ArticleFile, ArticleIdentifier
from scoap3.utils.pagination import OSStandardResultsSetPagination
from scoap3.utils.renderer import ArticleCSVRenderer


class ArticleViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = request.data
        article_id = data.get("id")

        if Article.objects.filter(id=article_id).exists():
            return Response({"error": "ID already exists"}, status=400)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save(id=article_id)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


class ArticleDocumentView(BaseDocumentViewSet):
    document = ArticleDocument
    serializer_class = ArticleDocumentSerializer
    filter_backends = [
        SearchFilterBackend,
        FacetedSearchFilterBackend,
        FilteringFilterBackend,
    ]
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [ArticleCSVRenderer]

    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = OSStandardResultsSetPagination

    search_fields = ("title", "id")

    filter_fields = {
        "publication_year": {
            "field": "publication_date",
            "lookups": [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
            ],
        },
        "journal": {
            "field": "publication_info.journal_title",
            "lookups": [
                LOOKUP_QUERY_IN,
            ],
        },
        "country": "authors.affiliations.country.name",
    }

    faceted_search_fields = {
        "publication_year": {
            "field": "publication_date",
            "facet": DateHistogramFacet,
            "options": {
                "interval": "year",
            },
            "enabled": True,
        },
        "journal": {
            "field": "publication_info.journal_title",
            "facet": TermsFacet,
            "enabled": True,
        },
        "country": {
            "field": "authors.affiliations.country.name",
            "facet": TermsFacet,
            "enabled": True,
        },
    }

    def get_serializer_class(self):
        requested_renderer_format = self.request.accepted_media_type
        if "text/csv" in requested_renderer_format:
            return SearchCSVSerializer
        return ArticleDocumentSerializer


class ArticleIdentifierViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = ArticleIdentifier.objects.all()
    serializer_class = ArticleIdentifierSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ArticleFileViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = ArticleFile.objects.all()
    serializer_class = ArticleFileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
