from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.bioregions.models import Bioregion
from apps.challenges.models import Challenge
from apps.communities.models import Community
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.stories.models import Story
from apps.relationships.models import Relationship
from apps.socialroles.models import Socialrole
from apps.metacrisis_facets.models import Metacrisis_facet
from apps.maladaptives.models import Maladaptive

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    user_bioregions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Bioregion.objects.all(), required=False
    )
    user_communities = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Community.objects.all(), required=False
    )
    user_relationships = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Relationship.objects.all(), required=False
    )
    user_socialroles = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Socialrole.objects.all(), required=False
    )
    user_metacrisis_facets = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Metacrisis_facet.objects.all(), required=False
    )
    user_maladaptives = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Maladaptive.objects.all(), required=False
    )
    invited_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "user_location",
            "invited_by",
            "user_bioregions",
            "user_communities",
            "user_relationships",
            "user_socialroles",
            "user_metacrisis_facets",
            "user_maladaptives",
            "linked_in",
            "view_members",
            "view_public",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new people via API.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "full_name",
            "password",
            "confirm_password",
        ]

    def validate(self, data):
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserDetailSerializer(UserSerializer):
    """
    Detailed user serializer with nested objects.
    """
    user_bioregions_detail = serializers.SerializerMethodField()
    user_communities_detail = serializers.SerializerMethodField()
    invited_by_detail = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            "user_bioregions_detail",
            "user_communities_detail",
            "invited_by_detail",
        ]

    def get_user_bioregions_detail(self, obj):
        return [{"id": b.id, "name": b.name} for b in obj.user_bioregions.all()]

    def get_user_communities_detail(self, obj):
        return [{"id": c.id, "name": c.name} for c in obj.user_communities.all()]

    def get_invited_by_detail(self, obj):
        if obj.invited_by:
            return {
                "id": obj.invited_by.id,
                "username": obj.invited_by.username,
                "full_name": obj.invited_by.full_name,
            }
        return None

class BioregionSerializer(serializers.ModelSerializer):
    """
    Serializer for Bioregion model.
    """
    created_by_detail = serializers.SerializerMethodField()
    parent_region_detail = serializers.SerializerMethodField()

    class Meta:
        model = Bioregion
        fields = [
            "id",
            "title",
            "description",
            "parent_region",
            "parent_region_detail",
            "picture",
            "picture_thumbnail",
            "location",
            "latitude",
            "longitude",
            "radius_km",
            "created_by",
            "created_by_detail",
        ]
        read_only_fields = ["id", "picture_thumbnail"]

    def get_created_by_detail(self, obj):
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "username": obj.created_by.username,
                "full_name": obj.created_by.full_name,
            }
        return None

    def get_parent_region_detail(self, obj):
        if obj.parent_region:
            return {
                "id": obj.parent_region.id,
                "title": obj.parent_region.title,
            }
        return None


class CommunitySerializer(serializers.ModelSerializer):
    """
    Serializer for Community model.
    """
    created_by_detail = serializers.SerializerMethodField()
    members_detail = serializers.SerializerMethodField()
    bioregions_detail = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            "id",
            "title",
            "description",
            "members",
            "members_detail",
            "bioregions",
            "bioregions_detail",
            "url",
            "picture",
            "picture_thumbnail",
            "created_by",
            "created_by_detail",
            "view_members",
            "view_public",
        ]
        read_only_fields = ["id", "picture_thumbnail"]

    def get_created_by_detail(self, obj):
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "username": obj.created_by.username,
                "full_name": obj.created_by.full_name,
            }
        return None

    def get_members_detail(self, obj):
        return [
            {
                "id": m.id,
                "username": m.username,
                "full_name": m.full_name,
            }
            for m in obj.members.all()
        ]

    def get_bioregions_detail(self, obj):
        return [
            {
                "id": b.id,
                "title": b.title,
            }
            for b in obj.bioregions.all()
        ]


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    """
    created_by_detail = serializers.SerializerMethodField()
    members_detail = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "members",
            "members_detail",
            "url",
            "created_by",
            "created_by_detail",
            "view_members",
            "view_public",
        ]
        read_only_fields = ["id"]

    def get_created_by_detail(self, obj):
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "username": obj.created_by.username,
                "full_name": obj.created_by.full_name,
            }
        return None

    def get_members_detail(self, obj):
        return [
            {
                "id": m.id,
                "username": m.username,
                "full_name": m.full_name,
            }
            for m in obj.members.all()
        ]


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.
    """
    created_by_detail = serializers.SerializerMethodField()
    assigned_to_detail = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "due_date",
            "description",
            "status",
            "created_by",
            "created_by_detail",
            "assigned_to",
            "assigned_to_detail",
        ]
        read_only_fields = ["id"]

    def get_created_by_detail(self, obj):
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "username": obj.created_by.username,
                "full_name": obj.created_by.full_name,
            }
        return None

    def get_assigned_to_detail(self, obj):
        return [
            {
                "id": u.id,
                "username": u.username,
                "full_name": u.full_name,
            }
            for u in obj.assigned_to.all()
        ]


class StorySerializer(serializers.ModelSerializer):
    """
    Serializer for Story model.
    """
    created_by_detail = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            "id",
            "title",
            "text_content",
            "created_by",
            "created_by_detail",
            "view_members",
            "view_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_created_by_detail(self, obj):
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "username": obj.created_by.username,
                "full_name": obj.created_by.full_name,
            }
        return None



class ChallengeSerializer(serializers.ModelSerializer):
    """
    Serializer for Challenge model.
    """
    created_by_detail = serializers.SerializerMethodField()
    related_bioregion_detail = serializers.SerializerMethodField()
    related_facet_detail = serializers.SerializerMethodField()
    parent_region_detail = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            "id",
            "title",
            "description",
            "parent_region",
            "parent_region_detail",
            "related_facet",
            "related_facet_detail",
            "related_bioregion",
            "related_bioregion_detail",
            "level",
            "location",
            "latitude",
            "longitude",
            "created_by",
            "created_by_detail",
        ]
        read_only_fields = ["id"]

    def get_created_by_detail(self, obj):
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "username": obj.created_by.username,
                "full_name": obj.created_by.full_name,
            }
        return None

    def get_related_bioregion_detail(self, obj):
        if obj.related_bioregion:
            return {
                "id": obj.related_bioregion.id,
                "title": obj.related_bioregion.title,
            }
        return None

    def get_related_facet_detail(self, obj):
        if obj.related_facet:
            return {
                "id": obj.related_facet.id,
                "name": obj.related_facet.title,
            }
        return None

    def get_parent_region_detail(self, obj):
        if obj.parent_region:
            return {
                "id": obj.parent_region.id,
                "title": obj.parent_region.title,
            }
        return None