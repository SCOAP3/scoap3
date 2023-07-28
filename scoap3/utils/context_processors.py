from django.conf import settings


def matomo_settings(request):
    return {
        "MATOMO_URL": settings.MATOMO_URL,
        "MATOMO_SITE_ID": settings.MATOMO_SITE_ID,
    }
