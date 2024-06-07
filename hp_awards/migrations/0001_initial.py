# Generated by Django 5.0.6 on 2024-06-07 17:43

import django.core.validators
import django.db.models.deletion
import django_resized.forms
import hp_awards.validators
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Kolaborator",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("nama", models.CharField(max_length=100)),
                (
                    "wa",
                    models.CharField(
                        blank=True, max_length=15, null=True, verbose_name="nomor WA"
                    ),
                ),
                ("email", models.EmailField(blank=True, max_length=50, null=True)),
                ("jabatan", models.CharField(blank=True, max_length=100, null=True)),
                ("peran", models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                "verbose_name_plural": "Kolaborator",
            },
        ),
        migrations.CreateModel(
            name="Pernyataan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("judul", models.TextField()),
            ],
            options={
                "verbose_name_plural": "Pernyataan",
            },
        ),
        migrations.CreateModel(
            name="PolicyQuestion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("judul", models.CharField(max_length=500)),
                ("sumber", models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                "verbose_name_plural": "Policy Questions",
            },
        ),
        migrations.CreateModel(
            name="Reviewer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("nama", models.CharField(max_length=50)),
                (
                    "nip",
                    models.CharField(
                        blank=True,
                        help_text="Maks. 18 karakter",
                        max_length=18,
                        null=True,
                        unique=True,
                        verbose_name="NIP/NIK/ID lainnya",
                    ),
                ),
                ("jabatan", models.CharField(blank=True, max_length=70, null=True)),
                ("instansi", models.CharField(blank=True, max_length=150, null=True)),
                ("kode_reviewer", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("username", models.CharField(max_length=20, unique=True)),
                (
                    "passphrase",
                    models.CharField(max_length=6, verbose_name="kata sandi"),
                ),
            ],
            options={
                "verbose_name_plural": "Reviewer",
            },
        ),
        migrations.CreateModel(
            name="Topik",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("judul", models.CharField(max_length=100)),
            ],
            options={
                "verbose_name_plural": "Topik",
            },
        ),
        migrations.CreateModel(
            name="Penilaian",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "string_nilai1",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "string_nilai2",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "string_nilai3",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("nilai1", models.IntegerField(default=0)),
                ("nilai2", models.IntegerField(default=0)),
                ("nilai3", models.IntegerField(default=0)),
                ("komentar", models.TextField(blank=True, null=True)),
                (
                    "reviewer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hp_awards.reviewer",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Submisi",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("kode_submisi", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("nama", models.CharField(help_text="Nama sesuai KTP", max_length=100)),
                (
                    "wa",
                    models.CharField(
                        help_text="Nomor WhatsApp (WA) yang bisa dihubungi, diawali 08",
                        max_length=15,
                        unique=True,
                        verbose_name="nomor WA",
                    ),
                ),
                ("email", models.EmailField(max_length=50, unique=True)),
                (
                    "pendidikan",
                    models.CharField(
                        choices=[
                            ("d12", "Diploma I/II"),
                            ("d3", "Akademi / Diploma III / Sarjana Muda"),
                            ("s1", "Diploma IV / Sarjana (S1)"),
                            ("s2", "Magister (S2)"),
                            ("s3", "Doktor (S3)"),
                        ],
                        max_length=5,
                        verbose_name="pendidikan terakhir",
                    ),
                ),
                (
                    "afiliasi",
                    models.CharField(
                        blank=True,
                        help_text="Nama institusi atau organisasi afiliasi, jika ada",
                        max_length=150,
                        null=True,
                    ),
                ),
                (
                    "swafoto",
                    django_resized.forms.ResizedImageField(
                        crop=None,
                        force_format="JPEG",
                        help_text="rasio 2x3 portrait",
                        keep_meta=True,
                        quality=80,
                        scale=None,
                        size=[None, 480],
                        upload_to="swafoto/",
                        verbose_name="pasfoto penulis utama",
                    ),
                ),
                (
                    "ktm",
                    models.FileField(
                        blank=True,
                        help_text="[PDF atau JPG/PNG] KTM atau surat keterangan mahasiswa",
                        null=True,
                        upload_to="ktm/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["pdf", "jpg", "jpeg", "png", "bmp"]
                            ),
                            hp_awards.validators.filesize_validator,
                        ],
                        verbose_name="KTM / surket mahasiswa",
                    ),
                ),
                (
                    "judul_pb",
                    models.CharField(
                        help_text="Maksimum 200 karakter",
                        max_length=200,
                        verbose_name="judul Policy Brief",
                    ),
                ),
                (
                    "abstrak_pb",
                    models.TextField(
                        help_text="Maksimum 250 kata",
                        verbose_name="abstrak Policy Brief",
                    ),
                ),
                (
                    "kategori_pendaftar",
                    models.CharField(
                        choices=[("umum", "Umum"), ("mhs", "Mahasiswa")],
                        help_text="Mahasiswa S3 harus memilih Kategori Umum",
                        max_length=10,
                    ),
                ),
                (
                    "kategori_tim",
                    models.CharField(
                        blank=True,
                        choices=[("indiv", "Individu"), ("tim", "Tim")],
                        editable=False,
                        max_length=10,
                        null=True,
                    ),
                ),
                (
                    "policy_question_custom",
                    models.CharField(blank=True, max_length=500, null=True),
                ),
                ("lolos_tahap_1", models.BooleanField(default=False)),
                ("lolos_tahap_2", models.BooleanField(default=False)),
                ("lolos_tahap_3", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        choices=[("tunggu", "Menunggu Penilaian"), ("gugur", "Gugur")],
                        default="tunggu",
                        max_length=100,
                    ),
                ),
                (
                    "file_pb_pdf",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="dokumen_pb_pdf/",
                        verbose_name="file PB PDF",
                    ),
                ),
                (
                    "file_pb_doc",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="dokumen_pb_doc/",
                        verbose_name="file PB DOC",
                    ),
                ),
                (
                    "file_pb_ppt",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="dokumen_pb_ppt/",
                        verbose_name="file PB PPT",
                    ),
                ),
                (
                    "kolaborators",
                    models.ManyToManyField(
                        blank=True,
                        related_name="submisis",
                        to="hp_awards.kolaborator",
                        verbose_name="kolaborators",
                    ),
                ),
                (
                    "policy_question",
                    models.ForeignKey(
                        help_text="Pilih Lainnya jika ingin membuat Policy Question baru",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submisis",
                        to="hp_awards.policyquestion",
                        verbose_name="policy question",
                    ),
                ),
                (
                    "reviewers",
                    models.ManyToManyField(
                        blank=True,
                        related_name="submisis",
                        through="hp_awards.Penilaian",
                        to="hp_awards.reviewer",
                        verbose_name="reviewer",
                    ),
                ),
                (
                    "topik",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="submisi",
                        to="hp_awards.topik",
                        verbose_name="topik penulisan",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Submisi",
            },
        ),
        migrations.AddField(
            model_name="penilaian",
            name="submisi",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="penilaians",
                to="hp_awards.submisi",
            ),
        ),
    ]
