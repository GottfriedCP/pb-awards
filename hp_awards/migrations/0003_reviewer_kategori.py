# Generated by Django 5.0.6 on 2024-06-10 01:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hp_awards", "0002_alter_submisi_ktm_alter_submisi_policy_question_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="reviewer",
            name="kategori",
            field=models.CharField(
                choices=[
                    ("kemkes", "Pejabat Kementerian Kesehatan"),
                    ("skm", "Staf Khusus Menteri"),
                    ("lan", "LAN"),
                    ("bappenas", "Bappenas"),
                    ("diaspora", "Diaspora"),
                    ("lainnya", "Lainnya"),
                ],
                default="lainnya",
                max_length=70,
            ),
        ),
    ]
