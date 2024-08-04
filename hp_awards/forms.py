from django import forms
from django.core.exceptions import ValidationError

from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

from .models import Submisi, Reviewer, PolicyQuestion


class FormCaptcha(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaV3)


class FormPendaftaran(forms.ModelForm):
    policy_question = forms.ModelChoiceField(
        queryset=PolicyQuestion.objects.order_by("id")
    )

    class Meta:
        model = Submisi
        fields = [
            "nama",
            "wa",
            "email",
            "kategori_pendaftar",
            "pendidikan",
            "pekerjaan",
            "afiliasi",
            # "topik",
            "policy_question",
            "policy_question_custom",
            # "swafoto",  # tidak pada saat registrasi awal
            "ktm",
            "judul_pb",
            "abstrak_pb",
        ]

    def clean(self):
        cleaned_data = super().clean()
        kategori_pendaftar = cleaned_data.get("kategori_pendaftar")
        ktm = cleaned_data.get("ktm")
        pekerjaan = cleaned_data.get("pekerjaan")
        # Mahasiswa butuh KTM/surket mhs
        if (kategori_pendaftar in (Submisi.MAHASISWA, Submisi.MAHASISWA2)) and not ktm:
            self.add_error(
                "ktm",
                "Kategori Mahasiswa harus menyertakan KTM atau surket mahasiswa",
            )

        # Umum harus mengisi kolom pekerjaan
        if kategori_pendaftar == Submisi.UMUM and not pekerjaan:
            self.add_error(
                "pekerjaan",
                "Kategori Umum harus mengisi nama profesi",
            )

        policy_question = cleaned_data.get("policy_question")
        policy_question_custom = cleaned_data.get("policy_question_custom")
        if (
            policy_question == PolicyQuestion.objects.get(pk=1)
            and not policy_question_custom
        ):
            self.add_error(
                "policy_question_custom",
                "Anda harus menuliskan Policy Question Anda jika memilih 'Lainnya'",
            )


class FormPenugasanJuri(forms.ModelForm):
    class Meta:
        model = Submisi
        fields = ["reviewers"]
        labels = {
            "reviewers": "Juri ditugaskan:",
        }


class FormUnggahFulltext(forms.ModelForm):
    class Meta:
        model = Submisi
        fields = ["file_pb_pdf", "file_pb_doc", "file_turnitin", "link_dakung"]
        labels = {
            "file_pb_pdf": "1. File Naskah format PDF",
            "file_pb_doc": "2. File Naskah format DOC/DOCX",
            "file_turnitin": "3. File Bukti Bebas Plagiarisme (misalnya Turnitin)",
            "link_dakung": "4. Link Apendiks dan Data Dukung (Jika Ada. Jangan lupa izinkan akses untuk panitia)."
        }


class ReviewerForm(forms.ModelForm):
    # tidak perlu ada Meta karena
    # sejauh ini Form ini hanya untuk situs admin

    def clean_username(self):
        username = self.cleaned_data["username"]
        duplicate_found = Reviewer.objects.filter(username=username).exists()
        if duplicate_found and self.instance.pk is None:
            raise ValidationError("Reviewer dengan username yang sama sudah ada.")
        return username


class FormKontak(forms.Form):
    nama = forms.CharField(label="Nama", max_length=150, required=True)
    email = forms.EmailField(
        required=True, max_length=50, help_text="Kami akan merespon ke alamat email ini"
    )
    wa = forms.CharField(label="Nomor WA", max_length=20, required=False)
    pertanyaan = forms.CharField(required=True, widget=forms.Textarea)
