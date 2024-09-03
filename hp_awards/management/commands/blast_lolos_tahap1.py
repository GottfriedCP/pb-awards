from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from hp_awards.models import Submisi


class Command(BaseCommand):
    help = "Blast email lolos tahap 1 ke tahap 2"

    # def add_arguments(self, parser):
    #     parser.add_argument("poll_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        # raise CommandError('Poll "%s" does not exist' % poll_id)
        # lolos-ke-tahap2.html
        submisis = Submisi.objects.filter(status=Submisi.TUNGGU2)
        emails = []
        n = 0
        for s in submisis:
            if s.email not in emails:
                emails.append(s.email)
        for email in emails:
            submisi_loloss = Submisi.objects.filter(email=email, status=Submisi.TUNGGU2)
            context = {
                "nama": submisi_loloss.first().nama,
                "wa": submisi_loloss.first().wa,
                "email": email,
                "submisis": submisi_loloss,
            }
            html_content = render_to_string("hp_awards/mail/lolos-ke-tahap2.html", context)
            text_content = strip_tags(html_content)  # Optional: Plain text version

            # Create email object with MultiAlternatives
            mail = EmailMultiAlternatives(
                subject="SiBijaKs Awards 2024 | Segera Unggah Naskah untuk Tahap 2",
                body=text_content,
                from_email="healthpolicyawards@gmail.com",
                to=[email],
                cc=[
                    # "healthpolicyawards@gmail.com",
                    # "perpustakaanbkpk@gmail.com",
                    "gottfriedcpn@gmail.com",
                ] if n == 1 else [],
            )
            mail.attach_alternative(html_content, "text/html")  # Attach HTML version

            # Send the email
            mail.send()
            self.stdout.write(self.style.SUCCESS(f"mengirim email ke {n}"))
            n += 1
        self.stdout.write(
            self.style.SUCCESS(f"{n} email terkirim")
        )