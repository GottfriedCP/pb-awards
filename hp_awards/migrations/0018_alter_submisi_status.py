# Generated by Django 5.0.6 on 2024-08-04 03:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hp_awards", "0017_submisi_nilai1_submisi_nilai2_submisi_nilai3"),
    ]

    operations = [
        migrations.AlterField(
            model_name="submisi",
            name="status",
            field=models.CharField(
                choices=[
                    ("tunggu", "Menunggu Penilaian"),
                    ("tunggu2", "Unggah Naskah / Menunggu Penilaian"),
                    ("tunggu3", "Unggah PPT / Menunggu Penilaian"),
                    ("review", "Dalam Penilaian"),
                    ("gugur", "Gugur"),
                ],
                default="tunggu",
                max_length=100,
            ),
        ),
    ]