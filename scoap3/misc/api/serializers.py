from rest_framework import serializers

from scoap3.misc.models import (
    Affiliation,
    ArticleArxivCategory,
    Copyright,
    Country,
    ExperimentalCollaboration,
    Funder,
    InstitutionIdentifier,
    InstitutionIdentifierType,
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
    ror = serializers.SerializerMethodField()

    class Meta:
        model = Affiliation
        fields = "__all__"

    def get_ror(self, obj):
        if obj.institutionidentifier_set.filter(
            identifier_type=InstitutionIdentifierType.ROR
        ).exists():
            return (
                obj.institutionidentifier_set.filter(
                    identifier_type=InstitutionIdentifierType.ROR
                )
                .values_list("identifier_value", flat=True)
                .first()
            )
        else:
            return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation.get("ror") is None:
            representation.pop("ror", None)

        return representation


class InstitutionIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionIdentifier
        fields = "__all__"


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = [
            "name",
        ]


class PublicationInfoSerializer(serializers.ModelSerializer):
    publisher = serializers.SerializerMethodField()

    class Meta:
        model = PublicationInfo
        fields = "__all__"

    def get_publisher(self, obj):
        return obj.publisher.name


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = "__all__"


class CopyrightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Copyright
        fields = ["statement", "holder", "year"]


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
