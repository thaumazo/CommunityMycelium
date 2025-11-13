from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q

from apps.acl.utils import get_permitted_objects
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
)
from .permissions import ACLPermission

User = get_user_model()


# Authentication endpoints
@api_view(["POST"])
@permission_classes([AllowAny])
def api_login(request):
    """
    API endpoint for user login.
    Returns JWT tokens on successful authentication.
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Please provide both username and password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    # Generate tokens
    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_admin": user.is_admin(),
            },
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def api_register(request):
    """
    API endpoint for user registration.
    Creates a new user and returns JWT tokens.
    """
    serializer = UserCreateSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "User created successfully",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """
    API endpoint for user logout.
    Blacklists the refresh token (if blacklisting is enabled).
    """
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_user_me(request):
    """
    Get the current authenticated user's information.
    """
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data)


# User ViewSet
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations.
    Respects ACL permissions.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ACLPermission]

    def get_queryset(self):
        """
        Return users based on ACL permissions.
        """
        user = self.request.user

        # Get users the current user has permission to view
        permitted_users = get_permitted_objects(user, "view", User)

        # Include users with view_members or view_public set to True
        additional_users = User.objects.filter(Q(view_members=True) | Q(view_public=True))

        # Combine both querysets and ensure no duplicates
        users = permitted_users | additional_users
        return users.distinct()

    def get_serializer_class(self):
        """
        Use detailed serializer for retrieve action.
        """
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        """
        Set created_by when creating a user.
        """
        serializer.save()
