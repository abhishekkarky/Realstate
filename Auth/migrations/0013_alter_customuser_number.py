# Generated by Django 5.0.1 on 2024-02-28 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0012_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='number',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
