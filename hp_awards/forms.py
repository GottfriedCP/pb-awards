from django import forms

from .models import Submisi


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
