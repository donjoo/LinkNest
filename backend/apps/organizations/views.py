"""
Organization views.

Moved from apps.links.views - handles organization and membership management.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
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
    InviteAcceptSerializer,
    InviteDeclineSerializer,
    InviteAcceptResponseSerializer,
    InviteDeclineResponseSerializer
)
from .permissions import (
    IsOrganizationMember,
    IsOrganizationAdmin,
    CanInviteMembers,
    CanManageMembers
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
            permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]
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


    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, CanInviteMembers])
    def invite_member(self, request, pk=None):
        """Invite a user to the organization."""
        organization = self.get_object()
        
        # Check if user is admin of the organization
        permission = CanInviteMembers()
        if not permission.has_object_permission(request, None, organization):
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

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated, CanInviteMembers])
    def invites(self, request, pk=None):
        """Get all invites for an organization (Admin only)."""
        organization = self.get_object()
        
        # Check if user is admin of the organization
        permission = CanInviteMembers()
        if not permission.has_object_permission(request, None, organization):
            return Response(
                {"detail": "Only organization admins can view invites."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        invites = organization.invites.all()
        serializer = InviteSerializer(invites, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, CanInviteMembers])
    def create_invite(self, request, pk=None):
        """Create an invite for the organization (Admin only)."""
        organization = self.get_object()
        
        # Check if user is admin of the organization
        permission = CanInviteMembers()
        if not permission.has_object_permission(request, None, organization):
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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, CanInviteMembers])
    def revoke_invite(self, request, pk=None):
        """Revoke an invite (Admin only)."""
        organization = self.get_object()
        
        # Check if user is admin of the organization
        permission = CanInviteMembers()
        if not permission.has_object_permission(request, None, organization):
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

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsOrganizationMember])
    def short_urls(self, request, pk=None):
        """Get all short URLs for an organization (Admin can see all, others see their own)."""
        organization = self.get_object()
        
        # Check if user has access to this organization
        permission = IsOrganizationMember()
        if not permission.has_object_permission(request, None, organization):
            return Response(
                {"detail": "You don't have access to this organization."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from apps.urls.models import ShortURL
        from apps.urls.serializers import ShortURLSerializer
        
        # Get all short URLs in this organization
        short_urls = ShortURL.objects.filter(
            namespace__organization=organization
        ).select_related('namespace', 'created_by').order_by('-created_at')
        
        # If user is not admin, filter to only show their own URLs
        is_admin = (
            organization.owner == request.user or
            organization.memberships.filter(
                user=request.user,
                role=OrganizationMembership.Role.ADMIN
            ).exists()
        )
        
        if not is_admin:
            short_urls = short_urls.filter(created_by=request.user)
        
        serializer = ShortURLSerializer(short_urls, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsOrganizationMember])
    def namespaces(self, request, pk=None):
        """Get all namespaces for an organization."""
        organization = self.get_object()
        
        # Check if user has access to this organization
        permission = IsOrganizationMember()
        if not permission.has_object_permission(request, None, organization):
            return Response(
                {"detail": "You don't have access to this organization."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from apps.urls.models import Namespace
        from apps.urls.serializers import NamespaceSerializer
        
        # Get all namespaces in this organization
        namespaces = Namespace.objects.filter(
            organization=organization
        ).order_by('-created_at')
        
        serializer = NamespaceSerializer(namespaces, many=True)
        return Response(serializer.data)

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
    permission_classes = []  # Allow both authenticated and unauthenticated users

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
                {"error": "This invitation link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if invitation is valid
        if not invite.is_valid():
            if invite.is_expired():
                return Response(
                    {"error": "This invitation link is invalid or has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif invite.used:
                return Response(
                    {"error": "This invitation link is invalid or has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif invite.accepted:
                return Response(
                    {"error": "This invitation link is invalid or has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # If user is not authenticated, return 401 with requires_auth flag
        if not request.user.is_authenticated:
            # Check if a user with this email already exists
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            user_exists = User.objects.filter(email=invite.email).exists()
            
            return Response(
                {
                    "error": "Authentication required to accept invitation.",
                    "requires_auth": True,
                    "token": token,
                    "user_exists": user_exists,
                    "invite_email": invite.email,
                    "organization_name": invite.organization.name,
                    "role": invite.role
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is already a member of this organization
        if OrganizationMembership.objects.filter(
            user=request.user,
            organization=invite.organization
        ).exists():
            return Response(
                {"error": "You are already a member of this organization."},
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
            "message": "Invite accepted successfully",
            "organization": invite.organization.name,
            "membership": membership_serializer.data
        }, status=status.HTTP_200_OK)


class InviteDeclineView(APIView):
    """View for declining organization invitations."""
    permission_classes = []  # Allow both authenticated and unauthenticated users

    def post(self, request):
        """Decline an invitation using a token."""
        serializer = InviteDeclineSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.validated_data['token']
        
        try:
            invite = Invite.objects.get(token=token)
        except Invite.DoesNotExist:
            return Response(
                {"error": "This invitation link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if invitation has already been used
        if invite.used:
            return Response(
                {"error": "This invitation link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark invite as used and declined
        invite.used = True
        invite.accepted = False
        invite.save()
        
        return Response({
            "message": "Invite declined"
        }, status=status.HTTP_200_OK)


class InviteRegisterView(APIView):
    """View for registering a new user from an invitation link."""
    permission_classes = []  # Allow unauthenticated users

    def post(self, request):
        """Register a new user and automatically accept the invitation."""
        from django.contrib.auth import get_user_model
        from apps.users.auth_serializers import RegisterSerializer
        from apps.users.otp_models import OTP
        
        User = get_user_model()
        
        # Get token from request
        token = request.data.get('token')
        if not token:
            return Response(
                {"error": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate the invitation
        try:
            invite = Invite.objects.get(token=token)
        except Invite.DoesNotExist:
            return Response(
                {"error": "This invitation link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if invitation is valid
        if not invite.is_valid():
            if invite.is_expired():
                return Response(
                    {"error": "This invitation link is invalid or has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif invite.used:
                return Response(
                    {"error": "This invitation link is invalid or has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif invite.accepted:
                return Response(
                    {"error": "This invitation link is invalid or has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check if user already exists
        if User.objects.filter(email=invite.email).exists():
            return Response(
                {"error": "A user with this email already exists. Please log in instead."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare registration data
        registration_data = {
            'email': invite.email,
            'first_name': request.data.get('first_name', ''),
            'last_name': request.data.get('last_name', ''),
            'password': request.data.get('password'),
            'password_confirm': request.data.get('password_confirm')
        }
        
        # Validate registration data
        serializer = RegisterSerializer(data=registration_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the user
        user = serializer.save()
        
        # Keep user inactive until email verification
        user.is_active = False
        user.save()
        
        # Generate OTP for email verification
        otp = OTP.generate_otp(user)
        
        # Send OTP email with invitation context
        self._send_invitation_otp_email(user, otp, invite)
        
        # Store the invitation token in the user's session or create a temporary record
        # For now, we'll store it in a custom field or use a different approach
        # The user will need to verify their email first, then accept the invitation
        
        return Response({
            'message': 'Registration successful! Please check your email for verification code.',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active
            },
            'invitation': {
                'organization_name': invite.organization.name,
                'role': invite.role,
                'token': token
            },
            'otp_expires_at': otp.expires_at,
            'time_remaining': otp.get_time_remaining(),
            'next_step': 'verify_email_then_accept_invitation'
        }, status=status.HTTP_201_CREATED)
    
    def _send_invitation_otp_email(self, user, otp, invite):
        """Send OTP email with invitation context."""
        subject = f'Verify Your Email - Join {invite.organization.name} on LinkNest'
        
        message = f"""
        Hello {user.first_name or 'User'},

        You've been invited to join {invite.organization.name} as {invite.role} on LinkNest!

        To complete your registration and accept the invitation, please verify your email address using the code below:

        Verification Code: {otp.code}

        This code will expire in 10 minutes.

        After verifying your email, you'll automatically be added to {invite.organization.name}.

        If you didn't request this invitation, please ignore this email.

        Best regards,
        The LinkNest Team
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't expose it to the user
            print(f"Failed to send invitation OTP email: {e}")


