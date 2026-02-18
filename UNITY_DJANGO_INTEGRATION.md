# Unity-Django Authentication Integration Summary

## Overview

Your Django REST API is now fully configured for Unity integration with JWT-based authentication that respects your existing ACL (Access Control List) permission system.

## Architecture

```
┌─────────────────────┐
│   Unity Client      │
│   (C# APIManager)   │
└──────────┬──────────┘
           │ HTTPS + JWT Bearer Token
           │
           ├─► POST /api/auth/login/
           ├─► POST /api/auth/register/
           ├─► POST /api/auth/refresh/
           ├─► GET  /api/people/
           └─► GET  /api/people/{id}/
           │
┌──────────▼──────────┐
│  Django REST API    │
│  ┌───────────────┐  │
│  │ JWT Auth      │  │
│  ├───────────────┤  │
│  │ ACL Perms     │◄─┼─ Uses existing permission system
│  ├───────────────┤  │
│  │ Serializers   │  │
│  ├───────────────┤  │
│  │ ViewSets      │  │
│  └───────────────┘  │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   PostgreSQL DB     │
│   - Users           │
│   - Permissions     │
│   - Communities     │
│   - etc.            │
└─────────────────────┘
```

## What Was Implemented

### Django Side ✅

1. **REST Framework Configuration**
   - JWT authentication with 1-hour access tokens
   - 7-day refresh tokens with rotation
   - Session auth for browsable API
   - Pagination (100 items per page)

2. **Custom ACL Integration**
   - `ACLPermission` class that uses your existing `is_permitted()` function
   - Respects object ownership, group permissions, and object-level permissions
   - Filters querysets based on user permissions
   - Honors `view_members` and `view_public` flags

3. **Authentication Endpoints**
   - Login: `POST /api/auth/login/`
   - Register: `POST /api/auth/register/`
   - Logout: `POST /api/auth/logout/`
   - Refresh: `POST /api/auth/refresh/`
   - Get Me: `GET /api/auth/me/`

4. **Person CRUD Endpoints**
   - List: `GET /api/people/`
   - Detail: `GET /api/people/{id}/`
   - Create: `POST /api/people/`
   - Update: `PUT/PATCH /api/people/{id}/`
   - Delete: `DELETE /api/people/{id}/`

5. **Serializers**
   - `UserSerializer` - Basic user data
   - `UserDetailSerializer` - Detailed user with nested relationships
   - `UserCreateSerializer` - User registration with password validation

### Unity Side (Provided) 📦

1. **UnityAPIManager.cs** - Complete Unity integration script
   - Singleton pattern for easy access
   - Token management (storage, refresh, expiration)
   - Login, register, logout methods
   - Generic GET/POST methods with auto-retry on token expiry
   - Event system for UI updates
   - Automatic token refresh on 401 errors
   - **Uses proper serializable classes** (not anonymous objects) for Unity's JsonUtility

2. **Data Models**
   - `UserData` - Matches Django User model
   - `LoginRequest` - Login credentials
   - `LoginResponse` - Login/register response
   - `RegisterRequest` - Registration data
   - `TokenRefreshResponse` - Token refresh response
   - `LogoutRequest` - Logout data
   - `RefreshRequest` - Refresh token data

## Security Features

### Implemented ✅
- JWT token-based authentication
- Password hashing (Django default)
- Token expiration (1 hour for access, 7 days for refresh)
- ACL permission enforcement
- CSRF protection (for web views)
- Session authentication (browsable API only)

### Recommended for Production ⚠️
- [ ] Enable HTTPS only
- [ ] Add rate limiting (django-ratelimit)
- [ ] Enable JWT token blacklisting
- [ ] Configure CORS for WebGL builds
- [ ] Use secure token storage in Unity
- [ ] Add request logging
- [ ] Set up monitoring/alerting
- [ ] Environment-based configuration

## Permission Flow

When Unity requests data:

1. **Request arrives** with JWT token
2. **Token validated** by `JWTAuthentication`
3. **User extracted** from token
4. **ACLPermission checks**:
   - Is user authenticated?
   - Map HTTP method to action (GET→view, POST→add, etc.)
   - Check model-level permission via `is_permitted()`
5. **ViewSet filters queryset**:
   - Call `get_permitted_objects()` for user
   - Add users with `view_members=True` or `view_public=True`
6. **Object-level check** (for detail views):
   - Call `is_permitted()` for specific object
7. **Response returned** with allowed data only

## Example Unity Usage

### Login Flow
```csharp
void OnLoginClick()
{
    UnityAPIManager.Instance.Login(username, password,
        onSuccess: (user) => {
            Debug.Log($"Welcome {user.full_name}!");
            PlayerPrefs.SetInt("user_id", user.id);
            SceneManager.LoadScene("MainMenu");
        },
        onError: (error) => {
            ShowError(error);
        }
    );
}
```

