# Generated by Django 5.0.2 on 2024-08-03 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0010_alter_staticpage_page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticpage',
            name='page',
            field=models.CharField(choices=[('faq', 'FAQ'), ('about', 'About'), ('contact', 'Contact'), ('terms and conditions', 'terms and conditions'), ('privacy policy', 'Privacy and Policy')], max_length=20, unique=True),
        ),
    ]
