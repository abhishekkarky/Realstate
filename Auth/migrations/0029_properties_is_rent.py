# Generated by Django 4.0.2 on 2024-04-28 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0028_rename_broker_id_review_broker'),
    ]

    operations = [
        migrations.AddField(
            model_name='properties',
            name='is_rent',
            field=models.BooleanField(default=False),
        ),
    ]
