# Generated by Django 5.1.4 on 2025-03-04 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0007_product_url_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, max_length=500),
        ),
    ]
