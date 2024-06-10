from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FormPendaftaran, FormPenugasanJuri
from .models import Pernyataan, Submisi, Reviewer


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


def policy_questions(request):
    return render(
        request,
        "hp_awards/policy_questions.html",
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
                # hanya create kolabo jika ada nama kolabo-nya
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
        "form_has_errors": form.errors,
        "pernyataans": Pernyataan.objects.all(),
        "page_title": "home",
        "hide_registration_navbar": True,
    }
    return render(request, "hp_awards/registrasi.html", context)


def list_submisi(request):
    context = {
        "page_title": "informasi",
    }
    # jika user adalah staf/admin
    if request.user.is_staff:
        context["submisis"] = Submisi.objects.all().order_by("kategori_pendaftar")

    # jika user adalah peserta
    if request.user.is_authenticated and request.session.get("role") == "user":
        wa = request.session.get("wa")
        email = request.session.get("email")
        submisis = Submisi.objects.filter(wa=wa, email=email)
        context["submisis"] = submisis

    # jika user adalah reviewer
    if request.user.is_authenticated and request.session.get("role") == "reviewer":
        submisis = Submisi.objects.prefetch_related("reviewers").filter(
            reviewers__username=request.session.get("username_reviewer")
        )
        context["submisis"] = submisis
        return render(request, "hp_awards/list_submisi_reviewer.html", context)

    if request.method == "POST":
        # handle POST dari form
        wa = request.POST.get("wa")
        email = request.POST.get("email")
        if Submisi.objects.filter(wa=wa, email=email).exists():
            submisis = Submisi.objects.filter(wa=wa, email=email)
            # log in sebagai generic user
            user = authenticate(request, username="user", password="user")
            if user is not None:
                login(request, user)
                request.session["role"] = "user"
                request.session["wa"] = wa
                request.session["email"] = email
            context["submisis"] = submisis
    return render(request, "hp_awards/list_submisi.html", context)


@login_required
def detail_submisi(request, id_submisi):
    submisi = get_object_or_404(Submisi, kode_submisi=id_submisi)
    context = {
        "submisi": submisi,
        "submisi_class": Submisi,
    }
    if request.user.is_staff:
        context["form_penugasan_juri"] = FormPenugasanJuri(instance=submisi)
        context["reviewers"] = Reviewer.objects.all().order_by("nama")
        # NOTE handle post di view func lain
    if request.session.get("role", False) == "reviewer":
        return render(request, "hp_awards/detail_submisi_reviewer.html", context)    
    return render(request, "hp_awards/detail_submisi.html", context)


def edit_submisi(request, id_submisi):
    # NOTE redir dulu yaa
    return redirect("hp_awards:home")
    submisi_manager = Submisi.objects.prefetch_related("kolaborators")
    submisi = get_object_or_404(submisi_manager, kode_submisi=id_submisi)
    form = FormPendaftaran(instance=submisi)
    if request.method == "POST":
        form = FormPendaftaran(request.POST, instance=submisi)
        if form.is_valid():
            submisi = form.save()
            # set kolaborators ke m2m rel
            zip_kolabs = zip(
                request.POST.getlist("kolab-nama"),
                request.POST.getlist("kolab-wa"),
                request.POST.getlist("kolab-email"),
            )
            # utk edit, hapus kolabos yang sudah ada
            _ = submisi.kolaborators.all().delete()
            submisi.kolaborators.clear()
            for nama_kolab, wa_kolab, email_kolab in zip_kolabs:
                # hanya create kolabo jika ada nama kolabo-nya
                if nama_kolab:
                    _ = submisi.kolaborators.create(
                        nama=nama_kolab, wa=wa_kolab, email=email_kolab
                    )
            return redirect("hp_awards:detail_submisi", submisi.kode_submisi)
    context = {
        "form": form,
        "submisi": submisi,
    }
    return render(request, "hp_awards/edit_submisi.html", context)


@login_required
def gugur_submisi(request):
    if request.method == "POST":
        kode_submisi = request.POST.get("kode_submisi")
        submisi = get_object_or_404(Submisi, kode_submisi=kode_submisi)
        submisi.status = Submisi.GUGUR
        submisi.save()
    return redirect("hp_awards:list_submisi")


@login_required
def tetapkan_reviewer(request, id_submisi):
    context = {}
    if request.method == "POST":
        submisi = get_object_or_404(Submisi, kode_submisi=id_submisi)
        form_penugasan_juri = FormPenugasanJuri(request.POST, instance=submisi)
        if form_penugasan_juri.is_valid():
            submisi = form_penugasan_juri.save()
            if submisi.reviewers.count() > 0:
                submisi.status = Submisi.IN_REVIEW
                submisi.save()
            return redirect("hp_awards:detail_submisi", submisi.kode_submisi)
        context["form_penugasan_juri"] = form_penugasan_juri
    return render(request, "hp_awards/detail_submisi.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("hp_awards:home")
    user = None
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        role = request.POST["role"]
        if role == "reviewer":
            # masuk sebagai reviewer
            # cek apa ada Reviewer dengan u dan p yang sudah ada
            if Reviewer.objects.filter(username=username, passphrase=password).exists():
                user = authenticate(request, username="reviewer", password="reviewer")
        else:
            user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session["role"] = "reviewer" if role == "reviewer" else "admin"
            request.session["username_reviewer"] = (
                Reviewer.objects.get(username=username, passphrase=password).username
                if role == "reviewer"
                else None
            )
            return redirect("hp_awards:list_submisi")

    return render(request, "hp_awards/login.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("hp_awards:home")
