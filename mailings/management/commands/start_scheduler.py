from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from mailings.models import Mailing
from django.utils import timezone
from django.core.management import call_command


class Command(BaseCommand):
    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")

        def check_mailings():
            now = timezone.now()
            for mailing in Mailing.objects.filter(status=Mailing.STATUS_CREATED, start_at__lte=now, end_at__gte=now):
                call_command("send_mailing", mailing.id)

        scheduler.add_job(check_mailings, "interval", minutes=1, id="check_mailings", replace_existing=True)
        scheduler.start()
        self.stdout.write("Scheduler started")
        try:
            import time

            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            scheduler.shutdown()