### Load User Data
```csharp
void LoadCurrentUser()
{
    UnityAPIManager.Instance.Get<UserData>("auth/me/",
        onSuccess: (user) => {
            nameText.text = user.full_name;
            emailText.text = user.email;
        },
        onError: (error) => {
            Debug.LogError(error);
        }
    );
}
```

### Load User List
```csharp
[System.Serializable]
public class UserListResponse
{
    public int count;
    public string next;
    public string previous;
    public UserData[] results;
}

void LoadUsers()
{
    UnityAPIManager.Instance.Get<UserListResponse>("people/",
        onSuccess: (response) => {
            foreach (var user in response.results)
            {
                CreateUserCard(user);
            }
        },
        onError: (error) => {
            Debug.LogError(error);
        }
    );
}
```

## Token Management

### Storage
- Unity: `PlayerPrefs` (consider encrypting for production)
- Access token: 1 hour lifetime
- Refresh token: 7 days lifetime, rotates on use

### Refresh Flow
1. Access token expires (1 hour)
2. API returns 401 Unauthorized
3. APIManager automatically calls `/api/auth/refresh/`
4. New access token received
5. Original request retried with new token
6. If refresh fails, user redirected to login

## Testing Checklist

### Django
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Start server: `python manage.py runserver`
- [ ] Test login: `curl -X POST http://localhost:8000/api/auth/login/ -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}'`
- [ ] Test browsable API: http://localhost:8000/api/

### Unity
- [ ] Copy `UnityAPIManager.cs` to Unity project
- [ ] Create APIManager GameObject
- [ ] Update `API_BASE_URL` constant
- [ ] Test login from Unity
- [ ] Test data retrieval
- [ ] Test token refresh
- [ ] Test logout

## Extending the API

To add endpoints for other models (Communities, Projects, etc.):

```python
# apps/api/serializers.py
class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = '__all__'

# apps/api/views.py
class CommunityViewSet(viewsets.ModelViewSet):
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated, ACLPermission]
    
    def get_queryset(self):
        return get_permitted_objects(self.request.user, "view", Community)

# apps/api/urls.py
router.register(r'communities', CommunityViewSet, basename='community')
```

Then in Unity:
```csharp
[System.Serializable]
public class CommunityData
{
    public int id;
    public string name;
    // ... other fields
}

UnityAPIManager.Instance.Get<CommunityData[]>("communities/",
    onSuccess: (communities) => { /* ... */ },
    onError: (error) => { /* ... */ }
);
```

**Important Note:** All data classes in Unity must use the `[System.Serializable]` attribute and have public fields. Unity's `JsonUtility` doesn't support anonymous objects or properties.

## Files Created/Modified

### Created
- `mycelium/apps/api/__init__.py`
- `mycelium/apps/api/apps.py`
- `mycelium/apps/api/permissions.py`
- `mycelium/apps/api/serializers.py`
- `mycelium/apps/api/views.py`
- `mycelium/apps/api/urls.py`
- `mycelium/apps/api/README.md`
- `mycelium/apps/api/UnityAPIManager.cs`
- `mycelium/test_api.py`
- `DJANGO_API_SETUP.md` (this file)

### Modified
- `mycelium/config/settings.py` - Added DRF and JWT configuration
- `mycelium/config/urls.py` - Added API routes

## Next Steps

1. **Test the Django API**
   ```bash
   cd mycelium
   pip install -r ../requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

2. **Test with curl or Postman**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username":"your_user","password":"your_pass"}'
   ```

3. **Integrate with Unity**
   - Copy `UnityAPIManager.cs` to Unity project
   - Create login UI
   - Test authentication flow

4. **Add More Endpoints** (as needed)
   - Communities
   - Projects
   - Meetings
   - etc.

5. **Configure for Production**
   - Set up HTTPS
   - Configure CORS (if using WebGL)
   - Enable rate limiting
   - Set up proper secret management

## Support Resources

- **Django REST Framework**: https://www.django-rest-framework.org/
- **SimpleJWT**: https://django-rest-framework-simplejwt.readthedocs.io/
- **Unity UnityWebRequest**: https://docs.unity3d.com/ScriptReference/Networking.UnityWebRequest.html
- **Your API docs**: `mycelium/apps/api/README.md`

## Questions & Customization

Common customizations:
- **Token lifetime**: Adjust in `settings.py` `SIMPLE_JWT` config
- **Pagination size**: Change `PAGE_SIZE` in `REST_FRAMEWORK` config
- **Add fields to User**: Update `UserSerializer.Meta.fields`
- **Custom permissions**: Extend `ACLPermission` class
- **Add endpoints**: Follow the ViewSet pattern in `views.py`

Your Django backend is now ready for Unity integration! 🎮🐍
