from rest_framework import serializers

from scoap3.authors.models import Author, AuthorIdentifier


class AuthorIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorIdentifier
        fields = "__all__"


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"
