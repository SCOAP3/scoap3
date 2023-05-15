from rest_framework import serializers

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


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["code", "name"]


class AffiliationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affiliation
        fields = "__all__"


class InstitutionIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionIdentifier
        fields = "__all__"


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = "__all__"


class PublicationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicationInfo
        fields = "__all__"


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = "__all__"


class CopyrightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Copyright
        fields = "__all__"


class ArticleArxivCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleArxivCategory
        fields = "__all__"


class ExperimentalCollaborationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentalCollaboration
        fields = "__all__"


class FunderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funder
        fields = "__all__"


class RelatedMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatedMaterial
        fields = "__all__"
