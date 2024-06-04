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


def registrasi(request):
    form = FormPendaftaran()
    if request.method == "POST":
        form = FormPendaftaran(request.POST, request.FILES)
        if form.is_valid():
            print("OK")
            return render(request, "hp_awards/registrasi_sukses.html", )
    context = {
        "form": form,
        "pernyataans": Pernyataan.objects.all(),
        "page_title": "home",
    }
    return render(request, "hp_awards/registrasi.html", context)
