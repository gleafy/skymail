from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name="Managers")
        models = ["recipient", "message", "mailing"]
        for model in models:
            app_label = "mailings"
            perms = Permission.objects.filter(content_type__app_label=app_label, content_type__model=model)
            for p in perms:
                group.permissions.add(p)
        self.stdout.write("Managers group created")
