# Generated by Django 5.0.6 on 2024-06-05 03:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hp_awards", "0004_remove_submisi_nik"),
    ]

    operations = [
        migrations.AlterField(
            model_name="submisi",
            name="abstrak_pb",
            field=models.TextField(
                help_text="Maksimum 200 kata", verbose_name="abstrak Policy Brief"
            ),
        ),
    ]
