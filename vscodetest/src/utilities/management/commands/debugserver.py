from django.core.management import CommandError
from django.core.management.commands.runserver import BaseRunserverCommand

import settings

DEFAULT_REMOTE_DEBUG_PORT = 12345
DEFAULT_REMOTE_DEBUG_HOST = "10.0.2.2"


class Command(BaseRunserverCommand):
    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        self.remote_debug_port = DEFAULT_REMOTE_DEBUG_PORT
        self.remote_debug_host = DEFAULT_REMOTE_DEBUG_HOST

        super().__init__(stdout, stderr, no_color, force_color)

    def handle(self, *args, **options):
        self.remote_debug_port = getattr(
            settings, "REMOTE_DEBUG_PORT", DEFAULT_REMOTE_DEBUG_PORT
        )
        self.remote_debug_host = getattr(
            settings, "REMOTE_DEBUG_HOST", DEFAULT_REMOTE_DEBUG_HOST
        )

        return super().handle(*args, **options)

    def inner_run(self, *args, **options):
        try:
            import pydevd
        except ImportError:
            raise CommandError("pydevd not installed.")
        else:
            print(
                "Debugger connecting to {}:{}".format(
                    self.remote_debug_host, self.remote_debug_port
                )
            )
            pydevd.settrace(
                host=self.remote_debug_host,
                port=self.remote_debug_port,
                suspend=False,
                stderrToServer=True,
                stdoutToServer=True,
            )

        super().inner_run(*args, **options)
