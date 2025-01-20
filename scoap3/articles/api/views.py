from django_elasticsearch_dsl_drf.constants import LOOKUP_FILTER_RANGE, LOOKUP_QUERY_IN
from django_elasticsearch_dsl_drf.filter_backends import (
    DefaultOrderingFilterBackend,
    FacetedSearchFilterBackend,
    FilteringFilterBackend,
    OrderingFilterBackend,
    SearchFilterBackend,
    SimpleQueryStringSearchFilterBackend,
    SourceBackend
)
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet
from opensearch_dsl import DateHistogramFacet, TermsFacet
from rest_framework import status
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
from rest_framework.viewsets import GenericViewSet, ViewSet

from scoap3.articles.api.serializers import (
    ArticleDocumentSerializer,
    ArticleFileSerializer,
    ArticleIdentifierSerializer,
    ArticleSerializer,
    LegacyArticleSerializer,
    SearchCSVSerializer,
)
from scoap3.articles.documents import ArticleDocument
from scoap3.articles.models import Article, ArticleFile, ArticleIdentifier
from scoap3.tasks import import_to_scoap3
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
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = request.data

        article_id = data.get("id")
        if Article.objects.filter(id=article_id).exists():
            return Response(
                {"error": "ID already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save(id=article_id)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class RecordViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    serializer_class = LegacyArticleSerializer
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]


class ArticleWorkflowImportView(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        try:
            article = import_to_scoap3(data, True)
        except Exception as e:
            error_msg = str(e)
            return Response({"message": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = ArticleSerializer(article)
            return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleDocumentView(BaseDocumentViewSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search = self.search.extra(track_total_hits=True)

    document = ArticleDocument
    serializer_class = ArticleDocumentSerializer
    filter_backends = [
        SearchFilterBackend,
        FacetedSearchFilterBackend,
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SimpleQueryStringSearchFilterBackend,
        SourceBackend,
    ]
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [ArticleCSVRenderer]

    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = OSStandardResultsSetPagination

    search_fields = (
        "title",
        "id",
        "doi",
        "authors.first_name",
        "authors.last_name",
        "article_identifiers.identifier_value",
    )

    ordering_fields = {"publication_date": "publication_date"}
    ordering = ["-publication_date"]

    filter_fields = {
        "publication_year": {
            "field": "publication_date",
            "lookups": [LOOKUP_FILTER_RANGE, LOOKUP_QUERY_IN, "lte", "gte"],
        },
        "journal": {
            "field": "publication_info.journal_title",
            "lookups": [
                LOOKUP_QUERY_IN,
            ],
        },
        "country": "authors.affiliations.country.name",
        "first_name": "authors.first_name",
        "last_name": "authors.last_name",
        "doi": "doi",
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
            "options": {
                "size": 15,
                "order": {
                    "_key": "asc",
                },
            },
        },
        "country": {
            "field": "authors.affiliations.country.name",
            "facet": TermsFacet,
            "enabled": True,
            "options": {
                "size": 300,
                "order": {
                    "_key": "asc",
                },
            },
        },
    }

    def get_queryset(self):
        get_all = self.request.query_params.get("all", "false").lower() == "true"
        search = super().get_queryset()

        if get_all and self.request.user.is_staff:
            search = search.extra(size=10000)

        return search

    def list(self, request, *args, **kwargs):
        get_all = request.query_params.get("all", "false").lower() == "true"

        if get_all and self.request.user.is_staff:
            self.pagination_class = None

        return super().list(request, *args, **kwargs)

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
