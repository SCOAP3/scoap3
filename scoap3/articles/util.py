from datetime import datetime

from scoap3.articles.models import ArticleIdentifierType


def get_first_doi(article_document):
    for identifier in article_document.article_identifiers:
        if identifier.identifier_type == ArticleIdentifierType.DOI.value:
            return identifier.identifier_value
    return None


def get_first_arxiv(article_document):
    for identifier in article_document.article_identifiers:
        if identifier.identifier_type == ArticleIdentifierType.ARXIV.value:
            return identifier.identifier_value
    return None


def get_arxiv_primary_category(article_document):
    for arxiv_category in article_document.article_arxiv_category:
        if arxiv_category.primary:
            return arxiv_category.category


def parse_string_to_date_object(date_string):
    return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
