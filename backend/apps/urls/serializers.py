"""
URL serializers.

Moved from apps.links.serializers - handles namespace and short URL serialization.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Namespace, ShortURL

User = get_user_model()


class NamespaceSerializer(serializers.ModelSerializer):
    """Serializer for namespaces."""
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
        # Check if this is an update operation
        if self.instance:
            # If updating, exclude current instance from uniqueness check
            if Namespace.objects.filter(name=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Namespace name must be globally unique.")
        else:
            # If creating, check if name already exists
            if Namespace.objects.filter(name=value).exists():
                raise serializers.ValidationError("Namespace name must be globally unique.")
        return value


class ShortURLSerializer(serializers.ModelSerializer):
    """Serializer for short URLs."""
    namespace_name = serializers.CharField(source="namespace.name", read_only=True)
    organization_name = serializers.CharField(source="namespace.organization.name", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    full_short_url = serializers.SerializerMethodField()

    class Meta:
        model = ShortURL
        fields = [
            "id", "namespace", "namespace_name", "organization_name",
            "original_url", "short_code", "title", "description",
            "created_by", "created_by_email", "is_active", "expiry_date",
            "click_count", "full_short_url", "created_at", "updated_at"
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
        if namespace and value and value.strip():  # Only validate if value is not empty
            # Check if this is an update operation
            if self.instance:
                # If updating, exclude current instance from uniqueness check
                if ShortURL.objects.filter(
                    namespace=namespace,
                    short_code=value
                ).exclude(pk=self.instance.pk).exists():
                    raise serializers.ValidationError(
                        "Short code must be unique within the namespace."
                    )
            else:
                # If creating, check if short code already exists
                if ShortURL.objects.filter(
                    namespace=namespace,
                    short_code=value
                ).exists():
                    raise serializers.ValidationError(
                        "Short code must be unique within the namespace."
                    )
        return value

    def validate_expiry_date(self, value):
        """Validate that expiry date is in the future."""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Expiry date must be in the future."
            )
        return value


class ShortURLCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating short URLs with auto-generated short codes."""
    
    short_code = serializers.CharField(required=False, allow_blank=True, max_length=50, default='')
    
    class Meta:
        model = ShortURL
        fields = [
            "namespace", "original_url", "short_code", "title", "description", "expiry_date"
        ]
        extra_kwargs = {
            'title': {'required': False, 'allow_blank': True},
            'description': {'required': False, 'allow_blank': True},
            'expiry_date': {'required': False}
        }

    def create(self, validated_data):
        # Set the current user as the creator
        validated_data["created_by"] = self.context["request"].user
        
        # Generate short code if not provided
        if not validated_data.get("short_code"):
            validated_data["short_code"] = ShortURL.generate_short_code()
        
        return super().create(validated_data)

    def validate_expiry_date(self, value):
        """Validate that expiry date is in the future."""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Expiry date must be in the future."
            )
        return value
