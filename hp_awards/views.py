from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import (
    Case,
    When,
    Avg,
    Count,
    F,
    Q,
    FloatField,
    ExpressionWrapper,
    Sum,
)
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bs4 import BeautifulSoup
from openpyxl import Workbook

from .forms import (
    FormPendaftaran,
    FormPenugasanJuri,
    FormCaptcha,
    FormKontak,
    FormUnggahFulltext,
    FormUnggahPPT,
)
from .models import Pernyataan, Submisi, Reviewer
from .helpers import kirim_konfirmasi_submisi, kirim_pertanyaan_pengunjung, Round

from datetime import datetime
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
    now = timezone.localtime()
    tanggal_tutup = timezone.make_aware(datetime(year=2024, month=7, day=21))
    if now >= tanggal_tutup:
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
        submisis = submisis.annotate(total_skor=Sum("penilaians__nilai3"))
        submisis = submisis.annotate(
            reviewer_menilai=Count("penilaians", filter=Q(penilaians__nilai3__gt=0))
        )
        submisis = submisis.annotate(
            rerata_skor=Case(
                When(reviewer_menilai=0, then=0.0),
                default=ExpressionWrapper(
                    F("total_skor") / F("reviewer_menilai"),
                    output_field=FloatField(),
                ),
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
        context["ada_lolos"] = submisis.filter(status=Submisi.TUNGGU3).exists()

    # jika user adalah reviewer
    if request.user.is_authenticated and request.session.get("role") == "reviewer":
        reviewer = Reviewer.objects.prefetch_related(
            "penilaians", "penilaians__submisi"
        ).get(username=request.session["username_reviewer"])
        context["reviewer"] = reviewer
        context["todo_count"] = reviewer.penilaians.filter(
            string_nilai3__isnull=True, submisi__status=Submisi.TUNGGU3
        ).count()
        context["penilaians"] = reviewer.penilaians.filter(
            submisi__status=Submisi.TUNGGU3
        ).order_by("submisi__nama")
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
        email = str(request.POST.get("email")).lower()
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
            context["ada_lolos"] = submisis.filter(status=Submisi.TUNGGU3).exists()
    return render(request, "hp_awards/list_submisi.html", context)


@login_required
def detail_submisi(request, id_submisi):
    submisi = get_object_or_404(Submisi, kode_submisi=id_submisi)
    context = {
        "submisi": submisi,
        "submisi_class": Submisi,
        "form_naskah": FormUnggahPPT(instance=submisi),
    }
    try:
        url_pb_pdf = f"{request.scheme}://{request.get_host()}{submisi.file_pb_pdf.url}"
        url_pb_ppt = f"{request.scheme}://{request.get_host()}{submisi.file_pb_ppt.url}"
    except:
        url_pb_pdf = ""
        url_pb_ppt = ""
    context["url_pb_pdf"] = url_pb_pdf
    context["url_pb_ppt"] = url_pb_ppt

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
def unggah_naskah(request):
    if request.method == "POST":
        kode_submisi = request.POST.get("kode_submisi")
        submisi = get_object_or_404(Submisi, kode_submisi=kode_submisi)
        form = FormUnggahPPT(request.POST, request.FILES, instance=submisi)
        if form.is_valid():
            submisi = form.save()
        # return redirect("hp_awards:detail_submisi", submisi.kode_submisi)
        context = {
            "submisi": submisi,
            "form_naskah": form,
        }
        return render(request, "hp_awards/htmx/form-unggah-naskah.html", context)
    return redirect("hp_awards:list_submisi")


@login_required
def gugur_submisi(request):
    if request.method == "POST":
        kode_submisi = request.POST.get("kode_submisi")
        submisi = get_object_or_404(Submisi, kode_submisi=kode_submisi)
        submisi.status = Submisi.TUNGGU2
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
            # if submisi.reviewers.count() > 0:
            #     submisi.status = Submisi.TUNGGU2
            #     submisi.save()
            # else:
            #     submisi.status = Submisi.TUNGGU2
            #     submisi.save()
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
        penilaian = reviewer.penilaians.get(submisi=submisi)
        string_nilai3_list = []
        nilai_komp1 = request.POST["1"]
        nilai_komp2 = request.POST["2"]
        nilai_komp3 = request.POST["3"]
        nilai3 = int(nilai_komp1) + int(nilai_komp2) + int(nilai_komp3)
        string_nilai3_list.append(nilai_komp1)
        string_nilai3_list.append(nilai_komp2)
        string_nilai3_list.append(nilai_komp3)
        penilaian.nilai3 = nilai3
        if request.session.get("kemkes", False):
            nilai_komp4 = request.POST["a1"]
            string_nilai3_list.append(nilai_komp4)
        else:
            string_nilai3_list.append("-")
        penilaian.string_nilai3 = "|".join(string_nilai3_list)
        # print(penilaian.nilai3)
        # print(penilaian.string_nilai3)
        penilaian.save()

        # PB
        # string_nilai2_list = []
        # for i in range(1, 15):
        #     string_nilai2_list.append(request.POST[f"{i}"])

        # # print(penilaian.string_nilai2)
        # i1 = int(request.POST["1"]) / 2.00
        # i2 = int(request.POST["2"]) / 2.00
        # i3 = int(request.POST["3"]) * 1.00
        # i4 = int(request.POST["4"]) * 1.00
        # i5 = int(request.POST["5"]) * 2.00
        # i6 = int(request.POST["6"]) * 2.00
        # i7 = int(request.POST["7"]) * 1.50
        # i8 = int(request.POST["8"]) * 1.50
        # i9 = int(request.POST["9"]) * 1.50
        # i10 = int(request.POST["10"]) * 1.50
        # i11 = int(request.POST["11"]) * 1.75
        # i12 = int(request.POST["12"]) * 1.75
        # i13 = int(request.POST["13"]) * 1.75
        # i14 = int(request.POST["14"]) * 1.75
        # # Perlakuan khusus dimensi B3
        # if string_nilai2_list[2] != "5":
        #     string_nilai2_list[3] = "-"
        #     i4 = 0.00
        # penilaian.nilai2 = (
        #     i1 + i2 + i3 + i4 + i5 + i6 + i7 + i8 + i9 + i10 + i11 + i12 + i13 + i14
        # )
        # penilaian.string_nilai2 = "|".join(string_nilai2_list)
        # penilaian.save()

        # ABSTRAK
        # id_submisi = request.POST["id_submisi"]
        # submisi = Submisi.objects.get(kode_submisi=id_submisi)

        # nilai_inovatif = int(request.POST["inovatif"])
        # nilai_aplikatif = int(request.POST["aplikatif"])
        # nilai_kritis = int(request.POST["kritis"])
        # nilai1 = nilai_inovatif + nilai_aplikatif + nilai_kritis
        # string_nilai1 = f"{nilai_inovatif}|{nilai_aplikatif}|{nilai_kritis}"

        # penilaian = reviewer.penilaians.get(submisi=submisi)
        # penilaian.nilai1 = nilai1
        # penilaian.string_nilai1 = string_nilai1
        # penilaian.save()
    return redirect("hp_awards:list_submisi")


@login_required
def unduh_hasil_penilaian_abstrak(request):
    def _get_rerata_skor_manfaat(skors_manfaat):
        _count = 0
        _total = 0
        for s in skors_manfaat:
            try:
                _total += int(s)
                _count += 1
            except:
                pass
        if _count > 0:
            return _total / _count * 1.0
        return "-"

    JUMLAH_JURI = 10

    if request.method == "POST":
        submisis = Submisi.objects.prefetch_related(
            "reviewers", "penilaians", "kolaborators"
        )
        # hanya unduh yg ada PB-nya
        submisis = submisis.filter(file_pb_pdf__isnull=False)
        # submisis = submisis.annotate(total_skor_abstrak=Sum("penilaians__nilai1"))
        submisis = submisis.annotate(total_skor_pb=Sum("penilaians__nilai3"))
        submisis = submisis.annotate(
            reviewer_menilai=Count("penilaians", filter=Q(penilaians__nilai3__gt=0))
        )
        submisis = submisis.annotate(
            rerata_skor_pb=Case(
                When(Q(reviewer_menilai=0), then=0.0),
                default=ExpressionWrapper(
                    F("total_skor_pb") / F("reviewer_menilai"),
                    output_field=FloatField(),
                ),
            )
        )
        submisis = submisis.all().order_by("-created_at", "kategori_pendaftar")

        wb = Workbook()
        ws = wb.active

        # Judul kolom
        header_row = [
            "No. Urut",
            "Kode Submisi",
            "Judul",
            "Abstrak",
            "Penulis Utama",
            "Kategori",
            "Individu/Tim",
        ]
        header_row.extend(
            ["WA", "Email", "Pekerjaan", "Instansi / Perguruan Tinggi", "Pendidikan"]
        )
        header_row.extend(["Tanggal Submisi", "Status", "Nilai Abstrak", "Nilai PB"])
        header_row.extend(["Jumlah Juri", "Juri Sudah Menilai", "Penilaian Lengkap"])
        for i in range(0, JUMLAH_JURI):
            header_row.extend(
                [
                    f"Nama Juri {i+1}",
                    f"Nilai Juri {i+1}",
                    f"Nilai Kebermanfaatan Juri {i+1}",  # khusus tahap 3
                    f"Detail Nilai Juri {i+1}",
                ]
            )
        header_row.extend(
            [
                "Nilai Rata-rata (Tanpa Komponen Manfaat)",
                "Nilai Rata-rata (hanya Komponen Manfaat)",
            ]
        )
        header_row.extend(["Berkas PPT"])
        header_row.extend(["Berkas PB PDF"])
        header_row.extend(["Berkas PB Word"])
        header_row.extend(["Policy Question"])
        ws.append(header_row)

        for s in submisis:
            juris = [p.reviewer.nama for p in s.penilaians.all()]
            skors = [p.nilai3 if p.nilai3 > 0 else "-" for p in s.penilaians.all()]
            detail_skors = [
                p.string_nilai3 if p.string_nilai3 else "-" for p in s.penilaians.all()
            ]
            # Khusus tahap 3
            skors_manfaat = [
                str(p.string_nilai3).split("|")[-1] if p.string_nilai3 else "-"
                for p in s.penilaians.all()
            ]
            rerata_skor_manfaat = _get_rerata_skor_manfaat(skors_manfaat)
            row = [
                s.id,
                str(s.kode_submisi),
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
            row.extend(
                [
                    timezone.make_naive(s.created_at),
                    s.get_status_display(),
                    s.nilai1,
                    s.nilai2,
                ]
            )
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
                ]
            )
            for i in range(0, JUMLAH_JURI):
                row.extend(
                    [
                        juris[i] if len(juris) > i else "-",
                        skors[i] if len(skors) > i else "-",
                        (
                            skors_manfaat[i] if len(skors_manfaat) > i else "-"
                        ),  # khusus tahap 3
                        detail_skors[i] if len(detail_skors) > i else "-",
                    ]
                )
            row.extend([s.rerata_skor_pb or "-", rerata_skor_manfaat])
            row.extend(["Sudah Unggah" if s.file_pb_ppt else "Belum Unggah"])
            if s.file_pb_pdf:
                row.extend([f"{request.scheme}://{request.get_host()}{s.file_pb_pdf.url}"])
            else:
                row.extend(["-"])
            if s.file_pb_doc:
                row.extend([f"{request.scheme}://{request.get_host()}{s.file_pb_doc.url}"])
            else:
                row.extend(["-"])
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
            f"attachment; filename=hasil_nilai-{str(timezone.localtime())}.xlsx"
        )

        wb.save(response)
        return response
    return redirect("hp_awards:list_submisi")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("hp_awards:home")
    form_captcha = FormCaptcha()
    user = None
    if request.method == "POST":
        form_captcha = FormCaptcha(request.POST)
        if form_captcha:
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
                if role == "reviewer":
                    request.session["role"] = "reviewer"
                    request.session["kemkes"] = reviewer.kategori == Reviewer.KEMKES
                else:
                    request.session["role"] = "admin"
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
