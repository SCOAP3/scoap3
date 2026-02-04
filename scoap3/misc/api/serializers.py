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
        fields = [
            "ror",
            "value",
            "organization",
            "country",
        ]

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


class InstitutionIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionIdentifier
        fields = [
            "identifier_type",
            "identifier_value",
            "affiliation_id",
        ]


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
        exclude = ["id", "article_id"]

    def get_publisher(self, obj):
        return obj.publisher.name


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        exclude = ["id"]


class CopyrightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Copyright
        fields = ["statement", "holder", "year"]


class ArticleArxivCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleArxivCategory
        exclude = ["id"]


class ExperimentalCollaborationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentalCollaboration
        exclude = ["id"]


class FunderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funder
        exclude = ["id"]


class RelatedMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatedMaterial
        exclude = ["id"]
