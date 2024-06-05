from django.urls import path
from . import views

app_name = "hp_awards"
urlpatterns = [
    path("", views.home, name="home"),
    path("umum/", views.home_umum, name="umum"),
    path("mahasiswa/", views.home_mahasiswa, name="mahasiswa"),
    path("syarat-peserta/", views.syarat_peserta, name="syarat_peserta"),
    path("prinsip/", views.prinsip, name="prinsip"),
    path("registrasi/", views.registrasi, name="registrasi"),
]
