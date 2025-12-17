"""
Google Drive and YouTube API integration utilities.

Provides OAuth flow and API access for:
- Google Drive: Read transcripts, manage permissions, create documents
- YouTube: Access video metadata, update privacy settings
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from django.conf import settings
from cryptography.fernet import Fernet
import io
import json


# OAuth 2.0 scopes needed for Drive and YouTube
SCOPES = [
    'https://www.googleapis.com/auth/drive',  # Full Drive access
    'https://www.googleapis.com/auth/youtube',  # YouTube access
]


def get_encryption_key():
    """Get or create encryption key for OAuth tokens."""
    # In production, store this in environment variable
    # For now, generate a key (you'll need to save this somewhere secure)
    key = settings.GOOGLE_OAUTH_ENCRYPTION_KEY
    return Fernet(key.encode())


def encrypt_token(token):
    """Encrypt an OAuth token for storage."""
    f = get_encryption_key()
    return f.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token):
    """Decrypt a stored OAuth token."""
    f = get_encryption_key()
    return f.decrypt(encrypted_token.encode()).decode()


def get_oauth_flow(redirect_uri):
    """
    Create OAuth flow for Google authentication.
    
    Args:
        redirect_uri: URL to redirect to after OAuth
        
    Returns:
        Flow object configured for Google OAuth
    """
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )


def get_drive_service(user):
    """
    Get authenticated Google Drive API service for a user.
    
    Args:
        user: User model instance with google_auth relationship
        
    Returns:
        Google Drive API service object
        
    Raises:
        ValueError: If user hasn't connected Google account
    """
    if not hasattr(user, 'google_auth'):
        raise ValueError("User has not connected Google account")
    
    google_auth = user.google_auth
    
    # Decrypt tokens
    access_token = decrypt_token(google_auth.access_token)
    refresh_token = decrypt_token(google_auth.refresh_token) if google_auth.refresh_token else None
    
    # Create credentials object
    credentials = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
        scopes=google_auth.scopes.split()
    )
    
    # Build and return Drive service
    return build('drive', 'v3', credentials=credentials)


def list_folder_files(user, folder_id, mime_type=None):
    """
    List files in a Google Drive folder.
    
    Args:
        user: User model instance
        folder_id: Google Drive folder ID
        mime_type: Optional filter by MIME type (e.g., 'text/plain')
        
    Returns:
        List of file dictionaries with id, name, mimeType, etc.
    """
    service = get_drive_service(user)
    
    query = f"'{folder_id}' in parents and trashed=false"
    if mime_type:
        query += f" and mimeType='{mime_type}'"
    
    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType, modifiedTime, size)",
        orderBy="modifiedTime desc"
    ).execute()
    
    return results.get('files', [])


def download_file_content(user, file_id):
    """
    Download content of a Google Drive file.
    
    Args:
        user: User model instance
        file_id: Google Drive file ID
        
    Returns:
        File content as string
    """
    service = get_drive_service(user)
    
    request = service.files().get_media(fileId=file_id)
    file_buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(file_buffer, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    file_buffer.seek(0)
    return file_buffer.read().decode('utf-8')


def grant_file_permission(user, file_id, email, role='reader'):
    """
    Grant a user permission to access a Google Drive file.
    
    Args:
        user: User model instance (file owner)
        file_id: Google Drive file ID
        email: Email address of user to grant access
        role: 'reader', 'writer', or 'commenter'
        
    Returns:
        Permission ID
    """
    service = get_drive_service(user)
    
    permission = {
        'type': 'user',
        'role': role,
        'emailAddress': email
    }
    
    result = service.permissions().create(
        fileId=file_id,
        body=permission,
        fields='id'
    ).execute()
    
    return result.get('id')


def revoke_file_permission(user, file_id, permission_id):
    """
    Revoke a user's permission to access a Google Drive file.
    
    Args:
        user: User model instance (file owner)
        file_id: Google Drive file ID
        permission_id: ID of permission to revoke
    """
    service = get_drive_service(user)
    
    service.permissions().delete(
        fileId=file_id,
        permissionId=permission_id
    ).execute()


def create_google_doc(user, title, content='', folder_id=None):
    """
    Create a new Google Doc.
    
    Args:
        user: User model instance
        title: Document title
        content: Initial text content
        folder_id: Optional folder ID to create document in
        
    Returns:
        Dictionary with file ID and web view link
    """
    service = get_drive_service(user)
    
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.document'
    }
    
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    file = service.files().create(
        body=file_metadata,
        fields='id, webViewLink'
    ).execute()
    
    # If content provided, insert it using Google Docs API
    if content:
        docs_service = build('docs', 'v1', credentials=service._http.credentials)
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            }
        ]
        docs_service.documents().batchUpdate(
            documentId=file['id'],
            body={'requests': requests}
        ).execute()
    
    return {
        'id': file['id'],
        'url': file['webViewLink']
    }


def get_youtube_service(user):
    """
    Get authenticated YouTube Data API service for a user.
    
    Args:
        user: User model instance with google_auth relationship
        
    Returns:
        YouTube API service object
    """
    if not hasattr(user, 'google_auth'):
        raise ValueError("User has not connected Google account")
    
    google_auth = user.google_auth
    
    # Decrypt tokens
    access_token = decrypt_token(google_auth.access_token)
    refresh_token = decrypt_token(google_auth.refresh_token) if google_auth.refresh_token else None
    
    # Create credentials object
    credentials = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
        scopes=google_auth.scopes.split()
    )
    
    # Build and return YouTube service
    return build('youtube', 'v3', credentials=credentials)


def get_video_details(user, video_id):
    """
    Get YouTube video details.
    
    Args:
        user: User model instance
        video_id: YouTube video ID
        
    Returns:
        Dictionary with video title, description, privacy status, etc.
    """
    service = get_youtube_service(user)
    
    response = service.videos().list(
        part='snippet,status',
        id=video_id
    ).execute()
    
    if not response.get('items'):
        return None
    
    video = response['items'][0]
    return {
        'title': video['snippet']['title'],
        'description': video['snippet']['description'],
        'privacy': video['status']['privacyStatus'],
        'published_at': video['snippet']['publishedAt']
    }


def update_video_privacy(user, video_id, privacy_status):
    """
    Update YouTube video privacy setting.
    
    Args:
        user: User model instance (video owner)
        video_id: YouTube video ID
        privacy_status: 'public', 'unlisted', or 'private'
        
    Returns:
        Updated video details
    """
    service = get_youtube_service(user)
    
    response = service.videos().update(
        part='status',
        body={
            'id': video_id,
            'status': {
                'privacyStatus': privacy_status
            }
        }
    ).execute()
    
    return response
