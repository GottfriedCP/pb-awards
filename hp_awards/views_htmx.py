from django.db.models import Count
from django.shortcuts import render

from .models import Submisi


def get_stats(request):
    context = {}
    mhs = Submisi.MAHASISWA
    umum = Submisi.UMUM
    submisis = Submisi.objects.prefetch_related("kolaborators").all()
    submisis = submisis.annotate(jumlah_kolaborator=Count("kolaborators"))
    context["jumlah_submisi"] = submisis.count()
    context["kategori_mhs_indiv"] = submisis.filter(
        kategori_pendaftar=mhs, jumlah_kolaborator=0
    ).count()
    context["kategori_mhs_tim"] = submisis.filter(
        kategori_pendaftar=mhs, jumlah_kolaborator__gt=0
    ).count()
    context["kategori_umum_indiv"] = submisis.filter(
        kategori_pendaftar=umum, jumlah_kolaborator=0
    ).count()
    context["kategori_umum_tim"] = submisis.filter(
        kategori_pendaftar=umum, jumlah_kolaborator__gt=0
    ).count()
    return render(request, "hp_awards/htmx/stats.html", context)
