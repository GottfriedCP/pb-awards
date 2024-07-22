from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, F, Q, FloatField, ExpressionWrapper, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bs4 import BeautifulSoup
from openpyxl import Workbook

from .forms import FormPendaftaran, FormPenugasanJuri, FormCaptcha, FormKontak
from .models import Pernyataan, Submisi, Reviewer
from .helpers import kirim_konfirmasi_submisi, kirim_pertanyaan_pengunjung, Round

import decimal


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


def tentang(request):
    return render(
        request,
        "hp_awards/tentang.html",
        {
            "page_title": "tentang",
        },
    )


def kontak(request):
    form = FormKontak()
    form_captcha = FormCaptcha()
    if request.method == "POST":
        form_captcha = FormCaptcha(request.POST)
        form = FormKontak(request.POST)
        if form_captcha.is_valid() and form.is_valid():
            nama = form.cleaned_data["nama"]
            email = form.cleaned_data["email"]
            pertanyaan = form.cleaned_data["pertanyaan"]
            kirim_pertanyaan_pengunjung(nama, email, pertanyaan)
            messages.info(request, "Pertanyaan Anda berhasil dikirim")
            form = None

    context = {
        "page_title": "informasi",
        "form": form,
        "form_captcha": form_captcha,
    }
    return render(request, "hp_awards/kontak.html", context)


def policy_questions(request):
    return render(
        request,
        "hp_awards/policy_questions.html",
        {
            "page_title": "informasi",
        },
    )


def registrasi(request):
    # handle pendaftaran jika sudah ditutup
    now = timezone.localdate()
    if now.day > 21 and now.month >= 7 and now.year >= 2024:
        raise Http404("Periode registrasi sudah ditutup.")
    form = FormPendaftaran()
    form_captcha = FormCaptcha()
    if request.method == "POST":
        # verifikasi captcha
        # form_captcha = FormCaptcha(request.POST)
        # if not form_captcha.is_valid():
        #     messages.error(request, "Anda diduga Robot. Coba lagi lain waktu.")
        #     return redirect("hp_awards:registrasi")
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
            kirim_konfirmasi_submisi(submisi=submisi)
            return render(request, "hp_awards/registrasi_sukses.html", context)
    context = {
        "form": form,
        "form_captcha": form_captcha,
        "form_has_errors": form.errors,
        "pernyataans": Pernyataan.objects.all(),
        "page_title": "home",
        "hide_registration_navbar": True,
    }
    return render(request, "hp_awards/registrasi.html", context)


def list_submisi(request):
    context = {
        "page_title": "",
    }
    ctx = decimal.getcontext()
    ctx.rounding = decimal.ROUND_HALF_UP

    # jika user adalah staf/admin
    if request.user.is_staff:
        submisis = Submisi.objects.prefetch_related("reviewers", "penilaians")
        # submisis = submisis.annotate(total_skor_abstrak=Avg("penilaians__nilai1"))
        submisis = submisis.annotate(total_skor_abstrak=Sum("penilaians__nilai1"))
        submisis = submisis.annotate(
            reviewer_menilai=Count(
                "penilaians", filter=Q(penilaians__string_nilai1__isnull=False)
            )
        )
        submisis = submisis.annotate(
            rerata_skor_abstrak=ExpressionWrapper(
                F("total_skor_abstrak") / F("reviewer_menilai"),
                output_field=FloatField(),
            )
        )
        context["submisis"] = submisis.all().order_by(
            "-created_at", "kategori_pendaftar"
        )
        return render(request, "hp_awards/list_submisi_admin.html", context)

    # jika user adalah peserta
    if request.user.is_authenticated and request.session.get("role") == "user":
        wa = request.session.get("wa")
        email = request.session.get("email")
        submisis = Submisi.objects.filter(wa=wa, email=email)
        context["submisis"] = submisis

    # jika user adalah reviewer
    if request.user.is_authenticated and request.session.get("role") == "reviewer":
        reviewer = Reviewer.objects.prefetch_related(
            "penilaians", "penilaians__submisi"
        ).get(username=request.session["username_reviewer"])
        submisis = Submisi.objects.prefetch_related("reviewers").filter(
            reviewers__in=[reviewer], penilaians__reviewer=reviewer
        )
        context["penilaians"] = reviewer.penilaians.all()
        return render(request, "hp_awards/list_submisi_reviewer.html", context)

    form_captcha = FormCaptcha()
    context["form_captcha"] = form_captcha
    if request.method == "POST":
        # handle POST dari form
        # check captcha
        # form_captcha = FormCaptcha(request.POST)
        # if not form_captcha.is_valid():
        #     messages.error(request, "Anda diduga Robot. Coba lagi lain waktu.")
        #     return redirect("hp_awards:list_submisi")
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
                request.session["nama_bar"] = email
            else:
                return HttpResponse("Basic user not found")
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
        return render(request, "hp_awards/detail_submisi_admin.html", context)
        # NOTE handle POST penugasan juri di view func lain
    if request.session.get("role", False) == "reviewer":
        return render(request, "hp_awards/detail_submisi_reviewer.html", context)
    if request.session.get("role", False) == "admin":
        return render(request, "hp_awards/detail_submisi_admin.html", context)
    # default return adalah peserta
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
            else:
                submisi.status = Submisi.TUNGGU
                submisi.save()
            return redirect("hp_awards:detail_submisi", submisi.kode_submisi)
        context["form_penugasan_juri"] = form_penugasan_juri
    return render(request, "hp_awards/detail_submisi.html", context)