class InviteAcceptAfterVerificationView(APIView):
    """View for accepting invitation after email verification."""
    permission_classes = []  # Allow unauthenticated users (they'll be verified via OTP)

    def post(self, request):
        """Accept invitation after email verification."""
        from django.contrib.auth import get_user_model
        from apps.users.otp_models import OTP
        
        User = get_user_model()
        
        # Get token and OTP from request
        token = request.data.get('token')
        otp_code = request.data.get('otp_code')
        
        if not token or not otp_code:
            return Response(
                {"error": "Token and OTP code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate the invitation
        try:
            invite = Invite.objects.get(token=token)
        except Invite.DoesNotExist:
            return Response(
                {"error": "This invitation link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if invitation is valid
        if not invite.is_valid():
            return Response(
                {"error": "This invitation link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find the user
        try:
            user = User.objects.get(email=invite.email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found. Please register first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify OTP
        try:
            otp = OTP.objects.get(user=user, code=otp_code, is_used=False)
            if otp.is_expired():
                return Response(
                    {"error": "OTP code has expired. Please request a new one."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except OTP.DoesNotExist:
            return Response(
                {"error": "Invalid OTP code."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark OTP as used
        otp.is_used = True
        otp.save()
        
        # Activate user
        user.is_active = True
        user.save()
        
        # Check if user is already a member of this organization
        if OrganizationMembership.objects.filter(
            user=user,
            organization=invite.organization
        ).exists():
            return Response(
                {"error": "You are already a member of this organization."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create membership
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=invite.organization,
            role=invite.role
        )
        
        # Mark invite as used and accepted
        invite.used = True
        invite.accepted = True
        invite.save()
        
        # Generate JWT tokens for the user
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        membership_serializer = OrganizationMembershipSerializer(membership)
        return Response({
            "message": "Email verified and invitation accepted successfully!",
            "organization": invite.organization.name,
            "membership": membership_serializer.data,
            "user": {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active
            },
            "tokens": {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)


class OrganizationMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for managing organization members (Admin only)."""
    serializer_class = OrganizationMembershipSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageMembers]

    def get_queryset(self):
        """Return memberships for organizations where user is admin."""
        organization_id = self.kwargs.get('organization_pk')
        if organization_id:
            try:
                organization = Organization.objects.get(id=organization_id)
                return organization.memberships.all()
            except Organization.DoesNotExist:
                pass
        return OrganizationMembership.objects.none()

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated, CanManageMembers]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, CanManageMembers]
        else:
            permission_classes = [permissions.IsAuthenticated, CanManageMembers]
        return [permission() for permission in permission_classes]

    def perform_update(self, serializer):
        """Update member role and validate permissions."""
        membership = self.get_object()
        organization = membership.organization
        
        # Check if user is admin of the organization
        permission = CanManageMembers()
        if not permission.has_object_permission(self.request, None, organization):
            raise PermissionDenied(
                "Only organization admins can manage members."
            )
        
        # Prevent changing the organization owner's role
        if membership.user == organization.owner:
            raise PermissionDenied(
                "Cannot change the organization owner's role."
            )
        
        serializer.save()

    def perform_destroy(self, instance):
        """Remove member from organization."""
        organization = instance.organization
        
        # Check if user is admin of the organization
        permission = CanManageMembers()
        if not permission.has_object_permission(self.request, None, organization):
            raise PermissionDenied(
                "Only organization admins can remove members."
            )
        
        # Prevent removing the organization owner
        if instance.user == organization.owner:
            raise PermissionDenied(
                "Cannot remove the organization owner."
            )
        
        instance.delete()