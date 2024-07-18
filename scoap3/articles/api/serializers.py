from datetime import datetime

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers

from scoap3.articles.documents import ArticleDocument
from scoap3.articles.models import (
    Article,
    ArticleFile,
    ArticleIdentifier,
    ArticleIdentifierType,
)
from scoap3.misc.api.serializers import (
    ArticleArxivCategorySerializer,
    CopyrightSerializer,
    PublicationInfoSerializer,
)


class ArticleFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleFile
        fields = "__all__"


class ArticleIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleIdentifier
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    related_files = ArticleFileSerializer(many=True, read_only=True)
    article_identifiers = ArticleIdentifierSerializer(many=True, read_only=True)
    article_arxiv_category = ArticleArxivCategorySerializer(many=True, read_only=True)
    publication_info = PublicationInfoSerializer(many=True, read_only=True)
    copyright = CopyrightSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.publication_date is None:
            representation["publication_date"] = instance._created_at
        return representation


class ArticleDocumentSerializer(DocumentSerializer):
    class Meta:
        document = ArticleDocument
        fields = "__all__"


class SearchCSVSerializer(DocumentSerializer):
    _created_at = serializers.SerializerMethodField()
    doi = serializers.SerializerMethodField()
    arxiv_id = serializers.SerializerMethodField()
    arxiv_primary_category = serializers.SerializerMethodField()
    journal = serializers.SerializerMethodField()

    def get__created_at(self, obj):
        return datetime.strptime(obj._created_at, "%Y-%m-%dT%H:%M:%S.%f%z").date()

    def get_doi(self, obj):
        for article_identifier in obj.article_identifiers:
            if article_identifier.identifier_type == ArticleIdentifierType.DOI:
                return article_identifier.identifier_value

    def get_arxiv_id(self, obj):
        for article_identifier in obj.article_identifiers:
            if article_identifier.identifier_type == ArticleIdentifierType.ARXIV:
                return article_identifier.identifier_value

    def get_arxiv_primary_category(self, obj):
        for arxiv_category in obj.article_arxiv_category:
            if arxiv_category.primary:
                return arxiv_category.category

    def get_journal(self, obj):
        for publication_info in obj.publication_info:
            return publication_info.journal_title

    class Meta:
        document = ArticleDocument
        fields = [
            "id",
            "title",
            "doi",
            "arxiv_id",
            "arxiv_primary_category",
            "journal",
            "publication_date",
            "_created_at",
        ]
