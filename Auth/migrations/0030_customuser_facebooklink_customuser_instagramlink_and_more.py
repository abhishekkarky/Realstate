# Generated by Django 5.0.1 on 2024-04-25 13:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Auth", "0029_properties_is_archived"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="facebookLink",
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AddField(
            model_name="customuser",
            name="instagramLink",
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AddField(
            model_name="customuser",
            name="intro",
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="customuser",
            name="linkedInLink",
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AddField(
            model_name="customuser",
            name="twitterLink",
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
