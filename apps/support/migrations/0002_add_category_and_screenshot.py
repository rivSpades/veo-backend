# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportticket',
            name='category',
            field=models.CharField(
                choices=[
                    ('cannot_use_app', 'I cannot use the app'),
                    ('payment_issue', 'Payment or billing issue'),
                    ('menu_not_loading', 'Menu not loading properly'),
                    ('qr_code_issue', 'QR code problem'),
                    ('translation_error', 'Translation or language issue'),
                    ('feature_request', 'Feature request or suggestion'),
                    ('other', 'Other issue'),
                ],
                default='other',
                max_length=30
            ),
        ),
        migrations.AddField(
            model_name='supportticket',
            name='screenshot',
            field=models.ImageField(blank=True, null=True, upload_to='ticket_screenshots/'),
        ),
        migrations.AlterField(
            model_name='supportticket',
            name='priority',
            field=models.CharField(
                choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
                default='medium',
                max_length=10
            ),
        ),
    ]

