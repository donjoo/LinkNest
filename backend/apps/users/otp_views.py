from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.core.exceptions import ValidationError

from .models import User
from .otp_models import OTP
from .otp_serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    OTPStatusSerializer,
    ResendOTPSerializer
)
from .auth_serializers import UserSerializer


class SendOTPView(generics.CreateAPIView):
    """
    View for sending OTP to user's email during registration.
    """
    serializer_class = SendOTPSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        user = result['user']
        otp = result['otp']
        
        # Send OTP email
        self._send_otp_email(user, otp)
        
        return Response({
            'message': 'OTP sent successfully to your email address.',
            'email': user.email,
            'expires_at': otp.expires_at,
            'time_remaining': otp.get_time_remaining()
        }, status=status.HTTP_201_CREATED)

    def _send_otp_email(self, user, otp):
        """
        Send OTP code to user's email.
        """
        subject = 'Verify Your Email - LinkNest'
        
        message = f"""
        Hello {user.first_name or 'User'},

        Thank you for registering with LinkNest! Please use the following code to verify your email address:

        Verification Code: {otp.code}

        This code will expire in 10 minutes.

        If you didn't request this verification, please ignore this email.

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
            print(f"Failed to send OTP email: {e}")
            raise ValidationError("Failed to send verification email. Please try again.")


class VerifyOTPView(generics.CreateAPIView):
    """
    View for verifying OTP and activating user account.
    """
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        otp = serializer.validated_data['otp']
        
        # Activate the user account
        user.is_active = True
        user.save()
        
        # Generate JWT tokens for the newly activated user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Email verified successfully! Your account is now active.',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)


class ResendOTPView(generics.CreateAPIView):
    """
    View for resending OTP to user's email.
    """
    serializer_class = ResendOTPSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        user = result['user']
        otp = result['otp']
        
        # Send OTP email
        self._send_otp_email(user, otp)
        
        return Response({
            'message': 'New OTP sent successfully to your email address.',
            'email': user.email,
            'expires_at': otp.expires_at,
            'time_remaining': otp.get_time_remaining()
        }, status=status.HTTP_201_CREATED)

    def _send_otp_email(self, user, otp):
        """
        Send OTP code to user's email.
        """
        subject = 'New Verification Code - LinkNest'
        
        message = f"""
        Hello {user.first_name or 'User'},

        You requested a new verification code for your LinkNest account. Please use the following code to verify your email address:

        Verification Code: {otp.code}

        This code will expire in 10 minutes.

        If you didn't request this verification, please ignore this email.

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
            print(f"Failed to send OTP email: {e}")
            raise ValidationError("Failed to send verification email. Please try again.")


@api_view(['GET'])
@permission_classes([AllowAny])
def otp_status_view(request):
    """
    Get OTP status for a user (remaining time, attempts, etc.).
    """
    email = request.query_params.get('email')
    
    if not email:
        return Response({
            'error': 'Email parameter is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'error': 'User with this email does not exist.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get the latest unused OTP for this user
    otp = OTP.objects.filter(
        user=user,
        is_used=False
    ).order_by('-created_at').first()
    
    if not otp:
        return Response({
            'error': 'No active OTP found for this user.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OTPStatusSerializer(otp)
    return Response(serializer.data, status=status.HTTP_200_OK)
