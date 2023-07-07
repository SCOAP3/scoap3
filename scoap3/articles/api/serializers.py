from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers

from scoap3.articles.documents import ArticleDocument
from scoap3.articles.models import Article, ArticleFile, ArticleIdentifier


class ArticleFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleFile
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    related_files = ArticleFileSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = "__all__"


class ArticleDocumentSerializer(DocumentSerializer):
    class Meta:
        document = ArticleDocument
        fields = "__all__"


class ArticleIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleIdentifier
        fields = "__all__"
