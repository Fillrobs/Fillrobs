from django.core.management.base import BaseCommand
from utilities.models import GlobalPreferences


class Command(BaseCommand):
    help = "Turns off Quick Setup."

    def handle(self, *args, **options):
        pref = GlobalPreferences.objects.first()
        pref.run_quick_setup = False
        pref.save()
        self.stdout.write(self.style.SUCCESS("Successfully turned off Quick Setup"))
