# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0002_add_category_and_screenshot'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketmessage',
            name='message_type',
            field=models.CharField(
                choices=[
                    ('message', 'Message'),
                    ('status_change', 'Status Change'),
                    ('system', 'System'),
                ],
                default='message',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='ticketmessage',
            name='author',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name='ticket_messages',
                to='authentication.user'
            ),
        ),
    ]

