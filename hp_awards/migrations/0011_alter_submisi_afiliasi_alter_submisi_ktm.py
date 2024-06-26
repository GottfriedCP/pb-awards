# Generated by Django 5.0.6 on 2024-06-13 04:27

import django.core.validators
import hp_awards.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hp_awards", "0010_alter_submisi_afiliasi_alter_submisi_ktm"),
    ]

    operations = [
        migrations.AlterField(
            model_name="submisi",
            name="afiliasi",
            field=models.CharField(
                blank=True,
                help_text="Nama institusi atau organisasi",
                max_length=150,
                null=True,
                verbose_name="institusi",
            ),
        ),
        migrations.AlterField(
            model_name="submisi",
            name="ktm",
            field=models.FileField(
                blank=True,
                help_text="[format PDF atau JPG/PNG] Bukti atau pernyataan sebagai mahasiswa aktif",
                null=True,
                upload_to="ktm/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["pdf", "jpg", "jpeg", "png", "bmp"]
                    ),
                    hp_awards.validators.filesize_validator,
                ],
                verbose_name="KTM / surat pernyataan",
            ),
        ),
    ]
