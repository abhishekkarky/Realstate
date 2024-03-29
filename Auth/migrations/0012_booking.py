# Generated by Django 5.0.1 on 2024-02-28 07:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0011_remove_customuser_isadmin'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('note', models.TextField(blank=True, null=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Auth.properties')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Auth.customuser')),
            ],
        ),
    ]
