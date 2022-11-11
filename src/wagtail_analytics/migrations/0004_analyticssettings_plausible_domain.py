# Generated by Django 4.1.2 on 2022-11-11 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtail_analytics", "0003_analyticssettings_plausible_enabled"),
    ]

    operations = [
        migrations.AddField(
            model_name="analyticssettings",
            name="plausible_domain",
            field=models.CharField(
                default="plausible.io", max_length=255, verbose_name="Plausible Domain"
            ),
        ),
    ]