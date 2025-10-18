import secrets
import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class OTP(models.Model):
    """
    Model to store OTP codes for email verification.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otps',
        verbose_name=_("User")
    )
    code = models.CharField(
        max_length=6,
        verbose_name=_("OTP Code"),
        help_text=_("6-digit verification code")
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Created At")
    )
    expires_at = models.DateTimeField(
        verbose_name=_("Expires At")
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name=_("Is Used"),
        help_text=_("Whether this OTP has been used for verification")
    )
    attempts = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Attempts"),
        help_text=_("Number of verification attempts")
    )
    max_attempts = models.PositiveIntegerField(
        default=3,
        verbose_name=_("Max Attempts"),
        help_text=_("Maximum number of verification attempts allowed")
    )

    class Meta:
        verbose_name = _("OTP")
        verbose_name_plural = _("OTPs")
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.user.email} - {self.code}"

    def save(self, *args, **kwargs):
        """
        Override save to set expiration time if not already set.
        """
        if not self.expires_at:
            # Set expiration to 10 minutes from now
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

    @classmethod
    def generate_otp(cls, user):
        """
        Generate a new OTP for the given user.
        Invalidates any existing unused OTPs for the user.
        """
        # Invalidate existing unused OTPs for this user
        cls.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)

        # Generate a new 6-digit OTP
        code = str(secrets.randbelow(1000000)).zfill(6)
        
        # Create new OTP
        otp = cls.objects.create(
            user=user,
            code=code
        )
        
        return otp

    def is_expired(self):
        """
        Check if the OTP has expired.
        """
        return timezone.now() > self.expires_at

    def is_valid(self):
        """
        Check if the OTP is valid (not used, not expired, and within attempt limit).
        """
        return (
            not self.is_used and
            not self.is_expired() and
            self.attempts < self.max_attempts
        )

    def verify(self, provided_code):
        """
        Verify the provided OTP code.
        Returns (is_valid, message) tuple.
        """
        self.attempts += 1
        self.save()

        if self.is_used:
            return False, "This OTP has already been used."

        if self.is_expired():
            return False, "This OTP has expired. Please request a new one."

        if self.attempts > self.max_attempts:
            return False, "Maximum verification attempts exceeded. Please request a new OTP."

        if self.code != provided_code:
            return False, "Invalid OTP code. Please try again."

        # Mark as used
        self.is_used = True
        self.save()

        return True, "OTP verified successfully."

    def get_remaining_attempts(self):
        """
        Get the number of remaining verification attempts.
        """
        return max(0, self.max_attempts - self.attempts)

    def get_time_remaining(self):
        """
        Get the time remaining until expiration in seconds.
        """
        if self.is_expired():
            return 0
        
        delta = self.expires_at - timezone.now()
        return int(delta.total_seconds())
