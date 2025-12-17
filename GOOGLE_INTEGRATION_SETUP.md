# Google Drive & YouTube Integration Setup

## Overview

This integration allows users to:
- Connect their Google account via OAuth 2.0
- Access Google Drive folders containing meeting transcripts
- Automatically grant meeting attendees access to transcript files
- Create summary documents in Google Drive
- Link YouTube videos to meetings
- (Future) Update YouTube video privacy settings

## Prerequisites

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Note your Project ID

### 2. Enable Required APIs

In the Google Cloud Console:
1. Navigate to "APIs & Services" > "Library"
2. Enable the following APIs:
   - **Google Drive API**
   - **YouTube Data API v3**
   - **Google Docs API** (optional, for creating formatted documents)

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (or Internal if using Google Workspace)
3. Fill in required fields:
   - App name: "Community Mycelium"
   - User support email: your email
   - Developer contact: your email
4. Add scopes:
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/youtube`
5. Add test users (if in testing mode)
6. Save and continue

### 4. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. Application type: "Web application"
4. Name: "Community Mycelium Web Client"
5. Authorized redirect URIs:
   - For local: `http://localhost:8000/users/google/auth/callback/`
   - For production: `https://yourdomain.com/users/google/auth/callback/`
6. Click "Create"
7. **Save the Client ID and Client Secret**

### 5. Generate Encryption Key

The encryption key is used to securely store OAuth tokens in the database.

Run this in Python:
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

Copy the output - this is your encryption key.

## Environment Configuration

Add these variables to your `.env` file:

```bash
# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-here
GOOGLE_OAUTH_ENCRYPTION_KEY=your-generated-fernet-key-here
```

**SECURITY IMPORTANT:**
- Never commit these values to git
- Use different credentials for development and production
- Keep the encryption key secret - if it's compromised, regenerate and re-authenticate all users

## Installation

1. Install required Python packages:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Usage

### For Users

1. **Connect Google Account:**
   - Go to your profile
   - Click "Connect Google Account"
   - Authorize the requested permissions
   - You'll be redirected back to your profile

2. **Create Meeting with Drive Transcript:**
   - Create/edit a meeting
   - Enter the Google Drive folder ID in "Transcript Folder ID"
   - Or paste the full Google Drive URL in "Transcript URL"

3. **Browse Drive Files:**
   - Visit `/users/google/drive/browse/`
   - Navigate through your Google Drive
   - Copy folder IDs or file URLs for meetings

### For Developers

**List transcripts in a folder:**
```python
from apps.utils.google_integration import list_folder_files

files = list_folder_files(user, folder_id='your-folder-id')
for file in files:
    print(f"{file['name']} - {file['id']}")
```

**Download a transcript:**
```python
from apps.utils.google_integration import download_file_content

content = download_file_content(user, file_id='your-file-id')
print(content)
```

**Grant access to a transcript:**
```python
from apps.utils.google_integration import grant_file_permission

permission_id = grant_file_permission(
    user=meeting_creator,
    file_id='transcript-file-id',
    email='attendee@example.com',
    role='reader'  # or 'writer', 'commenter'
)
```

**Create a summary document:**
```python
from apps.utils.google_integration import create_google_doc

doc = create_google_doc(
    user=request.user,
    title='Meeting Summary - Dec 15, 2024',
    content='# Summary\n\nKey points:\n- ...',
    folder_id='same-folder-as-transcript'
)

print(f"Created doc: {doc['url']}")
```

## API Quotas & Limits

### Google Drive API
- 20,000 queries per 100 seconds per project
- 20,000 queries per 100 seconds per user
- Generally very generous for typical usage

### YouTube Data API
- 10,000 quota units per day per project
- Reading operations: 1-50 units
- Writing operations: 50 units
- Update video: 50 units

**Note:** If you hit quota limits, request an increase in Google Cloud Console.

## Security Considerations

1. **Token Storage:** OAuth tokens are encrypted using Fernet symmetric encryption before storing in database

2. **Token Refresh:** Access tokens expire after ~1 hour. The integration automatically uses refresh tokens to get new access tokens.

3. **Scope Minimization:** Only request scopes you actually need. Current scopes:
   - `drive`: Full Drive access (read, write, permissions)
   - `youtube`: YouTube video management

4. **HTTPS Required:** OAuth requires HTTPS in production. Use `http://localhost` only for development.

5. **Credential Rotation:** Periodically rotate your OAuth client secret in Google Cloud Console.

## Troubleshooting

### "User has not connected Google account"
- User needs to visit "Connect Google Account" in their profile
- Check that `UserGoogleAuth` record exists for the user

### "Access blocked: This app's request is invalid"
- Redirect URI doesn't match what's configured in Google Cloud Console
- Check spelling and include trailing slash

### "Token has been expired or revoked"
- User needs to re-authenticate
- Delete `UserGoogleAuth` record and reconnect

### "Insufficient Permission"
- User didn't grant all required scopes
- Disconnect and reconnect, making sure to grant all permissions

### "File not found"
- User doesn't have access to the file/folder
- Check folder ID is correct
- Ensure file hasn't been deleted

## Future Enhancements

- [ ] Automatic transcript import when meeting is created
- [ ] Real-time transcript analysis and summarization
- [ ] Automated privacy setting updates for YouTube videos
- [ ] Meeting agenda document generation
- [ ] Action item extraction from transcripts
- [ ] Integration with meeting attendee notification system
