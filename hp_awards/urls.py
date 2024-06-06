from django.urls import path
from . import views

app_name = "hp_awards"
urlpatterns = [
    path("", views.home, name="home"),
    path("umum/", views.home_umum, name="umum"),
    path("mahasiswa/", views.home_mahasiswa, name="mahasiswa"),
    path("syarat-peserta/", views.syarat_peserta, name="syarat_peserta"),
    path("prinsip/", views.prinsip, name="prinsip"),
    path("policy-questions/", views.policy_questions, name="policy_questions"),
    path("registrasi/", views.registrasi, name="registrasi"),
    path("list-submisi/", views.list_submisi, name="list_submisi"),
    path("submisi/<str:id_submisi>/", views.detail_submisi, name="detail_submisi"),
    path("submisi/<str:id_submisi>/edit/", views.edit_submisi, name="edit_submisi"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
