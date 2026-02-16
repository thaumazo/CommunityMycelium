"""
Form token utilities to prevent duplicate form submissions.
Similar to CSRF tokens but specifically for preventing form resubmission.
"""
import secrets
from functools import wraps
from django.shortcuts import render
from django.contrib import messages


def generate_form_token():
    """Generate a unique token for form submission."""
    return secrets.token_urlsafe(32)


def get_form_token(request, form_name):
    """
    Get or create a form token for the given form name.
    
    Args:
        request: Django request object
        form_name: Unique identifier for the form (e.g., 'project_create')
    
    Returns:
        str: The form token
    """
    session_key = f'form_token_{form_name}'
    
    if session_key not in request.session:
        request.session[session_key] = generate_form_token()
    
    return request.session[session_key]


def validate_form_token(request, form_name):
    """
    Validate and consume a form token.
    
    Args:
        request: Django request object
        form_name: Unique identifier for the form
    
    Returns:
        bool: True if token is valid, False otherwise
    """
    session_key = f'form_token_{form_name}'
    submitted_token = request.POST.get('form_token')
    expected_token = request.session.get(session_key)
    
    # Token must exist and match
    if not submitted_token or not expected_token or submitted_token != expected_token:
        return False
    
    # Consume the token (one-time use)
    del request.session[session_key]
    
    return True


def require_form_token(form_name):
    """
    Decorator to require and validate form tokens on POST requests.
    
    Usage:
        @login_required
        @require_form_token('project_create')
        def project_create_view(request):
            # ... your view code
    
    Args:
        form_name: Unique identifier for the form
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if request.method == 'POST':
                if not validate_form_token(request, form_name):
                    messages.error(
                        request, 
                        "This form has already been submitted. Please don't use the back button after submitting."
                    )
                    # Regenerate token for the form
                    token = generate_form_token()
                    request.session[f'form_token_{form_name}'] = token
                    
                    # Call the view with GET method behavior to show the form again
                    get_request = request
                    get_request.method = 'GET'
                    return view_func(get_request, *args, **kwargs)
            else:
                # For GET requests, generate token and add to context
                token = get_form_token(request, form_name)
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


def inject_form_token(context, request, form_name):
    """
    Helper to inject form token into template context.
    
    Usage in view:
        context = {'form': form}
        inject_form_token(context, request, 'project_create')
        return render(request, 'template.html', context)
    
    Args:
        context: Template context dictionary
        request: Django request object
        form_name: Unique identifier for the form
    """
    context['form_token'] = get_form_token(request, form_name)
    context['form_token_field'] = f'<input type="hidden" name="form_token" value="{context["form_token"]}">'
    return context
