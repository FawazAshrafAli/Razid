# Generated by Django 5.1.4 on 2025-03-06 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0007_orderplaced_image_orderplaced_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='text',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
