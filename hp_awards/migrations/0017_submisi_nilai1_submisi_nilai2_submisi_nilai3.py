# Generated by Django 5.0.6 on 2024-08-04 03:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hp_awards", "0016_submisi_link_dakung_alter_submisi_file_pb_doc_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="submisi",
            name="nilai1",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name="submisi",
            name="nilai2",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name="submisi",
            name="nilai3",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
