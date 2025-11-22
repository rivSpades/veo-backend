# Generated manually - Populate default QR settings for existing instances

from django.db import migrations


def populate_qr_defaults(apps, schema_editor):
    """
    Populate default QR code settings for all instances that don't have them set
    """
    Instance = apps.get_model('instances', 'Instance')
    
    for instance in Instance.objects.all():
        updated = False
        
        # Set default QR foreground color if not set
        if not instance.qr_foreground_color or instance.qr_foreground_color == '':
            instance.qr_foreground_color = '#000000'
            updated = True
        
        # Set default QR size if not set or zero
        if not instance.qr_size or instance.qr_size == 0:
            instance.qr_size = 400
            updated = True
        
        # Set default QR margin if not set
        if instance.qr_margin is None or instance.qr_margin == 0:
            instance.qr_margin = 4
            updated = True
        
        # Set default error correction level if not set
        if not instance.qr_error_correction_level or instance.qr_error_correction_level == '':
            instance.qr_error_correction_level = 'M'
            updated = True
        
        # Set selected menu to first menu if not set
        if not instance.qr_selected_menu_id:
            Menu = apps.get_model('menus', 'Menu')
            first_menu = Menu.objects.filter(instance=instance, is_active=True).first()
            if first_menu:
                instance.qr_selected_menu_id = first_menu.id
                updated = True
        
        if updated:
            instance.save()
            print(f"✓ Populated QR defaults for instance: {instance.name}")


def reverse_func(apps, schema_editor):
    """
    Reverse is a no-op - we don't want to clear the QR settings
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('instances', '0002_add_qr_code_settings'),
        ('menus', '0001_initial'),  # Need menus to exist
    ]

    operations = [
        migrations.RunPython(populate_qr_defaults, reverse_func),
    ]


