from django.shortcuts import render

from .models import Submisi


def get_stats(request):
    context = {}
    mhs = Submisi.MAHASISWA
    umum = Submisi.UMUM
    submisis = Submisi.objects.prefetch_related("kolaborators").all()
    context["jumlah_submisi"] = submisis.count()
    context["kategori_mhs_indiv"] = submisis.filter(kategori_pendaftar=mhs, kolaborators__isnull=True).count()
    context["kategori_mhs_tim"] = submisis.filter(kategori_pendaftar=mhs, kolaborators__isnull=False).count()
    context["kategori_umum_indiv"] = submisis.filter(kategori_pendaftar=umum, kolaborators__isnull=True).count()
    context["kategori_umum_tim"] = submisis.filter(kategori_pendaftar=umum, kolaborators__isnull=False).count()
    return render(request, "hp_awards/htmx/stats.html", context)
