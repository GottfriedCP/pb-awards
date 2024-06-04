from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from . import models

admin.site.site_header = "Administrasi Konten Lomba PB"
admin.site.site_title = "HP Awards"
admin.site.index_title = "Beranda"


@admin.register(models.Pernyataan)
class PernyataanAdmin(admin.ModelAdmin):
    list_display = ["id", "judul"]


@admin.register(models.Topik)
class TopikAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Reviewer)
class ReviewerAdmin(admin.ModelAdmin):
    exclude = ("passphrase",)
