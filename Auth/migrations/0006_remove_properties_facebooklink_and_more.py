# Generated by Django 5.0.1 on 2024-02-04 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0005_brokeraccount_properties'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='properties',
            name='facebookLink',
        ),
        migrations.RemoveField(
            model_name='properties',
            name='instagramLink',
        ),
        migrations.RemoveField(
            model_name='properties',
            name='linkedInLink',
        ),
        migrations.RemoveField(
            model_name='properties',
            name='twitterLink',
        ),
        migrations.AddField(
            model_name='brokeraccount',
            name='facebookLink',
            field=models.CharField(default='https://facebook.com', max_length=1000),
        ),
        migrations.AddField(
            model_name='brokeraccount',
            name='instagramLink',
            field=models.CharField(default='https://instagram.com', max_length=1000),
        ),
        migrations.AddField(
            model_name='brokeraccount',
            name='linkedInLink',
            field=models.CharField(default='https://linkedin.com', max_length=1000),
        ),
        migrations.AddField(
            model_name='brokeraccount',
            name='twitterLink',
            field=models.CharField(default='https://twitter.com', max_length=1000),
        ),
    ]