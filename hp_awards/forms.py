from django import forms
from django.core.exceptions import ValidationError

from .models import Submisi, Reviewer


class FormPendaftaran(forms.ModelForm):
    class Meta:
        model = Submisi
        fields = [
            "nama",
            # "nik",
            "wa",
            "email",
            "pendidikan",
            "kategori_pendaftar",
            "afiliasi",
            # "topik",
            "policy_questions",
            "judul_pb",
            "abstrak_pb",
            "swafoto",
            "ktm",
        ]

    def clean(self):
        cleaned_data = super().clean()
        kategori_pendaftar = cleaned_data.get("kategori_pendaftar")
        ktm = cleaned_data.get("ktm")

        if kategori_pendaftar == Submisi.MAHASISWA and not ktm:
            raise ValidationError(
                "Kategori mahasiswa harus menyertakan KTM atau surket mahasiswa"
            )


class FormPenugasanJuri(forms.ModelForm):
    class Meta:
        model = Submisi
        fields = ["reviewers"]


class ReviewerForm(forms.ModelForm):
    # tidak perlu ada Meta karena
    # sejauh ini Form ini hanya untuk situs admin

    def clean_username(self):
        username = self.cleaned_data["username"]
        duplicate_found = Reviewer.objects.filter(username=username).exists()
        if duplicate_found and self.instance.pk is None:
            raise ValidationError("Reviewer dengan username yang sama sudah ada.")
        return username
