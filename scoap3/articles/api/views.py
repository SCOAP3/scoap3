from datetime import datetime, timedelta

from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_RANGE,
    LOOKUP_QUERY_CONTAINS,
    LOOKUP_QUERY_IN,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    DefaultOrderingFilterBackend,
    FacetedSearchFilterBackend,
    FilteringFilterBackend,
    OrderingFilterBackend,
    SearchFilterBackend,
    SimpleQueryStringSearchFilterBackend,
    SourceBackend,
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
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet, ViewSet

from scoap3.articles.api.serializers import (
    ArticleDocumentSerializer,
    ArticleFileSerializer,
    ArticleIdentifierSerializer,
    ArticleSerializer,
    LegacyArticleDocumentSerializer,
    LegacyArticleSerializer,
    SearchCSVSerializer,
)
from scoap3.articles.documents import ArticleDocument
from scoap3.articles.models import Article, ArticleFile, ArticleIdentifier
from scoap3.articles.permissions import IsSuperUserOrReadOnly
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
    permission_classes = [IsSuperUserOrReadOnly]

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


class RecordViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = LegacyArticleSerializer
    queryset = Article.objects.all()
    permission_classes = [IsSuperUserOrReadOnly]


class ArticleWorkflowImportView(ViewSet):
    permission_classes = [IsSuperUserOrReadOnly]

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

    permission_classes = [IsSuperUserOrReadOnly]
    pagination_class = OSStandardResultsSetPagination

    search_fields = (
        "title",
        "id",
        "doi",
        "authors.name",
        "authors.first_name",
        "authors.last_name",
        "article_identifiers.identifier_value",
    )

    ordering_fields = {
        "publication_date": "publication_date",
        "_updated_at": "_updated_at",
    }
    ordering = ["-publication_date", "-_updated_at"]

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
        "ror": "authors.affiliations.ror",
        "affiliation": "authors.affiliations.value",
        "name": {
            "field": "authors.name",
            "lookups": [LOOKUP_QUERY_CONTAINS],
        },
        "first_name": {
            "field": "authors.first_name",
            "lookups": [LOOKUP_QUERY_CONTAINS],
        },
        "last_name": {
            "field": "authors.last_name",
            "lookups": [LOOKUP_QUERY_CONTAINS],
        },
        "orcid": "author.orcid",
        "doi": "doi",
    }

    faceted_search_fields = {
        "publication_year": {
            "field": "publication_date.keyword",
            "facet": DateHistogramFacet,
            "options": {
                "interval": "year",
            },
            "enabled": True,
        },
        "journal": {
            "field": "publication_info.journal_title.keyword",
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
            "field": "authors.affiliations.country.name.keyword",
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
    permission_classes = [IsSuperUserOrReadOnly]


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
    permission_classes = [IsSuperUserOrReadOnly]


class LegacyArticleDocumentView(BaseDocumentViewSet):
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
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    permission_classes = [IsSuperUserOrReadOnly]
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

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data).data

            return Response(
                {
                    "count": paginated_response["count"],
                    "next": paginated_response["next"],
                    "previous": paginated_response["previous"],
                    "hits": {"hits": paginated_response["results"]},
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response({"hits": {"hits": serializer.data}})

    def get_serializer_class(self):
        return LegacyArticleDocumentSerializer


class ArticleStatsViewSet(ViewSet):
    permission_classes = [IsSuperUserOrReadOnly]

    def list(self, request):
        today = datetime.now().date()

        date_ranges = {
            "yesterday": {
                "gte": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "lte": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
            },
            "last_30_days": {
                "gte": (today - timedelta(days=30)).strftime("%Y-%m-%d"),
                "lte": today.strftime("%Y-%m-%d"),
            },
            "this_year": {
                "gte": today.replace(month=1, day=1).strftime("%Y-%m-%d"),
                "lte": today.strftime("%Y-%m-%d"),
            },
        }

        other_data = {}
        for key, range_values in date_ranges.items():
            search_query = ArticleDocument.search().query(
                "range", publication_date=range_values
            )
            count = search_query.count()
            other_data[key] = count

        journal_search = ArticleDocument.search().extra(track_total_hits=True)
        other_data["all"] = journal_search.count()
        journal_search.aggs.bucket(
            "journals", "terms", field="publication_info.journal_title", size=100
        )
        journals_result = journal_search.execute()
        journal_buckets = journals_result.aggregations.journals.buckets
        journals_data = {bucket.key: bucket.doc_count for bucket in journal_buckets}

        data = {
            "other": other_data,
            "journals": journals_data,
        }
        return Response(data)
