# Generated by Django 4.1.3 on 2023-03-14 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "wagtail_analytics",
            "0007_remove_analyticssettings_google_analytics_credentials_file_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="analyticssettings",
            name="google_analytics_view_id",
        ),
    ]