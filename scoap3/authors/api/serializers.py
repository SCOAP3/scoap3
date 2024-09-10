from rest_framework import serializers

from scoap3.authors.models import Author, AuthorIdentifier, AuthorIdentifierType
from scoap3.misc.api.serializers import AffiliationSerializer


class AuthorIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorIdentifier
        fields = "__all__"


class AuthorSerializer(serializers.ModelSerializer):
    affiliations = AffiliationSerializer(many=True, read_only=True)
    orcid = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = "__all__"

    def get_orcid(self, obj):
        return {
            orcid
            for orcid in obj.identifiers.filter(
                identifier_type=AuthorIdentifierType.ORCID
            )
            .values_list("identifier_value", flat=True)
            .all()
        }
