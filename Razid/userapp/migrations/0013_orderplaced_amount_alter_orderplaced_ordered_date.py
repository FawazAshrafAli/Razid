# Generated by Django 5.0.2 on 2024-04-15 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0012_alter_orderplaced_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderplaced',
            name='amount',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='orderplaced',
            name='ordered_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]