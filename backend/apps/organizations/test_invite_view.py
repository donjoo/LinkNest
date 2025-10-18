"""
Test view for invite creation using session authentication.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Organization, Invite, OrganizationMembership
from .serializers import InviteSerializer

User = get_user_model()


class TestInviteCreateView(APIView):
    """Test view for invite creation using session authentication."""
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create an invite using session authentication."""
        try:
            # Get the first organization (for testing)
            org = Organization.objects.first()
            if not org:
                return Response(
                    {'error': 'No organization found'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user is admin of the organization
            membership = OrganizationMembership.objects.filter(
                user=request.user,
                organization=org,
                role=OrganizationMembership.Role.ADMIN
            ).first()
            
            if not membership:
                return Response(
                    {'error': 'Only organization admins can create invites'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Create invite
            email = request.data.get('email')
            role = request.data.get('role', 'viewer')
            
            if not email:
                return Response(
                    {'error': 'Email is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            invite = Invite.objects.create(
                organization=org,
                email=email,
                role=role,
                invited_by=request.user
            )
            
            # Send invitation email
            frontend_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
            invite_url = f'{frontend_url}/invite/accept/?token={invite.token}'
            
            try:
                subject = f'You have been invited to join {invite.organization.name} on LinkNest'
                message = f'''
Hi {invite.email},

You have been invited to join {invite.organization.name} as {invite.role}.

Click the link below to accept:
{invite_url}

This invitation will expire in 7 days.

Best regards,
The LinkNest Team
                '''.strip()
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[invite.email],
                    fail_silently=False,
                )
                
                email_sent = True
            except Exception as e:
                email_sent = False
                print(f"Error sending email: {e}")
            
            serializer = InviteSerializer(invite)
            return Response({
                'message': 'Invite created successfully!',
                'invite': serializer.data,
                'email_sent': email_sent,
                'invite_url': invite_url if email_sent else None
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
