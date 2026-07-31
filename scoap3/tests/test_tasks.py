from unittest.mock import patch

import pytest
from django.core.files.storage import default_storage
from django.test import TestCase

from scoap3.tasks import fetch_file_and_save_to_s3


@pytest.mark.vcr
class TestFetchFileAndSaveToS3(TestCase):
    """Integration tests for the content-type resolution added to fix #532.

    Each test replays a recorded HTTP response (via vcrpy) through the real
    fetch/save flow, and inspects the ``content_type`` that ends up set on
    the file object handed to storage - this is the attribute django-storages
    uses to set the S3 object's ``Content-Type`` header.
    """

    def _save_and_get_content_type(self, url, s3_path):
        with patch.object(
            default_storage, "save", wraps=default_storage.save
        ) as save_spy:
            result_url = fetch_file_and_save_to_s3(url, s3_path)

        assert result_url is not None
        saved_content = save_spy.call_args.args[1]
        return saved_content.content_type

    def test_uses_content_type_returned_by_server(self):
        content_type = self._save_and_get_content_type(
            "https://example.org/files/article.xml", "articles/article.xml"
        )
        assert content_type == "text/xml"

    def test_falls_back_to_mimetypes_guess_when_server_returns_octet_stream(self):
        content_type = self._save_and_get_content_type(
            "https://example.org/files/article.pdf", "articles/article.pdf"
        )
        assert content_type == "application/pdf"

    def test_falls_back_to_hardcoded_pdf_default_for_pdfa_extension(self):
        # ".pdfa" isn't recognised by Python's mimetypes module, so this
        # exercises the explicit fallback branch rather than the guess.
        content_type = self._save_and_get_content_type(
            "https://example.org/files/article.pdfa", "articles/article.pdfa"
        )
        assert content_type == "application/pdf"

    def test_falls_back_to_binary_octet_stream_for_unknown_extension(self):
        content_type = self._save_and_get_content_type(
            "https://example.org/files/article.foobar", "articles/article.foobar"
        )
        assert content_type == "binary/octet-stream"
