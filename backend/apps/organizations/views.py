"""
Organization views.

Moved from apps.links.views - handles organization and membership management.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Organization, OrganizationMembership
from .serializers import (
    OrganizationSerializer,
    OrganizationMembershipSerializer,
    UserSerializer
)


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing organizations."""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return organizations where user is a member."""
        return Organization.objects.filter(
            Q(owner=self.request.user) | 
            Q(memberships__user=self.request.user)
        ).distinct()

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Create organization and set owner as admin."""
        organization = serializer.save(owner=self.request.user)
        # Create admin membership for the owner
        OrganizationMembership.objects.create(
            user=self.request.user,
            organization=organization,
            role=OrganizationMembership.Role.ADMIN
        )

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all members of an organization."""
        organization = self.get_object()
        
        # Check if user has access to this organization
        if not self._has_organization_access(organization):
            return Response(
                {"detail": "You don't have access to this organization."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        memberships = organization.memberships.all()
        serializer = OrganizationMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def invite_member(self, request, pk=None):
        """Invite a user to the organization."""
        organization = self.get_object()
        
        # Check if user is admin of the organization
        if not self._is_organization_admin(organization):
            return Response(
                {"detail": "Only organization admins can invite members."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        role = request.data.get('role', OrganizationMembership.Role.VIEWER)
        
        if not user_id:
            return Response(
                {"detail": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is already a member
        if OrganizationMembership.objects.filter(
            user=user, organization=organization
        ).exists():
            return Response(
                {"detail": "User is already a member of this organization."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role=role
        )
        
        serializer = OrganizationMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _has_organization_access(self, organization):
        """Check if user has access to the organization."""
        return (
            organization.owner == self.request.user or
            organization.memberships.filter(user=self.request.user).exists()
        )

    def _is_organization_admin(self, organization):
        """Check if user is admin of the organization."""
        return (
            organization.owner == self.request.user or
            organization.memberships.filter(
                user=self.request.user,
                role=OrganizationMembership.Role.ADMIN
            ).exists()
        )