@login_required
def tetapkan_nilai(request):
    """Tetapkan nilai abstrak."""
    # asumsikan ini sedang login sebagai reviewer
    reviewer = Reviewer.objects.get(username=request.session["username_reviewer"])

    if request.method == "POST":
        id_submisi = request.POST["id_submisi"]
        submisi = Submisi.objects.get(kode_submisi=id_submisi)

        nilai_inovatif = int(request.POST["inovatif"])
        nilai_aplikatif = int(request.POST["aplikatif"])
        nilai_kritis = int(request.POST["kritis"])
        nilai1 = nilai_inovatif + nilai_aplikatif + nilai_kritis
        string_nilai1 = f"{nilai_inovatif}|{nilai_aplikatif}|{nilai_kritis}"
        # reviewer.penilaians.all().delete()  # DON'T

        penilaian = reviewer.penilaians.get(submisi=submisi)
        penilaian.nilai1 = nilai1
        penilaian.string_nilai1 = string_nilai1
        penilaian.save()
    return redirect("hp_awards:list_submisi")


@login_required
def unduh_hasil_penilaian_abstrak(request):
    if request.method == "POST":
        submisis = Submisi.objects.prefetch_related(
            "reviewers", "penilaians", "kolaborators"
        )
        # submisis = submisis.annotate(
        #     total_skor_abstrak=Round(
        #         Avg("penilaians__nilai1"), 2, output_field=FloatField()
        #     )
        # )
        submisis = submisis.annotate(total_skor_abstrak=Sum("penilaians__nilai1"))
        submisis = submisis.annotate(
            reviewer_menilai=Count(
                "penilaians", filter=Q(penilaians__string_nilai1__isnull=False)
            )
        )
        submisis = submisis.annotate(rerata_skor_abstrak=ExpressionWrapper(F("total_skor_abstrak") / F("reviewer_menilai"), output_field=FloatField(),))
        submisis = submisis.all().order_by("-created_at", "kategori_pendaftar")

        wb = Workbook()
        ws = wb.active

        # Judul kolom
        header_row = ["Judul", "Abstrak", "Penulis Utama", "Kategori", "Individu/Tim"]
        header_row.extend(
            ["WA", "Email", "Pekerjaan", "Instansi / Perguruan Tinggi", "Pendidikan"]
        )
        header_row.extend(["Tanggal Submisi", "Status"])
        header_row.extend(
            [
                "Jumlah Juri",
                "Juri Sudah Menilai",
                "Penilaian Lengkap",
                "Nilai Rata-rata",
            ]
        )
        header_row.extend(["Policy Question"])
        ws.append(header_row)

        for s in submisis:
            row = [
                s.judul_pb,
                BeautifulSoup(s.abstrak_pb, "html.parser").get_text(),
                s.nama,
                s.get_kategori_pendaftar_display(),
                "Tim" if s.kolaborators.exists() else "Individu",
            ]
            row.extend(
                [
                    s.wa,
                    s.email,
                    s.pekerjaan or "-",
                    s.afiliasi or "-",
                    s.pendidikan or "-",
                ]
            )
            row.extend([timezone.make_naive(s.created_at), s.get_status_display()])
            row.extend(
                [
                    s.reviewers.count(),
                    s.reviewer_menilai or "-",
                    (
                        "Ya"
                        if s.reviewers.count() == s.reviewer_menilai
                        and s.reviewers.count() > 0
                        else "Belum"
                    ),
                    s.rerata_skor_abstrak or "-",
                ]
            )
            row.extend(
                [
                    (
                        f"LAINNYA: {s.policy_question_custom}"
                        if s.policy_question.pk == 1
                        else str(s.policy_question)
                    )
                ]
            )
            ws.append(row)
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = (
            f"attachment; filename=hasil_nilai_abstrak-{str(timezone.localtime())}.xlsx"
        )

        wb.save(response)
        return response


def login_view(request):
    if request.user.is_authenticated:
        return redirect("hp_awards:home")
    form_captcha = FormCaptcha()
    user = None
    if request.method == "POST":
        form_captcha = FormCaptcha(request.POST)
        if form_captcha.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            role = request.POST["role"]
            if role == "reviewer":
                # masuk sebagai reviewer
                # cek apa ada Reviewer dengan u dan p yang sudah ada
                if Reviewer.objects.filter(
                    username=username, passphrase=password
                ).exists():
                    reviewer = Reviewer.objects.get(
                        username=username, passphrase=password
                    )
                    user = authenticate(
                        request, username="reviewer", password="reviewer"
                    )
                else:
                    messages.error(request, "Username atau password juri salah")
                    return redirect("hp_awards:login")
            else:
                # masuk sebagai admin
                user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                request.session["role"] = "reviewer" if role == "reviewer" else "admin"
                # nama yg muncul pada navbar kanan atas
                request.session["nama_bar"] = (
                    reviewer.username if role == "reviewer" else user.username
                )
                request.session["username_reviewer"] = (
                    Reviewer.objects.get(
                        username=username, passphrase=password
                    ).username
                    if role == "reviewer"
                    else None
                )
                return redirect("hp_awards:list_submisi")
            else:
                return HttpResponse("Basic admin user not found")

    return render(request, "hp_awards/login.html", {"form_captcha": form_captcha})


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("hp_awards:home")
