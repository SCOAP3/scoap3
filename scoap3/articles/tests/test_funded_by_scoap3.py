from io import BytesIO

import fitz  # PyMuPDF
import pytest
from django.core.files import File
from django.core.files.base import ContentFile

from scoap3.articles.models import Article, ArticleFile
from scoap3.articles.tasks import check_contains_funded_by_scoap3

pytestmark = pytest.mark.django_db


@pytest.fixture
def create_article(db):
    def _create_article():
        return Article.objects.create(
            title="Test Article",
            subtitle="Subtitle",
            abstract="Abstract",
        )

    return _create_article


@pytest.fixture
def create_pdf_with_text():
    def _create_pdf_with_text(text):
        pdf_bytes = BytesIO()
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), text)
        doc.save(pdf_bytes)
        doc.close()
        pdf_bytes.seek(0)
        return ContentFile(pdf_bytes.read(), "test_file.pdf")

    return _create_pdf_with_text


@pytest.fixture
def attach_file_to_article(db):
    def _attach_file_to_article(article, content, file_name):
        file = File(content, name=file_name)
        ArticleFile.objects.create(article_id=article, file=file)

    return _attach_file_to_article


class TestCheckContainsFundedBySCOAP3:
    def test_contains_funded_by(
        self, create_article, create_pdf_with_text, attach_file_to_article
    ):
        article = create_article()

        file_with_text = create_pdf_with_text("Funded by SCOAP3")
        attach_file_to_article(article, file_with_text, "file_with_text.pdf")

        result, message = check_contains_funded_by_scoap3(article)
        assert result is True
        assert message.startswith("Files contain the required text: 'Funded by SCOAP3'")

    def test_contains_funded_by_multiple_files(
        self, create_article, create_pdf_with_text, attach_file_to_article
    ):
        article = create_article()

        file_with_text_1 = create_pdf_with_text("Funded by SCOAP3")
        file_with_text_2 = create_pdf_with_text(
            "Some other content. Funded by SCOAP3 again."
        )

        attach_file_to_article(article, file_with_text_1, "file_with_text_1.pdf")
        attach_file_to_article(article, file_with_text_2, "file_with_text_2.pdf")

        result, message = check_contains_funded_by_scoap3(article)
        assert result is True
        assert message.startswith("Files contain the required text: 'Funded by SCOAP3'")

    def test_does_not_contain_funded_by(
        self, create_article, create_pdf_with_text, attach_file_to_article
    ):
        article = create_article()

        file_without_text = create_pdf_with_text("Other text")
        attach_file_to_article(article, file_without_text, "file_without_text.pdf")

        result, message = check_contains_funded_by_scoap3(article)
        assert result is False
        assert message == "Files do not contain the required text: 'Funded by SCOAP3'"

    def test_does_not_contain_funded_by_multiple_files(
        self, create_article, create_pdf_with_text, attach_file_to_article
    ):
        article = create_article()

        file_without_text_1 = create_pdf_with_text("This is some random text.")
        file_without_text_2 = create_pdf_with_text("Some other random content.")

        attach_file_to_article(article, file_without_text_1, "file_without_text_1.pdf")
        attach_file_to_article(article, file_without_text_2, "file_without_text_2.pdf")

        result, message = check_contains_funded_by_scoap3(article)
        assert result is False
        assert message == "Files do not contain the required text: 'Funded by SCOAP3'"

    def test_mixed_files(
        self, create_article, create_pdf_with_text, attach_file_to_article
    ):
        article = create_article()

        file_with_text = create_pdf_with_text("Funded by SCOAP3")
        file_without_text = create_pdf_with_text("Other text")
        attach_file_to_article(article, file_with_text, "file_with_text.pdf")
        attach_file_to_article(article, file_without_text, "file_without_text.pdf")

        result, message = check_contains_funded_by_scoap3(article)
        assert result is True
        assert message.startswith("Files contain the required text: 'Funded by SCOAP3'")

    def test_no_files(self, create_article):
        article = create_article()

        result, message = check_contains_funded_by_scoap3(article)
        assert result is False
        assert message == "No files found for the given article."
