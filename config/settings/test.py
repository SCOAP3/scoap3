"""
With these settings, tests run faster.
"""

from .base import *  # noqa
from config.settings.base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="wpQt7H4zQGseXwknqw5RFWSpBXxKwr3FqavY6iEzFMmRLlUJWJ8U3eftfJlh88Ie",
)
ALLOWED_HOSTS = ["127.0.0.1"]


# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# DEBUGGING FOR TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["debug"] = True  # type: ignore # noqa: F405

# Opensearch
# ------------------------------------------------------------------------------
# Name of the Opensearch index
OPENSEARCH_INDEX_NAMES = {
    "scoap3.articles.documents": "scoap3-backend-test-articles",
}
# Force an index refresh with every save.
OPENSEARCH_DSL_AUTO_REFRESH = True

OPENSEARCH_DSL = {
    "default": {
        "hosts": [env("OPENSEARCH_HOST")],
        "use_ssl": False,
        "verify_certs": False,
        "timeout": 30,
    },
}
