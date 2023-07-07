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
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from scoap3.articles.api.serializers import (
    ArticleDocumentSerializer,
    ArticleFileSerializer,
    ArticleIdentifierSerializer,
    ArticleSerializer,
)
from scoap3.articles.documents import ArticleDocument
from scoap3.articles.models import Article, ArticleFile, ArticleIdentifier


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


class ArticleDocumentView(DocumentViewSet):
    document = ArticleDocument
    serializer_class = ArticleDocumentSerializer

    filter_backends = [SearchFilterBackend]

    search_fields = ("title",)
    permission_classes = [IsAuthenticatedOrReadOnly]


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
