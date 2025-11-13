"""
Test script for API endpoints.
Run this with: python manage.py shell < test_api.py

Or manually in Django shell to verify API setup.
"""

from django.contrib.auth import get_user_model
from apps.api.serializers import UserSerializer, UserCreateSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

print("=" * 50)
print("API Setup Test")
print("=" * 50)

# Test 1: Check if we can import all necessary modules
print("\n✓ All API modules imported successfully")

# Test 2: Check serializers
print("\n✓ Serializers are available:")
print(f"  - UserSerializer: {UserSerializer}")
print(f"  - UserCreateSerializer: {UserCreateSerializer}")

# Test 3: Check if we can create tokens
try:
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_api_user',
        defaults={
            'email': 'test@example.com',
            'full_name': 'Test API User'
        }
    )
    if created:
        user.set_password('testpassword123')
        user.save()
        print(f"\n✓ Created test user: {user.username}")
    else:
        print(f"\n✓ Test user already exists: {user.username}")
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    print(f"\n✓ JWT tokens generated successfully:")
    print(f"  - Access token (first 20 chars): {access_token[:20]}...")
    print(f"  - Refresh token (first 20 chars): {refresh_token[:20]}...")
    
except Exception as e:
    print(f"\n✗ Error generating tokens: {e}")

# Test 4: Serialize a user
try:
    serializer = UserSerializer(user)
    print(f"\n✓ User serialization successful:")
    print(f"  - User ID: {serializer.data['id']}")
    print(f"  - Username: {serializer.data['username']}")
    print(f"  - Email: {serializer.data['email']}")
except Exception as e:
    print(f"\n✗ Error serializing user: {e}")

print("\n" + "=" * 50)
print("Setup complete! You can now:")
print("1. Run: python manage.py runserver")
print("2. Test API at: http://localhost:8000/api/")
print("3. Login endpoint: http://localhost:8000/api/auth/login/")
print("4. Use the Unity code to connect your application")
print("=" * 50)
