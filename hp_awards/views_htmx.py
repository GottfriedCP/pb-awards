from django.db.models import Count
from django.shortcuts import render

from .models import Submisi, Reviewer

import decimal


def get_stats(request):
    ctx = decimal.getcontext()
    ctx.rounding = decimal.ROUND_HALF_UP
    context = {}
    mhs = Submisi.MAHASISWA
    umum = Submisi.UMUM
    submisis = Submisi.objects.prefetch_related("kolaborators").all()
    submisis = submisis.annotate(jumlah_kolaborator=Count("kolaborators"))
    # Naskah masuk
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
    context["naskah_eligible"] = submisis.filter(reviewers__isnull=False).count()

    # Juri dan penilaian
    juris = Reviewer.objects.prefetch_related("penilaians").all()
    jumlah_juri = juris.count()
    juri_selesai = 0
    for j in juris:
        if j.penilaians.count() == j.penilaians.filter(nilai1__gt=0).count():
            juri_selesai += 1
    context["jumlah_juri"] = jumlah_juri
    context["juri_selesai"] = juri_selesai
    context["progress_juri"] = (
        juri_selesai / jumlah_juri * 100.00 if jumlah_juri > 0 else 0.0
    )
    return render(request, "hp_awards/htmx/stats.html", context)
