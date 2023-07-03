from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import GenericViewSet

from scoap3.misc.api.serializers import (
    AffiliationSerializer,
    ArticleArxivCategorySerializer,
    CopyrightSerializer,
    CountrySerializer,
    ExperimentalCollaborationSerializer,
    FunderSerializer,
    InstitutionIdentifierSerializer,
    LicenseSerializer,
    PublicationInfoSerializer,
    PublisherSerializer,
    RelatedMaterialSerializer,
)
from scoap3.misc.models import (
    Affiliation,
    ArticleArxivCategory,
    Copyright,
    Country,
    ExperimentalCollaboration,
    Funder,
    InstitutionIdentifier,
    License,
    PublicationInfo,
    Publisher,
    RelatedMaterial,
)


class CountryViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AffiliationViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Affiliation.objects.all()
    serializer_class = AffiliationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class InstitutionIdentifierViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = InstitutionIdentifier.objects.all()
    serializer_class = InstitutionIdentifierSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PublisherViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PublicationInfoViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = PublicationInfo.objects.all()
    serializer_class = PublicationInfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class LicenseViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CopyrightViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Copyright.objects.all()
    serializer_class = CopyrightSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ArticleArxivCategoryViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = ArticleArxivCategory.objects.all()
    serializer_class = ArticleArxivCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ExperimentalCollaborationViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = ExperimentalCollaboration.objects.all()
    serializer_class = ExperimentalCollaborationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FunderViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Funder.objects.all()
    serializer_class = FunderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class RelatedMaterialViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = RelatedMaterial.objects.all()
    serializer_class = RelatedMaterialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
