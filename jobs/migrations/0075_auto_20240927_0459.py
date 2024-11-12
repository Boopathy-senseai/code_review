# Generated by Django 2.2.7 on 2024-09-27 04:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0074_client_addons_purchase_history_plan_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='discount_codes_claimed',
            name='is_claimed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='discounts',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='discount_codes_claimed',
            name='discount_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jobs.discounts'),
        ),
        migrations.CreateModel(
            name='discounts_addon',
            fields=[
                ('discount_id', models.AutoField(primary_key=True, serialize=False)),
                ('discount_name', models.CharField(max_length=255)),
                ('discount_code', models.CharField(max_length=255)),
                ('discount_type', models.CharField(max_length=255)),
                ('discount_value', models.IntegerField(default=0)),
                ('discount_currency', models.CharField(max_length=255)),
                ('discount_start_date', models.DateTimeField(null=True)),
                ('discount_end_date', models.DateTimeField(null=True)),
                ('usage_per_client', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('addon_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jobs.tmeta_addons')),
                ('plan_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jobs.tmeta_plan')),
            ],
        ),
        migrations.AddField(
            model_name='discount_codes_claimed',
            name='discount_addon',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jobs.discounts_addon'),
        ),
    ]
