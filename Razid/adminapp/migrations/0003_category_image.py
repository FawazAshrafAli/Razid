# Generated by Django 5.1.4 on 2025-02-21 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0002_alter_category_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(default=None, upload_to='categories/'),
            preserve_default=False,
        ),
    ]
