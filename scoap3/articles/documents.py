from django.conf import settings
from django_opensearch_dsl import Document, fields
from django_opensearch_dsl.registries import registry

from .models import Article, ArticleFile


@registry.register_document
class ArticleDocument(Document):
    id = fields.IntegerField()
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

    _updated_at = fields.DateField()

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
