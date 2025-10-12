# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instances', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='qr_foreground_color',
            field=models.CharField(default='#000000', max_length=7),
        ),
        migrations.AddField(
            model_name='instance',
            name='qr_size',
            field=models.IntegerField(default=400),
        ),
        migrations.AddField(
            model_name='instance',
            name='qr_margin',
            field=models.IntegerField(default=4),
        ),
        migrations.AddField(
            model_name='instance',
            name='qr_error_correction_level',
            field=models.CharField(
                choices=[('L', 'Low'), ('M', 'Medium'), ('Q', 'Quartile'), ('H', 'High')],
                default='M',
                max_length=1
            ),
        ),
        migrations.AddField(
            model_name='instance',
            name='qr_logo_image',
            field=models.ImageField(blank=True, null=True, upload_to='qr_logos/'),
        ),
        migrations.AddField(
            model_name='instance',
            name='qr_selected_menu_id',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]

