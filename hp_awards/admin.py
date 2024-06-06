from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from . import forms, models

admin.site.site_header = "Administrasi Konten Lomba PB"
admin.site.site_title = "HP Awards"
admin.site.index_title = "Beranda"


@admin.register(models.Submisi)
class SubmisiAdmin(admin.ModelAdmin):
    list_display = ["nama", "kategori_pendaftar", "created_at", "status", "judul_pb"]
    list_filter = ["status", "kategori_pendaftar"]
    filter_horizontal = ["reviewers", "kolaborators"]


@admin.register(models.Pernyataan)
class PernyataanAdmin(admin.ModelAdmin):
    list_display = ["id", "judul"]


@admin.register(models.Topik)
class TopikAdmin(admin.ModelAdmin):
    list_display = ["judul", "created_at"]


@admin.register(models.Kolaborator)
class KolaboratorAdmin(admin.ModelAdmin):
    list_display = ["nama", "wa", "email"]


@admin.register(models.Reviewer)
class ReviewerAdmin(admin.ModelAdmin):
    form = forms.ReviewerForm
    # exclude = ("passphrase",)
    list_display = ["nama", "jabatan", "instansi", "username"]
