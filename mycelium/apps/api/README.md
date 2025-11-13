# Django REST API for Unity Integration

This API provides authentication and data access endpoints for Unity applications to interact with the CommunityMycelium Django backend.

## Base URL

```
Local: http://localhost:8000/api/
Production: https://your-domain.com/api/
```

## Authentication

The API uses **JWT (JSON Web Token)** authentication. All protected endpoints require a valid access token in the Authorization header.

### Authentication Flow

1. **Login** or **Register** to get tokens
2. Store the `access` and `refresh` tokens securely in Unity
3. Include the access token in all API requests
4. Refresh the access token when it expires

## API Endpoints

### Authentication Endpoints

#### 1. Login
**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_admin": false
  }
}
```

#### 2. Register
**Endpoint:** `POST /api/auth/register/`

**Request:**
```json
{
  "username": "janedoe",
  "email": "jane@example.com",
  "full_name": "Jane Doe",
  "password": "securepassword123",
  "confirm_password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "message": "User created successfully",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 2,
    "username": "janedoe",
    "email": "jane@example.com",
    "full_name": "Jane Doe"
  }
}
```

#### 3. Refresh Token
**Endpoint:** `POST /api/auth/refresh/`

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 4. Logout
**Endpoint:** `POST /api/auth/logout/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

#### 5. Get Current User
**Endpoint:** `GET /api/auth/me/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "user_location": "Seattle, WA",
  "invited_by": null,
  "user_bioregions": [1, 2],
  "user_communities": [3],
  "user_relationships": [],
  "user_socialroles": [1, 4],
  "user_metacrisis_facets": [],
  "user_maladaptives": [],
  "linked_in": "https://linkedin.com/in/johndoe",
  "view_members": true,
  "view_public": false,
  "date_joined": "2025-01-15T10:30:00Z",
  "last_login": "2025-11-12T14:20:00Z",
  "user_bioregions_detail": [
    {"id": 1, "name": "Cascadia"},
    {"id": 2, "name": "Pacific Northwest"}
  ],
  "user_communities_detail": [
    {"id": 3, "name": "Seattle Community"}
  ],
  "invited_by_detail": null
}
```

### User Endpoints

#### 1. List Users
**Endpoint:** `GET /api/users/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Query Parameters:**
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of results per page (default: 100)

**Response (200 OK):**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "user_location": "Seattle, WA",
      "invited_by": null,
      "user_bioregions": [1, 2],
      "user_communities": [3],
      "user_relationships": [],
      "user_socialroles": [1, 4],
      "user_metacrisis_facets": [],
      "user_maladaptives": [],
      "linked_in": "https://linkedin.com/in/johndoe",
      "view_members": true,
      "view_public": false,
      "date_joined": "2025-01-15T10:30:00Z",
      "last_login": "2025-11-12T14:20:00Z"
    }
  ]
}
```

#### 2. Get User Details
**Endpoint:** `GET /api/users/{id}/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (200 OK):**
Returns detailed user information (same as `/api/auth/me/`)

#### 3. Create User (Admin Only)
**Endpoint:** `POST /api/users/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Request:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "full_name": "New User",
  "password": "securepassword123",
  "confirm_password": "securepassword123"
}
```

#### 4. Update User
**Endpoint:** `PUT /api/users/{id}/` or `PATCH /api/users/{id}/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Request (Partial Update):**
```json
{
  "user_location": "Portland, OR",
  "user_communities": [3, 5]
}
```

#### 5. Delete User
**Endpoint:** `DELETE /api/users/{id}/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (204 No Content)**

## Authorization & Permissions

The API respects the existing ACL (Access Control List) permission system:

1. **Object Ownership**: Users can always access objects they created
2. **Group Permissions**: Users inherit permissions from their groups (Admin, etc.)
3. **Object-Level Permissions**: Specific permissions granted to users for specific objects
4. **Public Access**: Users with `view_members=True` or `view_public=True` are visible to all authenticated users

## Error Responses

### 400 Bad Request
```json
{
  "error": "Please provide both username and password"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Token Lifetime

- **Access Token**: 1 hour
- **Refresh Token**: 7 days (rotates on refresh)

## Unity Integration Example

See the Unity C# example code in the accompanying documentation for implementation details.

### Basic Flow in Unity:

1. **Login**: POST to `/api/auth/login/` with credentials
2. **Store Tokens**: Save `access` and `refresh` tokens securely
3. **Make Requests**: Include `Authorization: Bearer {access_token}` header
4. **Handle Expiry**: When access token expires, use refresh token to get new one
5. **Logout**: POST to `/api/auth/logout/` and clear stored tokens

## CORS Configuration

For Unity WebGL builds, you may need to configure CORS in Django settings. Add the following to `settings.py`:

```python
INSTALLED_APPS += ['corsheaders']

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... other middleware
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Unity WebGL development
    "https://your-unity-build-domain.com",
]
```

## Next Steps

1. Install the required packages if not already installed
2. Run migrations: `python manage.py migrate`
3. Start the development server: `python manage.py runserver`
4. Test the API endpoints using tools like Postman or curl
5. Implement the Unity client code

## Security Recommendations

1. **Always use HTTPS** in production
2. **Never commit** SECRET_KEY to version control
3. **Implement rate limiting** to prevent abuse
4. **Enable token blacklisting** for logout (configure in settings)
5. **Validate all input** on both client and server
6. **Use environment variables** for sensitive configuration
