# Generated by Django 5.0.6 on 2024-06-05 01:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hp_awards", "0002_alter_pernyataan_options_alter_reviewer_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="submisi",
            name="abstrak_pb",
            field=models.TextField(max_length=200, verbose_name="abstrak Policy Brief"),
        ),
    ]
