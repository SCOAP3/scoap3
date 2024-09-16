from rest_framework import serializers

from scoap3.authors.models import Author, AuthorIdentifier
from scoap3.misc.api.serializers import AffiliationSerializer


class AuthorIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorIdentifier
        fields = "__all__"


class AuthorSerializer(serializers.ModelSerializer):
    affiliations = AffiliationSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = "__all__"
