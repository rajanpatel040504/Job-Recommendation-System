# Generated by Django 5.1.6 on 2025-02-20 10:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="company",
            old_name="company_name",
            new_name="company",
        ),
    ]
