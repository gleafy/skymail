from django.core.management.base import BaseCommand
from mailings.models import Mailing, MailingAttempt
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int)

    def handle(self, *args, **options):
        mid = options["mailing_id"]
        mailing = Mailing.objects.get(pk=mid)
        recipients = list(mailing.recipients.values_list("email", flat=True))
        try:
            subject = mailing.message.subject
            body = mailing.message.body
            sent = send_mail(subject, body, settings.SERVER_EMAIL or None, recipients)
            status = MailingAttempt.STATUS_SUCCESS if sent else MailingAttempt.STATUS_FAILED
            response = f"sent_count={sent}"
        except Exception as e:
            status = MailingAttempt.STATUS_FAILED
            response = str(e)
        MailingAttempt.objects.create(mailing=mailing, status=status, response=response)
        if status == MailingAttempt.STATUS_SUCCESS:
            mailing.status = Mailing.STATUS_RUNNING
            mailing.save()
        self.stdout.write("done")
