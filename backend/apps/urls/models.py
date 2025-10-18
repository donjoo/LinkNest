"""
URL models.

Moved from apps.links.models - handles URL shortening, namespaces, and related logic.
"""
import uuid
import string
import random
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

User = get_user_model()


class Namespace(models.Model):
    """Namespace model for organizing short URLs within organizations."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',  # Reference to the Organization model in organizations app
        on_delete=models.CASCADE,
        related_name="namespaces"
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Globally unique namespace name")
    )
    description = models.TextField(blank=True, help_text=_("Namespace description"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Namespace")
        verbose_name_plural = _("Namespaces")

    def __str__(self):
        return f"{self.organization.name}/{self.name}"

    def get_short_urls(self):
        """Get all short URLs in this namespace."""
        return self.shorturls.all()


class ShortURL(models.Model):
    """Short URL model for storing shortened URLs."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    namespace = models.ForeignKey(
        Namespace,
        on_delete=models.CASCADE,
        related_name="shorturls"
    )
    original_url = models.URLField(help_text=_("Original URL to be shortened"))
    short_code = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Short code for the URL (unique within namespace)")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_short_urls"
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Optional title for the short URL")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Optional description for the short URL")
    )
    is_active = models.BooleanField(default=True, help_text=_("Whether the short URL is active"))
    expiry_date = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text=_("Optional expiry date for the short URL")
    )
    click_count = models.PositiveIntegerField(default=0, help_text=_("Number of clicks"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["namespace", "short_code"]
        ordering = ["-created_at"]
        verbose_name = _("Short URL")
        verbose_name_plural = _("Short URLs")

    def __str__(self):
        return f"{self.namespace.name}/{self.short_code}"

    def get_full_short_url(self):
        """Get the full short URL."""
        from django.conf import settings
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:8000')
        return f"{base_url}/{self.namespace.name}/{self.short_code}"

    def increment_click_count(self):
        """Increment the click count."""
        self.click_count += 1
        self.save(update_fields=["click_count"])

    def is_expired(self):
        """Check if the short URL has expired."""
        if not self.expiry_date:
            return False
        from django.utils import timezone
        return timezone.now() > self.expiry_date

    def is_accessible(self):
        """Check if the short URL is accessible (active and not expired)."""
        return self.is_active and not self.is_expired()

    @staticmethod
    def generate_short_code(length=6):
        """Generate a random alphanumeric short code."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def clean(self):
        """Validate the short code and ensure it's unique within the namespace."""
        if not self.short_code:
            # Generate a short code if not provided
            self.short_code = self.generate_short_code()
        
        # Ensure short code is unique within the namespace
        if ShortURL.objects.filter(
            namespace=self.namespace,
            short_code=self.short_code
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                _("Short code must be unique within the namespace.")
            )
        
        # Validate expiry date is in the future
        if self.expiry_date:
            from django.utils import timezone
            if self.expiry_date <= timezone.now():
                raise ValidationError(
                    _("Expiry date must be in the future.")
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)