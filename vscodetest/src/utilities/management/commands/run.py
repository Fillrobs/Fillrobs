# For CB developers, this management command can be used instead of "runserver" to speed up the
# dev/test cycle. This management command skips running some of the checks that Django's
# runserver does by default every time it auto-reloads the code.

# This can be run with ./manage.py run 0.0.0.0:$MYPORT

# Taken from https://stackoverflow.com/questions/41438593/skip-system-checks-on-django-server-in-debug-mode-in-pycharm

from django.core.management.commands.runserver import Command as RunServer


class Command(RunServer):
    def check(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("SKIPPING SYSTEM CHECKS!\n"))

    def check_migrations(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("SKIPPING MIGRATION CHECKS!\n"))
