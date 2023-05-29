#!/usr/bin/env python
from __future__ import unicode_literals, print_function
import os
import sys

__version__ = "0.0.9"

mydir = os.path.dirname(sys.argv[0])

pathadds = ["../", "."]

sys.path.insert(0, mydir)
os.chdir(mydir + "/..")

for x in pathadds:
    sys.path.insert(0, x)

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

if __name__ == "__main__":
    import django

    django.setup()

from c2_wrapper import create_global_preferences


print("\nCreating GlobalPreferences")
gp = create_global_preferences()
