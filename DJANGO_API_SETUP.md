# Django REST API Setup Guide

## Installation & Setup Complete! ✅

The Django REST Framework with JWT authentication has been successfully configured for your CommunityMycelium project.

## What Was Added

### 1. **Dependencies** (already in requirements.txt)
- `djangorestframework` - REST API framework
- `djangorestframework-simplejwt` - JWT authentication

### 2. **New App: `apps.api`**

Created a new Django app with the following structure:

```
apps/api/
├── __init__.py
├── apps.py
├── permissions.py      # ACL-integrated permissions
├── serializers.py      # User data serializers
├── views.py           # API endpoints and viewsets
├── urls.py            # API URL routing
├── README.md          # API documentation
└── UnityAPIManager.cs # Unity C# integration code
```

### 3. **Settings Configuration**

Added to `config/settings.py`:
- REST Framework configuration
- JWT token settings (1-hour access, 7-day refresh)
- Authentication classes

### 4. **URL Routes**

Added API routes to `config/urls.py` at `/api/`

## Available API Endpoints

### Authentication
- `POST /api/auth/login/` - Login with username/password
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/logout/` - Logout (blacklist token)
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/me/` - Get current user info

### Users
- `GET /api/users/` - List users (with ACL filtering)
- `GET /api/users/{id}/` - Get user details
- `POST /api/users/` - Create user (admin only)
- `PUT/PATCH /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

## Next Steps

### 1. Install Dependencies (if not already installed)

```bash
cd mycelium
pip install -r ../requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Create a Superuser (if needed)

```bash
python manage.py createsuperuser
```

### 4. Start Development Server

```bash
python manage.py runserver
```

### 5. Test the API

#### Using curl:

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Get current user (replace YOUR_ACCESS_TOKEN)
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Using Python requests:

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login/', json={
    'username': 'your_username',
    'password': 'your_password'
})
tokens = response.json()
access_token = tokens['access']

# Get users
response = requests.get('http://localhost:8000/api/users/', 
    headers={'Authorization': f'Bearer {access_token}'})
users = response.json()
```

#### Using the Browsable API:

1. Open browser to: http://localhost:8000/api/
2. Login with your credentials (session auth is enabled)
3. Browse the interactive API documentation

## Unity Integration

### 1. Copy the Unity Script

Copy `apps/api/UnityAPIManager.cs` to your Unity project's Scripts folder.

### 2. Create an Empty GameObject

1. Create a new Empty GameObject in your scene
2. Name it "APIManager" or "UnityAPIManager"
3. Add the `UnityAPIManager` component to it

### 3. Update API Base URL

In `UnityAPIManager.cs`, change the API_BASE_URL:

```csharp
// For local testing
private const string API_BASE_URL = "http://localhost:8000/api";

// For production
private const string API_BASE_URL = "https://your-domain.com/api";
```

### 4. Example Usage in Unity

```csharp
public class LoginController : MonoBehaviour
{
    public void OnLoginClick(string username, string password)
    {
        UnityAPIManager.Instance.Login(username, password,
            onSuccess: (user) => {
                Debug.Log($"Welcome {user.full_name}!");
                // Navigate to main scene
            },
            onError: (error) => {
                Debug.LogError($"Login failed: {error}");
                // Show error to user
            }
        );
    }
}
```

## Security Considerations

### For Development:
✅ Currently configured for local development
✅ Session authentication enabled for browsable API
✅ JWT tokens with 1-hour expiration

### For Production:
⚠️ **Important:** Before deploying to production:

1. **HTTPS Only**: Set up SSL/TLS certificates
2. **Environment Variables**: Move SECRET_KEY to environment
3. **CORS Configuration**: Add `django-cors-headers` if needed for WebGL
4. **Token Blacklisting**: Enable token blacklisting in JWT settings
5. **Rate Limiting**: Add rate limiting to prevent brute force attacks
6. **Secure Token Storage**: In Unity, use encrypted storage for tokens

### Enable CORS for Unity WebGL (if needed):

```bash
pip install django-cors-headers
```

Add to `settings.py`:
```python
INSTALLED_APPS += ['corsheaders']

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... rest of middleware
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-unity-webgl-domain.com",
]
```

## Permission System

The API integrates with your existing ACL system:

- **Object Ownership**: Users can access their own created objects
- **Group Permissions**: Permissions inherited from user groups
- **Object-Level Permissions**: Fine-grained access control
- **Public/Member Visibility**: Respects `view_members` and `view_public` flags

All API endpoints automatically enforce these permissions through the `ACLPermission` class.

## Troubleshooting

### Issue: "Import rest_framework could not be resolved"
**Solution**: The linter error is expected if packages aren't installed yet. Run:
```bash
pip install djangorestframework djangorestframework-simplejwt
```

### Issue: "No module named 'apps.api'"
**Solution**: Make sure you've run the Django server at least once, or create migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: Unity can't connect to API
**Solution**: 
- Check if Django server is running
- Verify API_BASE_URL in Unity matches your Django server
- Check for CORS errors in browser console (for WebGL)
- Ensure firewall allows connections

### Issue: 400 Bad Request from Unity
**Solution**:
- The `UnityAPIManager.cs` script has been updated to use proper serializable classes
- If you modified the script, ensure you're NOT using anonymous objects like `new { username = "test" }`
- Use proper `[System.Serializable]` classes for all requests (LoginRequest, LogoutRequest, etc.)
- Check Unity console for the exact JSON being sent and Django's error response

### Issue: 401 Unauthorized errors
**Solution**:
- Check if access token is expired (refresh it)
- Verify Authorization header format: `Bearer {token}`
- Ensure user is logged in

## Testing the Setup

Run the test script:

```bash
cd mycelium
python manage.py shell < test_api.py
```

This will verify:
- All modules are imported correctly
- Serializers work
- JWT tokens can be generated
- User serialization functions

## Documentation

- **API Reference**: See `apps/api/README.md`
- **Unity Integration**: See `apps/api/UnityAPIManager.cs`
- **DRF Documentation**: https://www.django-rest-framework.org/
- **SimpleJWT Documentation**: https://django-rest-framework-simplejwt.readthedocs.io/

## What's Next?

1. **Test the endpoints** using Postman, curl, or the browsable API
2. **Implement Unity login UI** using the provided APIManager
3. **Add more endpoints** for Communities, Projects, etc.
4. **Set up CORS** if using Unity WebGL builds
5. **Configure production settings** when ready to deploy

## Need More Endpoints?

The current setup includes User endpoints. To add more (Communities, Projects, etc.), follow this pattern:

1. Create serializers in `apps/api/serializers.py`
2. Create viewsets in `apps/api/views.py`
3. Register routes in `apps/api/urls.py`

Example for Communities:

```python
# serializers.py
class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = '__all__'

# views.py
class CommunityViewSet(viewsets.ModelViewSet):
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated, ACLPermission]
    
    def get_queryset(self):
        return get_permitted_objects(self.request.user, "view", Community)

# urls.py
router.register(r'communities', CommunityViewSet, basename='community')
```

Happy coding! 🚀
