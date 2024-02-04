# Generated by Django 5.0.1 on 2024-02-04 16:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0004_contactlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrokerAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('intro', models.CharField(max_length=50)),
                ('photo', models.ImageField(default='/static/images/img_1.jpg', upload_to='media/')),
            ],
        ),
        migrations.CreateModel(
            name='Properties',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='/static/images/img_1.jpg', upload_to='media/')),
                ('imageTwo', models.ImageField(default='/static/images/img_1.jpg', upload_to='media/')),
                ('imageThree', models.ImageField(default='/static/images/img_1.jpg', upload_to='media/')),
                ('name', models.CharField(max_length=20)),
                ('location', models.CharField(max_length=50)),
                ('beds', models.CharField(max_length=10)),
                ('baths', models.CharField(max_length=10)),
                ('price', models.CharField(max_length=30)),
                ('instagramLink', models.CharField(default='https://instagram.com', max_length=1000)),
                ('facebookLink', models.CharField(default='https://facebook.com', max_length=1000)),
                ('twitterLink', models.CharField(default='https://twitter.com', max_length=1000)),
                ('linkedInLink', models.CharField(default='https://linkedin.com', max_length=1000)),
                ('description', models.CharField(max_length=1000)),
                ('broker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Auth.brokeraccount')),
            ],
        ),
    ]
