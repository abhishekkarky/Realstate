# Generated by Django 5.0.1 on 2024-03-07 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0015_rename_authuser_customuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]
