# Generated by Django 5.0.1 on 2024-04-13 11:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0028_rename_broker_id_review_broker"),
    ]

    operations = [
        migrations.AddField(
            model_name="properties",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
    ]
