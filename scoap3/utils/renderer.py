from rest_framework_csv.renderers import CSVRenderer


class ArticleCSVRenderer(CSVRenderer):
    header = [
        "id",
        "title",
        "doi",
        "arxiv_id",
        "arxiv_primary_category",
        "journal",
        "publication_date",
        "_created_at",
    ]

    labels = {
        "id": "ID",
        "title": "Title",
        "doi": "DOI",
        "arxiv_id": "arXiv id",
        "arxiv_primary_category": "arXiv primary category",
        "journal": "Journal",
        "publication_date": "Publication Date",
        "_created_at": "Record creation date",
    }

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if "results" in data:
            modified_data = data.get("results", [])
        else:
            modified_data = data
        return super().render(modified_data, accepted_media_type, renderer_context)
