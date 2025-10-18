"""
Organization models.

Moved from apps.links.models - handles organization, memberships, roles, and invitations.
"""
import uuid
import secrets
from datetime import timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Organization(models.Model):
    """Organization model for grouping users and namespaces."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text=_("Organization name"))
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_organizations",
        help_text=_("Organization owner")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    def __str__(self):
        return self.name

    def get_members(self):
        """Get all members of this organization."""
        return User.objects.filter(organizationmembership__organization=self)

    def get_admin_members(self):
        """Get all admin members of this organization."""
        return User.objects.filter(
            organizationmembership__organization=self,
            organizationmembership__role=OrganizationMembership.Role.ADMIN
        )


class OrganizationMembership(models.Model):
    """Membership model for users in organizations with roles."""
    
    class Role(models.TextChoices):
        ADMIN = "admin", _("Admin")
        EDITOR = "editor", _("Editor")
        VIEWER = "viewer", _("Viewer")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organization_memberships"
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text=_("User role in the organization")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "organization"]
        ordering = ["-created_at"]
        verbose_name = _("Organization Membership")
        verbose_name_plural = _("Organization Memberships")

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"

    def clean(self):
        """Validate that the organization owner is always an admin."""
        if self.organization.owner == self.user and self.role != self.Role.ADMIN:
            raise ValidationError(_("Organization owner must be an admin."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Invite(models.Model):
    """Invitation model for inviting users to join organizations."""
    
    class Role(models.TextChoices):
        ADMIN = "admin", _("Admin")
        EDITOR = "editor", _("Editor")
        VIEWER = "viewer", _("Viewer")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="invites",
        help_text=_("Organization being invited to")
    )
    email = models.EmailField(help_text=_("Email address of the invitee"))
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text=_("Role to be assigned to the invitee")
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        help_text=_("Unique token for the invitation")
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invites",
        help_text=_("User who sent the invitation")
    )
    accepted = models.BooleanField(
        default=False,
        help_text=_("Whether the invitation has been accepted")
    )
    used = models.BooleanField(
        default=False,
        help_text=_("Whether the invitation token has been used")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text=_("When the invitation expires"))

    class Meta:
        unique_together = ["organization", "email"]
        ordering = ["-created_at"]
        verbose_name = _("Invitation")
        verbose_name_plural = _("Invitations")

    def __str__(self):
        return f"Invite for {self.email} to {self.organization.name} ({self.role})"

    def save(self, *args, **kwargs):
        """Generate token and set expiry if not already set."""
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if the invitation has expired."""
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if the invitation is valid (not expired, not used, not accepted)."""
        return not self.is_expired() and not self.used and not self.accepted

    def clean(self):
        """Validate the invitation."""
        # Check if user is already a member
        if OrganizationMembership.objects.filter(
            user__email=self.email,
            organization=self.organization
        ).exists():
            raise ValidationError(_("User is already a member of this organization."))
        
        # Check if there's already a pending invite for this email
        existing_invite = Invite.objects.filter(
            organization=self.organization,
            email=self.email,
            used=False
        ).exclude(pk=self.pk)
        
        if existing_invite.exists():
            raise ValidationError(_("There is already a pending invitation for this email."))