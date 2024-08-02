# Generated by Django 5.0.6 on 2024-08-02 08:24

import hp_awards.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hp_awards", "0015_alter_submisi_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="submisi",
            name="link_dakung",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="submisi",
            name="file_pb_doc",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=hp_awards.models.randomize_name_doc,
                verbose_name="file PB DOC",
            ),
        ),
        migrations.AlterField(
            model_name="submisi",
            name="file_pb_pdf",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=hp_awards.models.randomize_name_pdf,
                verbose_name="file PB PDF",
            ),
        ),
        migrations.AlterField(
            model_name="submisi",
            name="file_turnitin",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=hp_awards.models.randomize_name_turnitin,
                verbose_name="file Turnitin",
            ),
        ),
    ]
