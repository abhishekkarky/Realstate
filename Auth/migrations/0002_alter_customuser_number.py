# Generated by Django 5.0.1 on 2024-01-13 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='number',
            field=models.CharField(max_length=12),
        ),
    ]
