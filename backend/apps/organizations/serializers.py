"""
Organization serializers.

Moved from apps.links.serializers - handles organization and membership serialization.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMembership

User = get_user_model()


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    """Serializer for organization memberships."""
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ["id", "user", "user_email", "user_full_name", "role", "created_at"]
        read_only_fields = ["id", "created_at"]


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for organizations."""
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    owner_full_name = serializers.CharField(source="owner.full_name", read_only=True)
    member_count = serializers.SerializerMethodField()
    memberships = OrganizationMembershipSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = [
            "id", "name", "owner", "owner_email", "owner_full_name",
            "member_count", "memberships", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_member_count(self, obj):
        return obj.memberships.count()


class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer for displaying user information."""
    
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name"]
        read_only_fields = ["id", "email", "first_name", "last_name", "full_name"]
