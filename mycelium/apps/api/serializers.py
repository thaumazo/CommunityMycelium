from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.bioregions.models import Bioregion
from apps.communities.models import Community
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
    Serializer for creating new users via API.
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
