# Generated by Django 5.0.1 on 2024-03-17 15:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0017_booking_status_review"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="is_agent",
            field=models.BooleanField(default=False),
        ),
    ]
