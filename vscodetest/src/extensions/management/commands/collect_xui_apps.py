"""
./manage.py collect_xui_apps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

django-admin command for collecting UI Extension (XUI) apps on a local
filesystem and indexing them in the database.
"""

from django.core.management.base import BaseCommand

from extensions.models import XUIIndexer


class Command(BaseCommand):
    help = (
        "Update records for UI Extension (XUI) apps in the PROSERV_DIR/xui/"
        "directory.\n"
        "PROSERV_DIR can be changed in `customer_settings.py`."
    )

    def handle(self, *args, **options):
        handler = XUIIndexer(verbose=True)
        handler.index()
