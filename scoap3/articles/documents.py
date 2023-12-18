from django.conf import settings
from django_opensearch_dsl import Document, fields
from django_opensearch_dsl.registries import registry

from scoap3.articles.models import Article, ArticleFile, ArticleIdentifier
from scoap3.authors.models import Author
from scoap3.misc.models import Affiliation, ArticleArxivCategory, PublicationInfo


@registry.register_document
class ArticleDocument(Document):
    settings = {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "max_result_window": 70000,
    }

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

    publication_info = fields.ObjectField(
        properties={
            "journal_volume": fields.TextField(),
            "journal_title": fields.KeywordField(),
            "journal_issue": fields.TextField(),
            "page_start": fields.TextField(),
            "page_end": fields.TextField(),
            "artid": fields.TextField(),
            "volume_year": fields.TextField(),
            "journal_issue_date": fields.DateField(),
            "publisher": fields.KeywordField(),
        }
    )

    copyright = fields.ObjectField(
        properties={
            "statement": fields.TextField(),
            "year": fields.TextField(),
            "holder": fields.TextField(),
        }
    )

    authors = fields.ObjectField(
        properties={
            "first_name": fields.KeywordField(),
            "last_name": fields.KeywordField(),
            "affiliations": fields.ObjectField(
                properties={
                    "value": fields.TextField(),
                    "organization": fields.TextField(),
                    "country": fields.ObjectField(
                        properties={
                            "code": fields.TextField(),
                            "name": fields.KeywordField(),
                        }
                    ),
                }
            ),
        }
    )

    def prepare_authors(self, instance):
        authors = Author.objects.filter(article_id=instance)
        serialized_authors = []
        for author in authors:
            affiliations = Affiliation.objects.filter(author_id=author)
            serialized_affiliations = []
            for affiliation in affiliations:
                serialized_affiliation = {
                    "value": affiliation.value,
                    "organization": affiliation.organization,
                    "country": {
                        "code": affiliation.country.code,
                        "name": affiliation.country.name,
                    },
                }
                serialized_affiliations.append(serialized_affiliation)

            serialized_author = {
                "first_name": author.first_name.strip(),
                "last_name": author.last_name.strip(),
                "affiliations": serialized_affiliations,
            }
            serialized_authors.append(serialized_author)
        return serialized_authors

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
                "journal_issue": publication_info.journal_issue,
                "journal_title": publication_info.journal_title,
                "page_start": publication_info.page_start,
                "page_end": publication_info.page_end,
                "artid": publication_info.artid,
                "volume_year": publication_info.volume_year,
                "journal_issue_date": publication_info.journal_issue_date,
                "publisher": publication_info.publisher.name,
            }
            serialized_publication_infos.append(serialized_publication_info)
        return serialized_publication_infos

    class Index:
        name = settings.OPENSEARCH_INDEX_NAMES[__name__]
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "max_result_window": 70000,
        }

    class Django:
        model = Article
        fields = [
            "title",
            "subtitle",
            "_created_at",
            "_updated_at",
        ]
