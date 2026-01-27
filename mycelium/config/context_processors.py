from django.conf import settings


def site_settings(request):
    """
    Add site-wide settings to the template context.
    """
    return {
        'URL_OVERRIDE': settings.URL_OVERRIDE,
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
    }
