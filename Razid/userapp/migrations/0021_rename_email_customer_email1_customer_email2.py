# Generated by Django 5.0.2 on 2024-04-29 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0020_customer_address1_customer_address2_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='email',
            new_name='email1',
        ),
        migrations.AddField(
            model_name='customer',
            name='email2',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]