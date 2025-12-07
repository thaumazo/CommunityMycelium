from django.conf import settings


def registration_mode(request):
    """Make REGISTRATION_MODE setting available in all templates."""
    mode = getattr(settings, 'REGISTRATION_MODE', 'open')
    print(f"DEBUG: REGISTRATION_MODE = {mode}")  # Debug line
    return {
        'REGISTRATION_MODE': mode,
    }
