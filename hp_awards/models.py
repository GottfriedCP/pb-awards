from random import randint
import re
import uuid

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models

from django_resized import ResizedImageField

from .validators import filesize_validator

pdf_validator = FileExtensionValidator(
    allowed_extensions=["docx", "doc", "pdf", "jpg", "jpeg", "png", "bmp"]
)


def randomize_name_doc(instance, filename):
    ext = filename.split(".")[-1]
    return f"dokumen_pb_doc/{instance.kode_submisi}.{ext}"


def randomize_name_pdf(instance, filename):
    ext = filename.split(".")[-1]
    return f"dokumen_pb_pdf/{instance.kode_submisi}.{ext}"


def randomize_name_turnitin(instance, filename):
    ext = filename.split(".")[-1]
    return f"dokumen_turnitin/{instance.kode_submisi}.{ext}"


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
    # PENDIDIKAN_LAINNYA = "oth"
    PENDIDIKAN_CHOICES = {
        SARJANA: "Sarjana (S1)",
        MAGISTER: "Magister (S2)",
        DOKTOR: "Doktor (S3)",
    }

    UMUM = "umum"
    MAHASISWA = "mhs"
    MAHASISWA2 = "mhs2"
    KATEGORI_PENDAFTAR_CHOICES = {
        UMUM: "Umum",
        MAHASISWA: "Mahasiswa",
        MAHASISWA2: "Mahasiswa S2",
    }

    INDIVIDU = "indiv"
    TIM = "tim"
    KATEGORI_TIM_CHOICES = {
        INDIVIDU: "Individu",
        TIM: "Tim",
    }

    kode_submisi = models.UUIDField(default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=100, help_text="Nama sesuai KTP")
    wa = models.CharField(
        max_length=15,
        verbose_name="nomor WA",
        help_text=ht_wa,
        # unique=True,
    )
    email = models.EmailField(max_length=50)
    pendidikan = models.CharField(
        choices=PENDIDIKAN_CHOICES,
        max_length=5,
        verbose_name="pendidikan terakhir",
        blank=True,
        null=True,
    )
    pekerjaan = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Contoh: analis kebijakan, dosen, peneliti, dsb",
        verbose_name="profesi",
    )
    afiliasi = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Nama institusi atau organisasi",
        verbose_name="institusi",
    )
    swafoto = ResizedImageField(
        verbose_name="pasfoto penulis utama",
        size=[None, 480],
        quality=80,
        upload_to="swafoto/",
        force_format="JPEG",
        help_text="[format JPG atau PNG] rasio 2x3 portrait",
        blank=True,
        null=True,
    )
    # ktp = ResizedImageField(
    #     verbose_name="pasfoto penulis utama",
    #     size=[640, None],
    #     quality=80,
    #     upload_to="ktp/",
    #     force_format="JPEG",
    # )
    ktm = models.FileField(
        upload_to="ktm/",
        verbose_name="KTM / surat pernyataan",
        blank=True,
        null=True,
        validators=[pdf_validator, filesize_validator],
        help_text="[format PDF atau JPG/PNG] Bukti atau pernyataan sebagai mahasiswa aktif",
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
        # help_text="Mahasiswa S3 harus memilih Kategori Umum",
    )
    kategori_tim = models.CharField(
        max_length=10,
        choices=KATEGORI_TIM_CHOICES,
        blank=True,
        null=True,
        editable=False,
    )
    topik = models.ForeignKey(
        "Topik",
        related_name="submisi",
        on_delete=models.SET_NULL,
        verbose_name="topik penulisan",
        blank=True,
        null=True,
    )
    # policy_questions = models.ManyToManyField(
    #     "PolicyQuestion",
    #     related_name="submisis",
    #     verbose_name="policy question",
    #     help_text="minimal pilih satu",
    # )
    policy_question = models.ForeignKey(
        "PolicyQuestion",
        related_name="submisis",
        verbose_name="Policy Question",
        on_delete=models.CASCADE,
        help_text="Pilih LAINNYA jika ingin membuat Policy Question baru",
    )
    policy_question_custom = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Policy Question Anda",
        help_text="Anda harus menuliskan Policy Question Anda jika memilih 'LAINNYA'",
    )
    reviewers = models.ManyToManyField(
        "Reviewer",
        related_name="submisis",
        blank=True,
        through="Penilaian",
        verbose_name="reviewer",
    )
    kolaborators = models.ManyToManyField(
        "Kolaborator", related_name="submisis", blank=True, verbose_name="kolaborators"
    )
    # bool check tahapan
    nilai1 = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    lolos_tahap_1 = models.BooleanField(default=False)
    nilai2 = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    lolos_tahap_2 = models.BooleanField(default=False)
    nilai3 = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    lolos_tahap_3 = models.BooleanField(default=False)

    # status submisi
    TUNGGU = "tunggu"
    TUNGGU2 = "tunggu2"  # tunggu penugasan juri tahap 2
    IN_REVIEW = "review"
    GUGUR = "gugur"
    STATUS_CHOICES = {
        TUNGGU: "Menunggu Penilaian",
        TUNGGU2: "Unggah Naskah / Menunggu Penilaian",
        IN_REVIEW: "Dalam Penilaian",
        GUGUR: "Gugur",
    }
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=TUNGGU)
    # field paska penilaian abstrak
    file_pb_pdf = models.FileField(
        blank=True, null=True, upload_to=randomize_name_pdf, verbose_name="file PB PDF"
    )
    file_pb_doc = models.FileField(
        blank=True, null=True, upload_to=randomize_name_doc, verbose_name="file PB DOC"
    )
    file_turnitin = models.FileField(
        blank=True,
        null=True,
        upload_to=randomize_name_turnitin,
        verbose_name="file Turnitin",
    )
    file_pb_ppt = models.FileField(
        blank=True, null=True, upload_to="dokumen_pb_ppt/", verbose_name="file PB PPT"
    )
    link_dakung = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nama} - {self.judul_pb}"

    def save(self, *args, **kwargs):
        # judul upper
        judul = self.judul_pb
        self.judul_pb = str(judul).upper()
        # nama upper
        nama = self.nama
        self.nama = str(nama).upper()
        # pekerjaan upper jika ada
        if self.pekerjaan:
            pekerjaan = str(self.pekerjaan).upper()
            self.pekerjaan = pekerjaan
        # sterilkan nomor WA
        wa = self.wa
        self.wa = re.sub(r"[^\d]", "", wa)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Submisi"
        permissions = [
            ("change_manage_submissions", "Bisa mengatur submisi"),
        ]


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


