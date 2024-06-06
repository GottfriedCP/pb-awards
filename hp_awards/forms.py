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
            "topik",
            "judul_pb",
            "abstrak_pb",
            "swafoto",
        ]


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
