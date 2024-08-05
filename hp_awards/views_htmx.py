from django.db.models import Count, F, Q, Case, When, BooleanField
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
    context["naskah_tahap2"] = submisis.filter(status=Submisi.TUNGGU2).count()
    context["naskah_tahap2_lengkap"] = submisis.filter(
        status=Submisi.TUNGGU2, file_pb_pdf__isnull=False
    ).exclude(file_pb_pdf__exact="").count()

    # Juri dan penilaian
    juris = Reviewer.objects.prefetch_related("penilaians").exclude(
        nama__icontains="juri"
    )
    jumlah_juri = (
        juris.annotate(penugasan=Count("penilaians")).filter(penugasan__gt=0).count()
    )
    juri_selesai = 0
    for j in juris:
        if (
            j.penilaians.count() > 0
            and j.penilaians.count() == j.penilaians.filter(nilai2__gt=0).count()
        ):
            juri_selesai += 1
    context["jumlah_juri"] = jumlah_juri
    context["juri_selesai"] = juri_selesai
    context["progress_juri"] = (
        juri_selesai / jumlah_juri * 100.00 if jumlah_juri > 0 else 0.0
    )
    # TABEL PROGRESS JURI
    juris = juris.annotate(penilaian_ditugaskan=Count("penilaians"))
    juris = juris.annotate(
        penilaian_selesai=Count("penilaians", filter=Q(penilaians__nilai2__gt=0))
    )
    juris = juris.annotate(
        selesai=Case(
            When(penilaian_ditugaskan=F("penilaian_selesai"), then=True),
            default=False,
            output_field=BooleanField(),
        )
    )
    context["juris"] = juris
    return render(request, "hp_awards/htmx/stats.html", context)
