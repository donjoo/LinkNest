"""
URL views.

Moved from apps.links.views - handles namespace and short URL management.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Namespace, ShortURL
from .serializers import (
    NamespaceSerializer,
    ShortURLSerializer,
    ShortURLCreateSerializer
)


class NamespaceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing namespaces."""
    queryset = Namespace.objects.all()
    serializer_class = NamespaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return namespaces from organizations where user is a member."""
        return Namespace.objects.filter(
            organization__memberships__user=self.request.user
        ).distinct()

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create']:
            # Only admins and editors can create namespaces
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Create namespace and validate user permissions."""
        organization = serializer.validated_data['organization']
        
        # Check if user has permission to create namespaces in this organization
        if not self._can_create_namespace(organization):
            raise permissions.PermissionDenied(
                "You don't have permission to create namespaces in this organization."
            )
        
        serializer.save()

    def _can_create_namespace(self, organization):
        """Check if user can create namespaces in the organization."""
        from apps.organizations.models import OrganizationMembership
        membership = organization.memberships.filter(user=self.request.user).first()
        return (
            organization.owner == self.request.user or
            (membership and membership.role in [
                OrganizationMembership.Role.ADMIN,
                OrganizationMembership.Role.EDITOR
            ])
        )


class ShortURLViewSet(viewsets.ModelViewSet):
    """ViewSet for managing short URLs."""
    queryset = ShortURL.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ShortURLCreateSerializer
        return ShortURLSerializer

    def get_queryset(self):
        """Return short URLs from namespaces where user has access."""
        return ShortURL.objects.filter(
            namespace__organization__memberships__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        """Create short URL and validate user permissions."""
        namespace = serializer.validated_data['namespace']
        
        # Check if user has permission to create short URLs in this namespace
        if not self._can_create_short_url(namespace):
            raise permissions.PermissionDenied(
                "You don't have permission to create short URLs in this namespace."
            )
        
        serializer.save(created_by=self.request.user)

    def _can_create_short_url(self, namespace):
        """Check if user can create short URLs in the namespace."""
        from apps.organizations.models import OrganizationMembership
        organization = namespace.organization
        membership = organization.memberships.filter(user=self.request.user).first()
        return (
            organization.owner == self.request.user or
            (membership and membership.role in [
                OrganizationMembership.Role.ADMIN,
                OrganizationMembership.Role.EDITOR
            ])
        )

    @action(detail=True, methods=['post'])
    def redirect(self, request, pk=None):
        """Handle URL redirection and increment click count."""
        short_url = self.get_object()
        
        if not short_url.is_active:
            return Response(
                {"detail": "Short URL is not active."},
                status=status.HTTP_410_GONE
            )
        
        # Increment click count
        short_url.increment_click_count()
        
        return Response({
            "original_url": short_url.original_url,
            "redirect": True
        })

    @action(detail=False, methods=['get'])
    def by_namespace(self, request):
        """Get short URLs by namespace."""
        namespace_id = request.query_params.get('namespace_id')
        if not namespace_id:
            return Response(
                {"detail": "namespace_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            namespace = Namespace.objects.get(id=namespace_id)
        except Namespace.DoesNotExist:
            return Response(
                {"detail": "Namespace not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user has access to this namespace
        if not self._has_namespace_access(namespace):
            return Response(
                {"detail": "You don't have access to this namespace."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        short_urls = self.get_queryset().filter(namespace=namespace)
        serializer = self.get_serializer(short_urls, many=True)
        return Response(serializer.data)

    def _has_namespace_access(self, namespace):
        """Check if user has access to the namespace."""
        organization = namespace.organization
        return (
            organization.owner == self.request.user or
            organization.memberships.filter(user=self.request.user).exists()
        )