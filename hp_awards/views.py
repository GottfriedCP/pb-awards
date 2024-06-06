from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FormPendaftaran
from .models import Pernyataan, Submisi


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
        if form.is_valid():
            submisi = form.save(commit=True)
            # set kolaborators ke m2m rel
            zip_kolabs = zip(
                request.POST.getlist("kolab-nama"),
                request.POST.getlist("kolab-wa"),
                request.POST.getlist("kolab-email"),
            )
            for nama_kolab, wa_kolab, email_kolab in zip_kolabs:
                if nama_kolab:
                    _ = submisi.kolaborators.create(
                        nama=nama_kolab, wa=wa_kolab, email=email_kolab
                    )
            context = {
                "wa": submisi.wa,
                "email": submisi.email,
            }
            return render(request, "hp_awards/registrasi_sukses.html", context)
    context = {
        "form": form,
        "pernyataans": Pernyataan.objects.all(),
        "page_title": "home",
        "hide_registration_navbar": True,
    }
    return render(request, "hp_awards/registrasi.html", context)


def list_submisi(request):
    context = {}
    if request.method == "POST":
        wa = request.POST.get("wa")
        email = request.POST.get("email")
        if Submisi.objects.filter(wa=wa, email=email).exists():
            submisi = Submisi.objects.get(wa=wa, email=email)
            context["submisis"] = [submisi]
    return render(request, "hp_awards/list_submisi.html", context)


def detail_submisi(request, id_submisi):
    submisi = get_object_or_404(Submisi, kode_submisi=id_submisi)
    context = {
        "submisi": submisi,
    }
    return render(request, "hp_awards/detail_submisi.html", context)


def edit_submisi(request, id_submisi):
    submisi = get_object_or_404(Submisi, kode_submisi=id_submisi)
    form = FormPendaftaran(instance=submisi)
    if request.method == "POST":
        form = FormPendaftaran(request.POST, instance=submisi)
        if form.is_valid():
            submisi = form.save()
            return redirect("hp_awards:detail_submisi", submisi.kode_submisi)
    context = {
        "form": form,
    }
    return render(request, "hp_awards/edit_submisi.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("hp_awards:home")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("hp_awards:home")

    return render(request, "hp_awards/login.html")


def logout_view(request):
    logout(request)
    return redirect("hp_awards:home")
