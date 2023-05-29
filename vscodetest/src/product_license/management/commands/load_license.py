import os.path
import sys
from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandParser

from product_license.license_service import LicenseService


class Command(BaseCommand):
    help = "Load a license into the database"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-f", "--file", default=None, help="Path to the license file"
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        file = options.get("file", None)
        if not file:
            print("Error: Please supply the path to a license file")
            sys.exit(1)
        if not os.path.exists(file):
            print(f"Error: file {file} does not exist")
            sys.exit(2)
        with open(file, "rb") as license_file:
            license_bytes = license_file.read()
            LicenseService().add_license(license_bytes, allow_job=False)
        print("License added")
