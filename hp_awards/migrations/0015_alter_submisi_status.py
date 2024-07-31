# Generated by Django 5.0.6 on 2024-07-30 14:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hp_awards", "0014_alter_penilaian_options_submisi_file_turnitin"),
    ]

    operations = [
        migrations.AlterField(
            model_name="submisi",
            name="status",
            field=models.CharField(
                choices=[
                    ("tunggu", "Menunggu Penilaian"),
                    ("tunggu2", "Unggah Naskah / Menunggu Penilaian"),
                    ("review", "Dalam Penilaian"),
                    ("gugur", "Gugur"),
                ],
                default="tunggu",
                max_length=100,
            ),
        ),
    ]