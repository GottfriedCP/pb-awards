from random import randint
import re
import uuid

from django.contrib.auth.models import User
from django.db import models

from django_resized import ResizedImageField


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Submisi(TimestampedModel):
    # Tahap 1: Abstrak
    # Tahap 2: Fulltext PDF
    # Tahap 3: PPT dan file final Word docx
    ht_wa = "Nomor WhatsApp (WA) yang bisa dihubungi, diawali 08"
    ht_daftar_anggota = "Tuliskan nama-nama anggota tim yang terlibat (jika ada) dipisahkan dengan tanda titik koma (;)"

    DIPLOMA12 = "d12"
    DIPLOMA3 = "d3"
    SARJANA = "s1"
    MAGISTER = "s2"
    DOKTOR = "s3"
    PENDIDIKAN_CHOICES = {
        DIPLOMA12: "Diploma I/II",
        DIPLOMA3: "Akademi / Diploma III / Sarjana Muda",
        SARJANA: "Diploma IV / Sarjana (S1)",
        MAGISTER: "Magister (S2)",
        DOKTOR: "Doktor (S3)",
    }

    UMUM = "umum"
    MAHASISWA = "mhs"
    KATEGORI_PENDAFTAR_CHOICES = {
        UMUM: "Umum",
        MAHASISWA: "Mahasiswa",
    }
    kode_submisi = models.UUIDField(default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=100, help_text="Nama sesuai KTP")
    wa = models.CharField(
        max_length=15,
        verbose_name="nomor WA",
        help_text=ht_wa,
        unique=True,
    )
    email = models.EmailField(max_length=50, unique=True)
    pendidikan = models.CharField(
        choices=PENDIDIKAN_CHOICES,
        max_length=5,
        verbose_name="pendidikan terakhir",
    )
    afiliasi = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Nama institusi atau organisasi afiliasi, jika ada",
    )
    swafoto = ResizedImageField(
        verbose_name="pasfoto pendaftar",
        size=[None, 480],
        quality=80,
        upload_to="swafoto/",
        force_format="JPEG",
        help_text="rasio 2x3 portrait",
    )
    judul_pb = models.CharField(
        max_length=200,
        help_text="Maksimum 200 karakter",
        verbose_name="judul Policy Brief",
    )
    abstrak_pb = models.TextField(
        verbose_name="abstrak Policy Brief",
        help_text="Maksimum 250 kata",
    )
    kategori_pendaftar = models.CharField(
        max_length=10,
        choices=KATEGORI_PENDAFTAR_CHOICES,
        help_text="Mahasiswa S3 harus memilih Kategori Umum",
    )
    daftar_anggota = models.TextField(
        blank=True, null=True, help_text=ht_daftar_anggota
    )
    topik = models.ForeignKey("Topik", related_name="submisi", on_delete=models.CASCADE)
    reviewers = models.ManyToManyField(
        "Reviewer", related_name="submisis", blank=True, verbose_name="reviewer"
    )
    kolaborators = models.ManyToManyField(
        "Kolaborator", related_name="submisis", blank=True, verbose_name="kolaborators"
    )
    # bool check tahapan
    lolos_tahap_1 = models.BooleanField(default=False)
    lolos_tahap_2 = models.BooleanField(default=False)
    lolos_tahap_3 = models.BooleanField(default=False)

    # status submisi
    TUNGGU = "tunggu"
    GUGUR = "gugur"
    STATUS_CHOICES = {
        TUNGGU: "Menunggu Penilaian",
        GUGUR: "Gugur",
    }
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=TUNGGU)
    # field paska penilaian abstrak
    file_pb_pdf = models.FileField(
        blank=True, null=True, upload_to="dokumen_pb/", verbose_name="file PB PDF"
    )
    file_pb_doc = models.FileField(
        blank=True, null=True, upload_to="dokumen_pb/", verbose_name="file PB DOC"
    )
    file_pb_ppt = models.FileField(
        blank=True, null=True, upload_to="dokumen_pb/", verbose_name="file PB PPT"
    )

    class Meta:
        abstract = False

    def __str__(self):
        return f"{self.nama} - {self.judul_pb}"

    def save(self, *args, **kwargs):
        # judul upper
        judul = self.judul_pb
        self.judul_pb = str(judul).upper()
        # nama upper
        nama = self.nama
        self.nama = str(nama).upper()
        # sterilkan nomor WA
        wa = self.wa
        self.wa = re.sub(r"[^\d]", "", wa)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Submisi"


class Pernyataan(TimestampedModel):
    judul = models.TextField()

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "Pernyataan"


class Topik(TimestampedModel):
    judul = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        judul = self.judul
        self.judul = str(judul).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "Topik"


class Kolaborator(TimestampedModel):
    nama = models.CharField(max_length=100)
    wa = models.CharField(max_length=15, verbose_name="nomor WA", blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    jabatan = models.CharField(max_length=100, blank=True, null=True)
    peran = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Kolaborator"

    def __str__(self):
        return self.nama

    def save(self, *args, **kwargs):
        nama = self.nama
        self.nama = str(nama).upper()
        super().save(*args, **kwargs)


class Reviewer(TimestampedModel):
    nama = models.CharField(max_length=50)
    nip = models.CharField(
        blank=True,
        null=True,
        max_length=18,
        verbose_name="NIP/NIK/ID lainnya",
        help_text="Maks. 18 karakter",
    )
    jabatan = models.CharField(blank=True, null=True, max_length=70)
    instansi = models.CharField(blank=True, null=True, max_length=150)
    kode_reviewer = models.UUIDField(default=uuid.uuid4, editable=False)
    # fuck security
    username = models.CharField(max_length=20)
    passphrase = models.CharField(verbose_name="kata sandi", max_length=6)

    def save(self, *args, **kwargs):
        if not self.passphrase:
            self.passphrase = randint(100000, 999999)
        username = self.username
        self.username = str(username).lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama} - {self.jabatan or ''} - {self.instansi or ''}"

    class Meta:
        verbose_name_plural = "Reviewer"


class Penilaian(TimestampedModel):
    submisi = models.ForeignKey(
        Submisi, on_delete=models.CASCADE, related_name="penilaians"
    )
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    nilai1 = models.IntegerField(default=0)
    nilai2 = models.IntegerField(default=0)
    nilai3 = models.IntegerField(default=0)
    komentar = models.TextField(blank=True, null=True)
