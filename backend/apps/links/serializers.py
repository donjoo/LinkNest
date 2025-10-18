from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMembership, Namespace, ShortURL

User = get_user_model()


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ["id", "user", "user_email", "user_full_name", "role", "created_at"]
        read_only_fields = ["id", "created_at"]


class OrganizationSerializer(serializers.ModelSerializer):
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


class NamespaceSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    short_url_count = serializers.SerializerMethodField()

    class Meta:
        model = Namespace
        fields = [
            "id", "organization", "organization_name", "name", "description",
            "short_url_count", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_short_url_count(self, obj):
        return obj.shorturls.count()

    def validate_name(self, value):
        """Validate that namespace name is unique globally."""
        if Namespace.objects.filter(name=value).exists():
            raise serializers.ValidationError("Namespace name must be globally unique.")
        return value


class ShortURLSerializer(serializers.ModelSerializer):
    namespace_name = serializers.CharField(source="namespace.name", read_only=True)
    organization_name = serializers.CharField(source="namespace.organization.name", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    full_short_url = serializers.SerializerMethodField()

    class Meta:
        model = ShortURL
        fields = [
            "id", "namespace", "namespace_name", "organization_name",
            "original_url", "short_code", "title", "description",
            "created_by", "created_by_email", "is_active", "click_count",
            "full_short_url", "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "created_by", "click_count", "created_at", "updated_at"
        ]

    def get_full_short_url(self, obj):
        return obj.get_full_short_url()

    def create(self, validated_data):
        # Set the current user as the creator
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def validate_short_code(self, value):
        """Validate that short code is unique within the namespace."""
        namespace = self.initial_data.get("namespace")
        if namespace and value:
            if ShortURL.objects.filter(
                namespace=namespace,
                short_code=value
            ).exists():
                raise serializers.ValidationError(
                    "Short code must be unique within the namespace."
                )
        return value


class ShortURLCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating short URLs with auto-generated short codes."""
    
    class Meta:
        model = ShortURL
        fields = [
            "namespace", "original_url", "short_code", "title", "description"
        ]

    def create(self, validated_data):
        # Set the current user as the creator
        validated_data["created_by"] = self.context["request"].user
        
        # Generate short code if not provided
        if not validated_data.get("short_code"):
            validated_data["short_code"] = ShortURL.generate_short_code()
        
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer for displaying user information."""
    
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name"]
        read_only_fields = ["id", "email", "first_name", "last_name", "full_name"]
