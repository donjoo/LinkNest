from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .otp_models import OTP

User = get_user_model()


class SendOTPSerializer(serializers.Serializer):
    """
    Serializer for sending OTP to user's email.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """
        Validate that the email exists and user is not already verified.
        """
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        # Check if user is already active (verified)
        if user.is_active:
            raise serializers.ValidationError("This email is already verified.")
        
        return value

    def create(self, validated_data):
        """
        Generate and send OTP to the user.
        """
        email = validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate new OTP
        otp = OTP.generate_otp(user)
        
        # Send email (this will be handled by the view)
        return {
            'user': user,
            'otp': otp,
            'message': 'OTP sent successfully'
        }


class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying OTP code.
    """
    email = serializers.EmailField(required=True)
    code = serializers.CharField(
        max_length=6,
        min_length=6,
        required=True,
        help_text="6-digit OTP code"
    )

    def validate_code(self, value):
        """
        Validate OTP code format.
        """
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must contain only digits.")
        
        if len(value) != 6:
            raise serializers.ValidationError("OTP code must be exactly 6 digits.")
        
        return value

    def validate(self, attrs):
        """
        Validate the OTP code against the user's email.
        """
        email = attrs['email']
        code = attrs['code']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        # Get the latest unused OTP for this user
        try:
            otp = OTP.objects.filter(
                user=user,
                is_used=False
            ).order_by('-created_at').first()
        except OTP.DoesNotExist:
            otp = None
        
        if not otp:
            raise serializers.ValidationError("No valid OTP found. Please request a new one.")
        
        # Verify the OTP
        is_valid, message = otp.verify(code)
        
        if not is_valid:
            raise serializers.ValidationError(message)
        
        # Store the verified OTP in the validated data for use in the view
        attrs['user'] = user
        attrs['otp'] = otp
        
        return attrs


class OTPStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for OTP status information.
    """
    time_remaining = serializers.SerializerMethodField()
    remaining_attempts = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = OTP
        fields = [
            'id',
            'created_at',
            'expires_at',
            'is_used',
            'attempts',
            'max_attempts',
            'time_remaining',
            'remaining_attempts',
            'is_expired'
        ]
        read_only_fields = fields

    def get_time_remaining(self, obj):
        return obj.get_time_remaining()

    def get_remaining_attempts(self, obj):
        return obj.get_remaining_attempts()

    def get_is_expired(self, obj):
        return obj.is_expired()


class ResendOTPSerializer(serializers.Serializer):
    """
    Serializer for resending OTP.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """
        Validate that the email exists and user is not already verified.
        """
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        # Check if user is already active (verified)
        if user.is_active:
            raise serializers.ValidationError("This email is already verified.")
        
        return value

    def create(self, validated_data):
        """
        Generate and send a new OTP to the user.
        """
        email = validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate new OTP
        otp = OTP.generate_otp(user)
        
        return {
            'user': user,
            'otp': otp,
            'message': 'New OTP sent successfully'
        }
