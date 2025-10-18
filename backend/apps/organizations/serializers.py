"""
Organization serializers.

Moved from apps.links.serializers - handles organization and membership serialization.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Organization, OrganizationMembership, Invite

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
    current_user_role = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id", "name", "owner", "owner_email", "owner_full_name",
            "member_count", "memberships", "current_user_role", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_member_count(self, obj):
        return obj.memberships.count()
    
    def get_current_user_role(self, obj):
        """Get the current user's role in this organization."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.owner == request.user:
                return 'admin'
            try:
                membership = obj.memberships.get(user=request.user)
                return membership.role
            except OrganizationMembership.DoesNotExist:
                return None
        return None


class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer for displaying user information."""
    
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name"]
        read_only_fields = ["id", "email", "first_name", "last_name", "full_name"]


class InviteSerializer(serializers.ModelSerializer):
    """Serializer for viewing invites."""
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    invited_by_name = serializers.CharField(source="invited_by.full_name", read_only=True)
    invited_by_email = serializers.EmailField(source="invited_by.email", read_only=True)
    is_expired = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = Invite
        fields = [
            "id", "organization", "organization_name", "email", "role",
            "invited_by", "invited_by_name", "invited_by_email",
            "accepted", "used", "created_at", "expires_at",
            "is_expired", "is_valid"
        ]
        read_only_fields = [
            "id", "organization", "invited_by", "accepted", "used",
            "created_at", "expires_at", "is_expired", "is_valid"
        ]

    def get_is_expired(self, obj):
        return obj.is_expired()

    def get_is_valid(self, obj):
        return obj.is_valid()


class InviteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating invites."""
    
    class Meta:
        model = Invite
        fields = ["email", "role"]

    def validate_email(self, value):
        """Validate that the email is not already a member."""
        organization = self.context.get('organization')
        if organization and OrganizationMembership.objects.filter(
            user__email=value,
            organization=organization
        ).exists():
            raise serializers.ValidationError("User is already a member of this organization.")
        return value

    def validate(self, attrs):
        """Validate the invite data."""
        organization = self.context.get('organization')
        if organization:
            # Check if there's already a pending invite for this email
            existing_invite = Invite.objects.filter(
                organization=organization,
                email=attrs['email'],
                used=False
            )
            if existing_invite.exists():
                raise serializers.ValidationError("There is already a pending invitation for this email.")
        return attrs


class InviteAcceptSerializer(serializers.Serializer):
    """Serializer for accepting invites."""
    token = serializers.CharField(max_length=64)

    def validate_token(self, value):
        """Validate the invite token."""
        try:
            invite = Invite.objects.get(token=value)
        except Invite.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token.")
        
        if not invite.is_valid():
            if invite.is_expired():
                raise serializers.ValidationError("This invitation has expired.")
            elif invite.used:
                raise serializers.ValidationError("This invitation has already been used.")
            elif invite.accepted:
                raise serializers.ValidationError("This invitation has already been accepted.")
        
        return value


class InviteDeclineSerializer(serializers.Serializer):
    """Serializer for declining invites."""
    token = serializers.CharField(max_length=64)

    def validate_token(self, value):
        """Validate the invite token."""
        try:
            invite = Invite.objects.get(token=value)
        except Invite.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token.")
        
        if invite.used:
            raise serializers.ValidationError("This invitation has already been used.")
        
        return value


class InviteAcceptResponseSerializer(serializers.Serializer):
    """Serializer for invite accept response."""
    message = serializers.CharField()
    organization = serializers.CharField()
    membership = OrganizationMembershipSerializer(required=False)


class InviteDeclineResponseSerializer(serializers.Serializer):
    """Serializer for invite decline response."""
    message = serializers.CharField()
