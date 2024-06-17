from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import threading


def send_welcome_email(submisi):
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
    )
    email.attach_alternative(html_content, "text/html")  # Attach HTML version

    # Send the email
    email.send()


def send_welcome_email_async(submisi):
    try:
        thread = threading.Thread(target=send_welcome_email, args=(submisi,))
        thread.start()
    except:
        return False
    return True


def kirim_pertanyaan_pengunjung(nama: str, email: str, pertanyaan: str):
    def _send(nama, email, pertanyaan):
        # recipient_list = ["sibijaksawards@gmail.com"]
        recipient_list = ["gottfriedcpn@gmail.com"]

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
        )
        # email.attach_alternative(html_content, "text/html")  # Attach HTML version

        # Send the email
        email.send()

    try:
        thread = threading.Thread(target=_send, args=(nama, email, pertanyaan))
        thread.start()
    except Exception as e:
        print(e)
        return False
    return True
