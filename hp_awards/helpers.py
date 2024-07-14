from django.core.mail import EmailMultiAlternatives
from django.db.models import Func
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import threading


class Round(Func):
    function = "ROUND"
    arity = 2


def kirim_konfirmasi_submisi(submisi):
    def _kirim(submisi):
        recipient_list = [submisi.email]

        context = {
            "submisi": submisi,
        }

        html_content = render_to_string("hp_awards/mail/welcome.html", context)
        text_content = strip_tags(html_content)  # Optional: Plain text version

        # Create email object with MultiAlternatives
        email = EmailMultiAlternatives(
            subject="Submisi Abstrak SiBijaKs Awards 2024",
            body=text_content,
            from_email="sibijaksawards@gmail.com",
            to=recipient_list,
            cc=[
                # "sibijaksawards@gmail.com",
                "healthpolicyawards@gmail.com",
                "perpustakaanbkpk@gmail.com",
                # "gottfriedcpn@gmail.com",
            ],
        )
        email.attach_alternative(html_content, "text/html")  # Attach HTML version

        # Send the email
        email.send()

    try:
        thread = threading.Thread(target=_kirim, args=(submisi,))
        thread.start()
    except:
        return False
    return True


def kirim_pertanyaan_pengunjung(nama: str, email: str, pertanyaan: str):
    def _kirim(nama, email, pertanyaan):
        # recipient_list = ["sibijaksawards@gmail.com"]
        recipient_list = ["sibijaksawards@gmail.com", "healthpolicyawards@gmail.com"]

        # context = {}

        # html_content = render_to_string("hp_awards/mail/pertanyaan.html", context)
        # text_content = strip_tags(html_content)  # Optional: Plain text version

        # Create email object with MultiAlternatives
        email = EmailMultiAlternatives(
            subject=f"Pertanyaan dari {nama}",
            body=strip_tags(pertanyaan),
            from_email="sibijaksawards@gmail.com",
            reply_to=(email,),
            to=recipient_list,
            cc=[
                "gottfriedcpn@gmail.com",
            ],
        )
        # email.attach_alternative(html_content, "text/html")  # Attach HTML version

        # Send the email
        email.send()

    try:
        thread = threading.Thread(target=_kirim, args=(nama, email, pertanyaan))
        thread.start()
    except Exception as e:
        # print(e)
        return False
    return True
