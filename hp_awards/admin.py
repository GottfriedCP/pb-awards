from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from . import forms, models

admin.site.site_header = "Administrasi Konten Lomba PB"
admin.site.site_title = "HP Awards"
admin.site.index_title = "Beranda"


def gugurkan_naskah(modeladmin, request, queryset):
    for obj in queryset:
        obj.status = models.Submisi.GUGUR
        obj.save()


gugurkan_naskah.short_description = "Gugurkan Naskah"


@admin.register(models.Submisi)
class SubmisiAdmin(admin.ModelAdmin):
    list_display = ["nama", "kategori_pendaftar", "created_at", "status", "judul_pb"]
    list_filter = ["status", "kategori_pendaftar"]
    filter_horizontal = ["kolaborators"]
    search_fields = ["nama", "judul_pb"]
    actions = [gugurkan_naskah]


@admin.register(models.Pernyataan)
class PernyataanAdmin(admin.ModelAdmin):
    list_display = ["id", "judul"]


@admin.register(models.Topik)
class TopikAdmin(admin.ModelAdmin):
    list_display = ["judul", "created_at"]


@admin.register(models.PolicyQuestion)
class PolicyQuestionAdmin(admin.ModelAdmin):
    list_display = ["judul", "sumber", "created_at"]


@admin.register(models.Kolaborator)
class KolaboratorAdmin(admin.ModelAdmin):
    list_display = ["nama", "wa", "email"]


@admin.register(models.Reviewer)
class ReviewerAdmin(admin.ModelAdmin):
    form = forms.ReviewerForm
    # exclude = ("passphrase",)
    list_display = ["nama", "jabatan", "instansi", "username"]
    search_fields = ["nama", "username"]


def reset_nilai_abstrak(modeladmin, request, queryset):
    for obj in queryset:
        obj.nilai1 = 0
        obj.string_nilai1 = None
        obj.save()


def reset_nilai_pb(modeladmin, request, queryset):
    for obj in queryset:
        obj.nilai2 = 0
        obj.string_nilai2 = None
        obj.save()


reset_nilai_abstrak.short_description = "Reset nilai abstrak dari juri terpilih"
reset_nilai_pb.short_description = "Reset nilai PB dari juri terpilih"


@admin.register(models.Penilaian)
class PenilaianAdmin(admin.ModelAdmin):
    list_display = ["submisi", "reviewer", "nilai1", "nilai2", "nilai3"]
    list_filter = ["reviewer__nama"]
    search_fields = ["reviewer"]
    actions = [reset_nilai_abstrak, reset_nilai_pb]
