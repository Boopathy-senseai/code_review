from django.conf import settings
from django.core.mail import EmailMessage


class Mailer:
    def send(mail_to, mail_from, subject, body, content_type="text"):
        email = EmailMessage(
            subject,
            body,
            mail_from,
            [mail_to],
        )

        email.fail_silently = False
        email.content_subtype = content_type
        return email.send()
