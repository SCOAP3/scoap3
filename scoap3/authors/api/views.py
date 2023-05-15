from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from scoap3.authors.api.serializers import AuthorIdentifierSerializer, AuthorSerializer
from scoap3.authors.models import Author, AuthorIdentifier


class AuthorViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class AuthorIdentifierViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = AuthorIdentifier.objects.all()
    serializer_class = AuthorIdentifierSerializer
