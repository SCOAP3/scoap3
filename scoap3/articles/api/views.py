from django_elasticsearch_dsl_drf.filter_backends import SearchFilterBackend
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
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
from scoap3.articles.permissions import AdminOrReadOnly
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
    permission_classes = [IsAuthenticatedOrReadOnly, AdminOrReadOnly]


class ArticleDocumentView(DocumentViewSet):
    document = ArticleDocument
    serializer_class = ArticleDocumentSerializer

    filter_backends = [SearchFilterBackend]
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [ArticleCSVRenderer]

    search_fields = ("title", "id")
    permission_classes = [IsAuthenticatedOrReadOnly]

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
