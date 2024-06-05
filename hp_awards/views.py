from django.http import Http404, HttpResponse
from django.shortcuts import render

from .forms import FormPendaftaran
from .models import Pernyataan


def home(request):
    context = {
        "page_title": "home",
    }
    return render(request, "hp_awards/home.html", context)


def home_umum(request):
    context = {
        "page_title": "umum",
    }
    return render(request, "hp_awards/home_umum.html", context)


def home_mahasiswa(request):
    context = {
        "page_title": "mahasiswa",
    }
    return render(request, "hp_awards/home_mahasiswa.html", context)


def syarat_peserta(request):
    return render(
        request,
        "hp_awards/syarat_peserta.html",
        {
            "page_title": "informasi",
        },
    )


def prinsip(request):
    return render(
        request,
        "hp_awards/prinsip.html",
        {
            "page_title": "informasi",
        },
    )


def registrasi(request):
    form = FormPendaftaran()
    if request.method == "POST":
        form = FormPendaftaran(request.POST, request.FILES)
        kolaborator_namas = request.POST.getlist("kolab-nama")
        kolaborator_was = request.POST.getlist("kolab-wa")
        print(kolaborator_namas)
        print(kolaborator_was)
        if form.is_valid():
            print("OK")
            return render(
                request,
                "hp_awards/registrasi_sukses.html",
            )
    context = {
        "form": form,
        "pernyataans": Pernyataan.objects.all(),
        "page_title": "home",
        "hide_registration_navbar": True,
    }
    return render(request, "hp_awards/registrasi.html", context)
