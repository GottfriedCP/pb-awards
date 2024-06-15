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
