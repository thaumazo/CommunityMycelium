"""
Views for Google OAuth integration.
"""

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from apps.users.models import UserGoogleAuth
from apps.utils.google_integration import (
    get_oauth_flow, encrypt_token, get_drive_service,
    list_folder_files, download_file_content
)
from datetime import datetime, timedelta


@login_required
def google_auth_start(request):
    """
    Start Google OAuth flow.
    """
    redirect_uri = request.build_absolute_uri(reverse('google_auth_callback'))
    flow = get_oauth_flow(redirect_uri)
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # Force consent to get refresh token
    )
    
    # Store state in session for verification
    request.session['google_oauth_state'] = state
    
    return redirect(authorization_url)


@login_required
def google_auth_callback(request):
    """
    Handle Google OAuth callback.
    """
    import os
    
    # Allow insecure transport for local development
    if request.get_host().startswith('localhost') or request.get_host().startswith('127.0.0.1'):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    state = request.session.get('google_oauth_state')
    
    if not state:
        messages.error(request, "Invalid OAuth state")
        return redirect('user_detail', pk=request.user.pk)
    
    redirect_uri = request.build_absolute_uri(reverse('google_auth_callback'))
    flow = get_oauth_flow(redirect_uri)
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    
    credentials = flow.credentials
    
    # Calculate token expiry
    expiry = None
    if credentials.expiry:
        expiry = credentials.expiry
    elif credentials.expires_in:
        expiry = datetime.now() + timedelta(seconds=credentials.expires_in)
    
    # Store or update credentials
    UserGoogleAuth.objects.update_or_create(
        user=request.user,
        defaults={
            'access_token': encrypt_token(credentials.token),
            'refresh_token': encrypt_token(credentials.refresh_token) if credentials.refresh_token else None,
            'token_expiry': expiry,
            'scopes': ' '.join(credentials.scopes)
        }
    )
    
    messages.success(request, "Successfully connected your Google account!")
    return redirect('user_detail', pk=request.user.pk)


@login_required
def google_auth_disconnect(request):
    """
    Disconnect Google account.
    """
    if request.method == 'POST':
        UserGoogleAuth.objects.filter(user=request.user).delete()
        messages.success(request, "Google account disconnected")
    
    return redirect('user_detail', pk=request.user.pk)


@login_required
def google_drive_browser(request):
    """
    Browse Google Drive folders and files.
    """
    if not hasattr(request.user, 'google_auth'):
        messages.error(request, "Please connect your Google account first")
        return redirect('google_auth_start')
    
    folder_id = request.GET.get('folder_id', 'root')
    
    try:
        service = get_drive_service(request.user)
        
        # Get folder metadata
        if folder_id != 'root':
            folder = service.files().get(
                fileId=folder_id,
                fields='id, name'
            ).execute()
            folder_name = folder['name']
        else:
            folder_name = 'My Drive'
        
        # List files in folder
        files = list_folder_files(request.user, folder_id)
        
        context = {
            'folder_id': folder_id,
            'folder_name': folder_name,
            'files': files
        }
        
        return render(request, 'users/google_drive_browser.html', context)
        
    except Exception as e:
        messages.error(request, f"Error accessing Google Drive: {e}")
        return redirect('user_detail', pk=request.user.pk)
