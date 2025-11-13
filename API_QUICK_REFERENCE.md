# Quick Reference: Unity-Django API

## Django Server Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Test API setup
python manage.py shell < test_api.py
```

## API Endpoints Quick Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/login/` | POST | No | Login, get tokens |
| `/api/auth/register/` | POST | No | Register new user |
| `/api/auth/refresh/` | POST | No* | Refresh access token |
| `/api/auth/logout/` | POST | Yes | Logout, blacklist token |
| `/api/auth/me/` | GET | Yes | Get current user |
| `/api/users/` | GET | Yes | List users (ACL filtered) |
| `/api/users/{id}/` | GET | Yes | Get user details |
| `/api/users/` | POST | Yes | Create user |
| `/api/users/{id}/` | PUT/PATCH | Yes | Update user |
| `/api/users/{id}/` | DELETE | Yes | Delete user |

*Requires refresh token in body

## curl Examples

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}'
```

### Get Current User
```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### List Users
```bash
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"YOUR_REFRESH_TOKEN"}'
```

## Unity Quick Start

### 1. Add UnityAPIManager to Scene
```csharp
// Create empty GameObject, add UnityAPIManager component
```

### 2. Login
```csharp
UnityAPIManager.Instance.Login(username, password,
    onSuccess: (user) => Debug.Log($"Welcome {user.full_name}!"),
    onError: (error) => Debug.LogError(error)
);
```

### 3. Check Authentication
```csharp
if (UnityAPIManager.Instance.IsAuthenticated())
{
    // User is logged in
}
```

### 4. Get Data
```csharp
UnityAPIManager.Instance.Get<UserData>("auth/me/",
    onSuccess: (user) => { /* use user data */ },
    onError: (error) => { /* handle error */ }
);
```

### 5. Logout
```csharp
UnityAPIManager.Instance.Logout(
    onSuccess: () => Debug.Log("Logged out")
);
```

## Response Examples

### Login Response
```json
{
  "refresh": "eyJ0eXAiOiJKV1Qi...",
  "access": "eyJ0eXAiOiJKV1Qi...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_admin": false
  }
}
```

### User List Response
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "johndoe",
      "full_name": "John Doe",
      "email": "john@example.com",
      "user_location": "Seattle",
      "view_members": true,
      "view_public": false
    }
  ]
}
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Import errors | Run `pip install -r requirements.txt` |
| 401 Unauthorized | Token expired, refresh or login again |
| 403 Forbidden | User lacks permission for this action |
| Connection refused | Django server not running |
| CORS error | Add `django-cors-headers` for WebGL |

## Token Lifetimes

- **Access Token**: 1 hour
- **Refresh Token**: 7 days
- Auto-refresh on 401 (APIManager handles this)

## Configuration Files

- API settings: `mycelium/config/settings.py`
- API routes: `mycelium/config/urls.py`
- API views: `mycelium/apps/api/views.py`
- Unity manager: `UnityAPIManager.cs`

## HTTP Status Codes

- 200 OK - Success
- 201 Created - Resource created
- 204 No Content - Success, no response body
- 400 Bad Request - Invalid data
- 401 Unauthorized - Not authenticated
- 403 Forbidden - No permission
- 404 Not Found - Resource doesn't exist
- 500 Server Error - Django error

## Security Checklist

Development:
- ✅ JWT tokens
- ✅ Password hashing
- ✅ ACL permissions
- ✅ Token expiration

Production:
- [ ] HTTPS only
- [ ] Rate limiting
- [ ] Token blacklisting
- [ ] CORS configuration
- [ ] Secure token storage
- [ ] Environment variables

## Unity Data Models

All request/response classes must be properly serializable with `[System.Serializable]` attribute:

```csharp
[System.Serializable]
public class UserData
{
    public int id;
    public string username;
    public string email;
    public string full_name;
    public string user_location;
    public bool view_members;
    public bool view_public;
    public bool is_admin;
}

[System.Serializable]
public class LoginRequest
{
    public string username;
    public string password;
}

[System.Serializable]
public class LoginResponse
{
    public string access;
    public string refresh;
    public UserData user;
}

[System.Serializable]
public class UserListResponse
{
    public int count;
    public string next;
    public string previous;
    public UserData[] results;
}
```

**Important:** Unity's `JsonUtility` requires proper serializable classes. Do NOT use anonymous objects like `new { username = "test" }` - they won't serialize correctly and will cause 400 Bad Request errors.

## Adding New Endpoints

1. Create serializer in `apps/api/serializers.py`
2. Create viewset in `apps/api/views.py`
3. Register in `apps/api/urls.py`

Example:
```python
# Serializer
class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = '__all__'

# ViewSet
class CommunityViewSet(viewsets.ModelViewSet):
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated, ACLPermission]
    queryset = Community.objects.all()

# Router
router.register(r'communities', CommunityViewSet)
```

## Documentation Links

- API Docs: `apps/api/README.md`
- Setup Guide: `DJANGO_API_SETUP.md`
- Integration Guide: `UNITY_DJANGO_INTEGRATION.md`
- DRF Docs: https://www.django-rest-framework.org/
- JWT Docs: https://django-rest-framework-simplejwt.readthedocs.io/
