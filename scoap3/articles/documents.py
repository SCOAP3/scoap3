from django.conf import settings
from django_opensearch_dsl import Document, fields
from django_opensearch_dsl.registries import registry

from scoap3.misc.models import ArticleArxivCategory, PublicationInfo

from .models import Article, ArticleFile, ArticleIdentifier


@registry.register_document
class ArticleDocument(Document):
    id = fields.TextField()
    reception_date = fields.DateField()
    acceptance_date = fields.DateField()
    publication_date = fields.DateField()
    first_online_date = fields.DateField()
    abstract = fields.TextField()
    related_licenses = fields.NestedField(
        properties={
            "url": fields.TextField(),
            "name": fields.TextField(),
        }
    )
    related_materials = fields.NestedField(
        properties={
            "title": fields.TextField(),
            "doi": fields.TextField(),
            "related_material_type": fields.TextField(),
        }
    )
    related_files = fields.NestedField(
        properties={
            "file": fields.TextField(),
            "created": fields.DateField(),
            "updated": fields.DateField(),
        }
    )
    article_identifiers = fields.NestedField(
        properties={
            "identifier_type": fields.TextField(),
            "identifier_value": fields.TextField(),
        }
    )

    article_arxiv_category = fields.NestedField(
        properties={
            "category": fields.TextField(),
            "primary": fields.BooleanField(),
        }
    )

    publication_info = fields.NestedField(
        properties={
            "journal_volume": fields.TextField(),
            "journal_title": fields.TextField(),
            "page_start": fields.TextField(),
            "page_end": fields.TextField(),
            "artid": fields.TextField(),
            "volume_year": fields.TextField(),
            "journal_issue_date": fields.DateField(),
        }
    )

    _updated_at = fields.DateField()

    def prepare_article_identifiers(self, instance):
        article_identifiers = ArticleIdentifier.objects.filter(article_id=instance)
        serialized_article_identifiers = []
        for article_identifier in article_identifiers:
            serialized_article_identifier = {
                "identifier_type": article_identifier.identifier_type,
                "identifier_value": article_identifier.identifier_value,
            }
            serialized_article_identifiers.append(serialized_article_identifier)
        return serialized_article_identifiers

    def prepare_related_files(self, instance):
        article_files = ArticleFile.objects.filter(article_id=instance)
        serialized_files = []
        for file in article_files:
            serialized_file = {
                "file": file.file.url,
                "created": file.created,
                "updated": file.updated,
            }
            serialized_files.append(serialized_file)
        return serialized_files

    def prepare_article_arxiv_category(self, instance):
        arxiv_categories = ArticleArxivCategory.objects.filter(article_id=instance)
        serialized_arxiv_categories = []
        for arxiv_category in arxiv_categories:
            serialized_arxiv_category = {
                "category": arxiv_category.category,
                "primary": arxiv_category.primary,
            }
            serialized_arxiv_categories.append(serialized_arxiv_category)
        return serialized_arxiv_categories

    def prepare_publication_info(self, instance):
        publication_infos = PublicationInfo.objects.filter(article_id=instance)
        serialized_publication_infos = []
        for publication_info in publication_infos:
            serialized_publication_info = {
                "journal_volume": publication_info.journal_volume,
                "journal_title": publication_info.journal_title,
                "page_start": publication_info.page_start,
                "page_end": publication_info.page_end,
                "artid": publication_info.artid,
                "volume_year": publication_info.volume_year,
                "journal_issue_date": publication_info.journal_issue_date,
            }
            serialized_publication_infos.append(serialized_publication_info)
        return serialized_publication_infos

    class Index:
        name = f"{settings.OPENSEARCH_INDEX_PREFIX}-articles"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Article
        fields = [
            "title",
            "subtitle",
            "_created_at",
        ]
