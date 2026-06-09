from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q

from apps.acl.utils import get_permitted_objects
from apps.bioregions.models import Bioregion
from apps.challenges.models import Challenge
from apps.communities.models import Community
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.stories.models import Story
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    BioregionSerializer,
    ChallengeSerializer,
    CommunitySerializer,
    ProjectSerializer,
    TaskSerializer,
    StorySerializer,
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
        Return people based on ACL permissions.
        """
        user = self.request.user

        # Get people the current user has permission to view
        return User.objects.filter(
            Q(id=user.id) | Q(view_members=True) | Q(view_public=True)
        ).distinct()

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

# Bioregion ViewSet
class BioregionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Bioregion CRUD operations.
    Respects ACL permissions.
    """

    serializer_class = BioregionSerializer
    permission_classes = [IsAuthenticated, ACLPermission]

    def get_queryset(self):
        """
        Return bioregions based on ACL permissions.
        """
        user = self.request.user
        # Get bioregions the current user has permission to view
        permitted_bioregions = get_permitted_objects(user, "view", Bioregion)
        return permitted_bioregions

    def perform_create(self, serializer):
        """
        Set created_by when creating a bioregion.
        """
        serializer.save(created_by=self.request.user)

# Community ViewSet
class CommunityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Community CRUD operations.
    Respects ACL permissions.
    """

    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated, ACLPermission]

    def get_queryset(self):
        """
        Return communities based on ACL permissions.
        """
        user = self.request.user
        permitted_communities = get_permitted_objects(user, "view", Community)
        return permitted_communities

    def perform_create(self, serializer):
        """
        Set created_by when creating a community.
        """
        serializer.save(created_by=self.request.user)


# Project ViewSet
class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project CRUD operations.
    Respects ACL permissions.
    """

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, ACLPermission]

    def get_queryset(self):
        """
        Return projects based on ACL permissions.
        """
        user = self.request.user
        permitted_projects = get_permitted_objects(user, "view", Project)
        return permitted_projects

    def perform_create(self, serializer):
        """
        Set created_by when creating a project.
        """
        serializer.save(created_by=self.request.user)


# Task ViewSet
class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task CRUD operations.
    Respects ACL permissions.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, ACLPermission]

    def get_queryset(self):
        """
        Return tasks based on ACL permissions.
        """
        user = self.request.user
        permitted_tasks = get_permitted_objects(user, "view", Task)
        return permitted_tasks

    def perform_create(self, serializer):
        """
        Set created_by when creating a task.
        """
        serializer.save(created_by=self.request.user)


# Story ViewSet
class StoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Story CRUD operations.
    Respects ACL permissions.
    """

    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated, ACLPermission]

    def get_queryset(self):
        """
        Return stories based on ACL permissions.
        """
        user = self.request.user
        permitted_stories = get_permitted_objects(user, "view", Story)
        return permitted_stories

    def perform_create(self, serializer):
        """
        Set created_by when creating a story.
        """
        serializer.save(created_by=self.request.user)

# Challenge ViewSet
class ChallengeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Challenge CRUD operations.
    Respects ACL permissions.
    """

    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated, ACLPermission]

    def get_queryset(self):
        """
        Return challenges based on ACL permissions.
        """
        user = self.request.user
        # Get challenges the current user has permission to view
        permitted_challenges = get_permitted_objects(user, "view", Challenge)
        return permitted_challenges

    def perform_create(self, serializer):
        """
        Set created_by when creating a challenge.
        """
        serializer.save(created_by=self.request.user)