class PolicyQuestion(TimestampedModel):
    judul = models.CharField(max_length=500)
    sumber = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        # judul = self.judul
        # self.judul = judul[0].upper() + judul[1:].lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name_plural = "Policy Questions"


class Kolaborator(TimestampedModel):
    nama = models.CharField(max_length=100)
    wa = models.CharField(max_length=30, verbose_name="nomor WA", blank=True, null=True)
    email = models.EmailField(max_length=70, blank=True, null=True)
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
    # Pejabat Kementerian Kesehatan, SKM, LAN, Bappenas, Diaspora
    KEMKES = "kemkes"
    PT = "pt"
    SKM = "skm"
    LAN = "lan"
    BAPPENAS = "bappenas"
    DIASPORA = "diaspora"
    LAINNYA = "lainnya"
    KATEGORI_CHOICES = {
        KEMKES: "Pejabat Kementerian Kesehatan",
        PT: "Perguruan Tinggi",
        SKM: "Staf Khusus Menteri",
        LAN: "LAN",
        BAPPENAS: "Bappenas",
        DIASPORA: "Diaspora",
        LAINNYA: "Lainnya",
    }

    nama = models.CharField(max_length=50)
    nip = models.CharField(
        blank=True,
        null=True,
        unique=True,
        max_length=18,
        verbose_name="NIP/NIK/ID lainnya",
        help_text="Maks. 18 karakter",
    )
    kategori = models.CharField(
        choices=KATEGORI_CHOICES, default=LAINNYA, max_length=70
    )
    kepakaran = models.CharField(blank=True, null=True, max_length=100)
    jabatan = models.CharField(blank=True, null=True, max_length=70)
    instansi = models.CharField(blank=True, null=True, max_length=150)
    kode_reviewer = models.UUIDField(default=uuid.uuid4, editable=False)
    # fuck security
    username = models.CharField(max_length=20, unique=True)
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
    reviewer = models.ForeignKey(
        Reviewer, on_delete=models.CASCADE, related_name="penilaians"
    )
    string_nilai1 = models.CharField(max_length=50, blank=True, null=True)
    string_nilai2 = models.CharField(max_length=50, blank=True, null=True)
    string_nilai3 = models.CharField(max_length=50, blank=True, null=True)
    nilai1 = models.IntegerField(default=0)
    nilai2 = models.IntegerField(default=0)
    nilai3 = models.IntegerField(default=0)
    komentar = models.TextField(blank=True, null=True)

    def get_nilai1_list(self):
        if self.string_nilai1:
            return str(self.string_nilai1).split(sep="|")
        return [None, None, None]

    def __str__(self):
        return f"{self.submisi} {self.reviewer}"

    class Meta:
        verbose_name = "Penilaian"
        verbose_name_plural = verbose_name
