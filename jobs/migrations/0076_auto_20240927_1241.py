# Generated by Django 2.2.7 on 2024-09-27 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0075_auto_20240927_0459'),
    ]

    operations = [
        migrations.AddField(
            model_name='discounts',
            name='min_amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='discounts_addon',
            name='min_amount',
            field=models.IntegerField(default=0),
        ),
    ]
