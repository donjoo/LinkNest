"""
Organization views.

Moved from apps.links.views - handles organization and membership management.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
import logging
from .models import Organization, OrganizationMembership, Invite
from .serializers import (
    OrganizationSerializer,
    OrganizationMembershipSerializer,
    UserSerializer,
    InviteSerializer,
    InviteCreateSerializer,
    InviteAcceptSerializer
)

User = get_user_model()


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

    @action(detail=True, methods=['get'])
    def invites(self, request, pk=None):
        """Get all invites for an organization (Admin only)."""
        organization = self.get_object()
        
        # Check if user is admin of the organization
        if not self._is_organization_admin(organization):
            return Response(
                {"detail": "Only organization admins can view invites."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        invites = organization.invites.all()
        serializer = InviteSerializer(invites, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_invite(self, request, pk=None):
        """Create an invite for the organization (Admin only)."""
        organization = self.get_object()
        
        # Check if user is admin of the organization
        if not self._is_organization_admin(organization):
            return Response(
                {"detail": "Only organization admins can create invites."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = InviteCreateSerializer(
            data=request.data,
            context={'organization': organization}
        )
        
        if serializer.is_valid():
            invite = serializer.save(
                organization=organization,
                invited_by=request.user
            )
            
            # Send invitation email
            email_sent = False
            email_error = None
            try:
                email_sent = self._send_invitation_email(invite)
            except Exception as e:
                email_error = str(e)
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send invitation email for invite {invite.id}: {e}")
            
            response_serializer = InviteSerializer(invite)
            response_data = response_serializer.data
            response_data['email_sent'] = email_sent
            if email_error:
                response_data['email_error'] = email_error
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def revoke_invite(self, request, pk=None):
        """Revoke an invite (Admin only)."""
        organization = self.get_object()
        
        # Check if user is admin of the organization
        if not self._is_organization_admin(organization):
            return Response(
                {"detail": "Only organization admins can revoke invites."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        invite_id = request.data.get('invite_id')
        if not invite_id:
            return Response(
                {"detail": "invite_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invite = organization.invites.get(id=invite_id)
        except Invite.DoesNotExist:
            return Response(
                {"detail": "Invite not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if invite.used or invite.accepted:
            return Response(
                {"detail": "Cannot revoke a used or accepted invite."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invite.delete()
        return Response({"detail": "Invite revoked successfully."}, status=status.HTTP_200_OK)

    def _send_invitation_email(self, invite):
        """Send invitation email to the invitee."""
        frontend_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
        invite_url = f"{frontend_url}/invite/accept/?token={invite.token}"
        
        subject = f"You've been invited to join {invite.organization.name} on LinkNest"
        message = f"""
Hi {invite.email},

You've been invited to join {invite.organization.name} as {invite.role}.

Click the link below to accept:
{invite_url}

This invitation will expire in 7 days.

Best regards,
The LinkNest Team
        """.strip()
        
        logger = logging.getLogger(__name__)
        logger.info(f"Attempting to send invitation email to {invite.email}")
        logger.info(f"Email backend: {settings.EMAIL_BACKEND}")
        logger.info(f"From email: {settings.DEFAULT_FROM_EMAIL}")
        logger.info(f"Invite URL: {invite_url}")
        
        try:
            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invite.email],
                fail_silently=False,
            )
            logger.info(f"Successfully sent invitation email to {invite.email}. Result: {result}")
            logger.info(f"Email backend used: {settings.EMAIL_BACKEND}")
            return True
        except Exception as e:
            logger.error(f"Failed to send invitation email to {invite.email}: {e}")
            logger.error(f"Email backend: {settings.EMAIL_BACKEND}")
            logger.error(f"From email: {settings.DEFAULT_FROM_EMAIL}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {str(e)}")
            # Re-raise the exception so the caller knows email sending failed
            raise e


class InviteAcceptView(APIView):
    """View for accepting organization invitations."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Accept an invitation using a token."""
        serializer = InviteAcceptSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.validated_data['token']
        
        try:
            invite = Invite.objects.get(token=token)
        except Invite.DoesNotExist:
            return Response(
                {"detail": "Invalid invitation token."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not invite.is_valid():
            if invite.is_expired():
                return Response(
                    {"detail": "This invitation has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif invite.used:
                return Response(
                    {"detail": "This invitation has already been used."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif invite.accepted:
                return Response(
                    {"detail": "This invitation has already been accepted."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check if user is already a member
        if OrganizationMembership.objects.filter(
            user=request.user,
            organization=invite.organization
        ).exists():
            return Response(
                {"detail": "You are already a member of this organization."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create membership
        membership = OrganizationMembership.objects.create(
            user=request.user,
            organization=invite.organization,
            role=invite.role
        )
        
        # Mark invite as used and accepted
        invite.used = True
        invite.accepted = True
        invite.save()
        
        membership_serializer = OrganizationMembershipSerializer(membership)
        return Response({
            "detail": "Successfully joined the organization!",
            "membership": membership_serializer.data
        }, status=status.HTTP_200_OK)