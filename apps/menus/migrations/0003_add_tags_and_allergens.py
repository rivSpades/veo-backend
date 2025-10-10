# Generated manually for tags and allergens feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0001_initial'),
    ]

    operations = [
        # Add tags field to MenuItem
        migrations.AddField(
            model_name='menuitem',
            name='tags',
            field=models.JSONField(blank=True, default=list),
        ),
        
        # Create MenuTag model
        migrations.CreateModel(
            name='MenuTag',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.JSONField()),
                ('icon', models.CharField(blank=True, max_length=50)),
                ('color', models.CharField(default='bg-gray-100 text-gray-800', max_length=50)),
                ('category', models.CharField(blank=True, max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Menu Tag',
                'verbose_name_plural': 'Menu Tags',
                'db_table': 'menu_tags',
                'ordering': ['order', 'id'],
            },
        ),
        
        # Create MenuAllergen model
        migrations.CreateModel(
            name='MenuAllergen',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.JSONField()),
                ('color', models.CharField(default='bg-orange-100 text-orange-800', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Menu Allergen',
                'verbose_name_plural': 'Menu Allergens',
                'db_table': 'menu_allergens',
                'ordering': ['order', 'id'],
            },
        ),
    ]

