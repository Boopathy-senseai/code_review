# Generated by Django 2.2.7 on 2023-08-28 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0004_auto_20230824_0738"),
    ]

    operations = [
        migrations.AddField(
            model_name="career_page_setting",
            name="font_color",
            field=models.CharField(max_length=200, null=True),
        ),
    ]
