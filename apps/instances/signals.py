"""
Signals for instances app
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from apps.menus.models import Menu
from apps.authentication.models import User
from apps.instances.models import Instance


@receiver(post_save, sender=Menu)
def set_default_qr_menu(sender, instance, created, **kwargs):
    """
    When a new menu is created for an instance that has no QR menu selected,
    automatically set this menu as the QR menu
    """
    if created and instance.instance:
        restaurant_instance = instance.instance
        
        # If instance doesn't have a QR menu selected, set this one
        if not restaurant_instance.qr_selected_menu_id:
            restaurant_instance.qr_selected_menu_id = instance.id
            restaurant_instance.save(update_fields=['qr_selected_menu_id'])
            print(f"✓ Auto-selected menu '{instance.name}' for QR code in instance '{restaurant_instance.name}'")


@receiver(pre_delete, sender=User)
def delete_user_instances(sender, instance, **kwargs):
    """
    When a user is deleted, delete all instances where they are the owner.
    This will cascade delete all related menus, sections, items, etc.
    """
    # Get all instances where this user is an owner
    owned_instances = Instance.objects.filter(
        members__user=instance,
        members__role='owner'
    ).distinct()
    
    # Delete all owned instances (this will cascade delete menus, etc.)
    for instance_obj in owned_instances:
        instance_obj.delete()
        print(f"✓ Deleted instance '{instance_obj.name}' owned by user '{instance.email}'")


