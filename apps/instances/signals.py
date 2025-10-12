"""
Signals for instances app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.menus.models import Menu


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

