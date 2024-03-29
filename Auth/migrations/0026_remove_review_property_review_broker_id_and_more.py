# Generated by Django 5.0.1 on 2024-03-25 03:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0025_properties_latitude_properties_longitude"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="review",
            name="property",
        ),
        migrations.AddField(
            model_name="review",
            name="broker_id",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="Auth.brokeraccount",
            ),
        ),
        migrations.AlterField(
            model_name="properties",
            name="longitude",
            field=models.FloatField(default=85.34238),
        ),
    ]
