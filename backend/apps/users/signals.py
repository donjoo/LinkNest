"""
Django signals for user-related events.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from apps.links.models import Organization, OrganizationMembership

User = get_user_model()


def create_default_organization_for_user(user):
    """
    Create a default organization for a new user.
    
    Args:
        user: The User instance to create an organization for
        
    Returns:
        Organization: The created organization instance
    """
    # Determine organization name based on available user data
    if user.first_name:
        org_name = f"{user.first_name}'s Organization"
    else:
        # Extract email prefix (part before @)
        email_prefix = user.email.split('@')[0]
        org_name = f"{email_prefix}'s Organization"
    
    # Create the organization
    organization = Organization.objects.create(
        name=org_name,
        owner=user
    )
    
    # Create admin membership for the owner
    OrganizationMembership.objects.create(
        user=user,
        organization=organization,
        role=OrganizationMembership.Role.ADMIN
    )
    
    return organization


@receiver(post_save, sender=User)
def create_user_organization(sender, instance, created, **kwargs):
    """
    Signal handler to create a default organization when a new user is created.
    
    This signal is triggered after a User instance is saved. It only creates
    an organization if the user was just created (created=True) to avoid
    creating duplicate organizations if the user is updated later.
    
    Args:
        sender: The model class that sent the signal (User)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        create_default_organization_for_user(instance)
