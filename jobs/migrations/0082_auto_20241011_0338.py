# Generated by Django 2.2.7 on 2024-10-11 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0081_auto_20241011_0331'),
    ]

    operations = [
        migrations.AddField(
            model_name='discounts',
            name='days',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='discounts_addon',
            name='days',
            field=models.IntegerField(default=0),
        ),
    ]