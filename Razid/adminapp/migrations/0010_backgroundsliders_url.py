# Generated by Django 5.1.4 on 2025-03-11 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0009_staticpage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='backgroundsliders',
            name='url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
