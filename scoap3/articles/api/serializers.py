from datetime import datetime

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from drf_queryfields import QueryFieldsMixin
from rest_framework import serializers

from scoap3.articles.documents import ArticleDocument
from scoap3.articles.models import (
    Article,
    ArticleFile,
    ArticleIdentifier,
    ArticleIdentifierType,
)
from scoap3.authors.api.serializers import AuthorSerializer
from scoap3.authors.models import AuthorIdentifierType
from scoap3.misc.api.serializers import (
    ArticleArxivCategorySerializer,
    CopyrightSerializer,
    PublicationInfoSerializer,
)
from scoap3.misc.models import InstitutionIdentifierType


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
    authors = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.publication_date is None:
            representation["publication_date"] = instance._created_at
        if instance.publication_info.exists():
            for pub_info in representation["publication_info"]:
                if pub_info.get("volume_year") is None:
                    pub_info["volume_year"] = instance._created_at.year
        return representation


class LegacyArticleSerializer(serializers.ModelSerializer):
    metadata = serializers.SerializerMethodField()
    updated = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ["id", "metadata", "updated", "created"]

    def get_id(self, obj):
        return obj.id

    def get_metadata(self, obj):
        return {
            "_files": [
                {
                    "filetype": entry.filetype,
                    "size": entry.file.size,
                    "key": entry.file.name,
                }
                for entry in obj.related_files.all()
            ],
            "abstracts": [
                {
                    "source": "".join(
                        [entry.publisher.name for entry in obj.publication_info.all()]
                    ),
                    "value": obj.abstract,
                }
            ],
            "arxiv_eprints": [
                {
                    "categories": {
                        entry.category for entry in obj.article_arxiv_category.all()
                    },
                    "value": {
                        entry.identifier_value
                        for entry in obj.article_identifiers.all()
                    },
                }
            ],
            "authors": [
                {
                    "affiliations": [
                        {
                            "country": affiliation.country.name
                            if affiliation.country
                            else None,
                            "organization": affiliation.organization,
                            "value": affiliation.value,
                            **(
                                {
                                    "ror": affiliation.institutionidentifier_set.filter(
                                        identifier_type=InstitutionIdentifierType.ROR
                                    )
                                    .values_list("identifier_value", flat=True)
                                    .first(),
                                }
                                if affiliation.institutionidentifier_set.filter(
                                    identifier_type=InstitutionIdentifierType.ROR
                                ).exists()
                                else {}
                            ),
                        }
                        for affiliation in entry.affiliations.all()
                    ],
                    "email": entry.email,
                    "full_name": entry.full_name,
                    "given_names": entry.first_name,
                    "surname": entry.last_name,
                    **(
                        {
                            "orcid": entry.identifiers.filter(
                                identifier_type=AuthorIdentifierType.ORCID
                            )
                            .values_list("identifier_value", flat=True)
                            .first()
                        }
                        if entry.identifiers.filter(
                            identifier_type=AuthorIdentifierType.ORCID
                        ).exists()
                        else {}
                    ),
                }
                for entry in obj.authors.all()
            ],
            "collections": [
                {"primary": entry.journal_title} for entry in obj.publication_info.all()
            ],
            "control_number": obj.id,
            "copyright": [
                {
                    "statement": entry.statement,
                    "holder": entry.holder,
                    "year": entry.year,
                }
                for entry in obj.copyright.all()
            ],
            "dois": [
                {"value": entry.identifier_value}
                for entry in obj.article_identifiers.all()
            ],
            "imprints": [
                {
                    "date": entry.journal_issue_date,
                    "publisher": entry.publisher.name,
                }
                for entry in obj.publication_info.all()
            ],
            "license": [
                {
                    "license": entry.name,
                    "url": entry.url,
                }
                for entry in obj.related_licenses.all()
            ],
            "page_nr": [
                int(entry.page_end)
                for entry in obj.publication_info.all()
                if entry.page_end.isdigit()
            ],
            "publication_info": [
                {
                    "artid": entry.artid,
                    "journal_issue": entry.journal_issue,
                    "journal_title": entry.journal_title,
                    "journal_volume": entry.journal_volume,
                    "page_end": entry.page_end,
                    "page_start": entry.page_start,
                    "year": entry.volume_year,
                }
                for entry in obj.publication_info.all()
            ],
            "record_creation_date": obj._created_at,
            "titles": [
                {
                    "source": entry.publisher.name,
                    "title": obj.title,
                }
                for entry in obj.publication_info.all()
            ],
        }

    def get_updated(self, obj):
        return obj._updated_at

    def get_created(self, obj):
        return obj._created_at


class ArticleDocumentSerializer(QueryFieldsMixin, DocumentSerializer):
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
