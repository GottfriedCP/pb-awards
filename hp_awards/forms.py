from django import forms

from .models import Submisi


class FormPendaftaran(forms.ModelForm):
    class Meta:
        model = Submisi
        fields = [
            "nama",
            "nik",
            "wa",
            "email",
            "pendidikan",
            "afiliasi",
            "kategori_pendaftar",
            # "topik",
            "judul_pb",
            "abstrak_pb",
            "swafoto",
        ]
