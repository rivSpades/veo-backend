# Add icon field to Menu model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0004_seed_default_tags_allergens'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='icon',
            field=models.CharField(blank=True, default='Utensils', max_length=50),
        ),
    ]

