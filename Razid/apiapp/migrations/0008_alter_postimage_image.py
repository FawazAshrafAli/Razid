# Generated by Django 5.0.2 on 2024-03-07 14:11

import apiapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiapp', '0007_postimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postimage',
            name='image',
            field=models.ImageField(upload_to=apiapp.models.upload_path),
        ),
    ]
