"""
CloudBolt built-in settings.

    DO NOT MODIFY THIS FILE - it is overwritten during upgrades.

To override settings, create or edit the file at this location:
/var/opt/cloudbolt/proserv/customer_settings.py
For settings changes to take effect, Apache must be restarted.

These settings, combined with your overrides, can be viewed in the CB interface
under Admin > Support Tools > Django Settings.
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

# Django settings for CloudBolt project.
# import django.conf.global_settings as DEFAULT_SETTINGS
from django.utils.translation import ugettext_lazy as _lazy
import os
import pwd
import sys
import warnings
from datetime import timedelta

from bleach import ALLOWED_TAGS
from corsheaders.defaults import default_headers
from pythonjsonlogger import jsonlogger


program = os.path.basename(sys.argv[0])
TESTING = "test" in sys.argv or program in [  # manage.py test
    "pytest",
    "py.test",
]  # pytest

# If you are embedding CloudBolt in a frame in a different UI, you can set Embedded Mode enabled
# in Misc Settings and it will prevent non-admin users from directly accessing the CB UI.
# Changing the setting here is deprecated but may be used in some customer environments
EMBEDDED_MODE = False


def running_in_docker():
    try:
        with open("/proc/self/cgroup", "r") as procfile:
            for line in procfile:
                fields = line.strip().split("/")
                if "docker" in fields[1]:
                    return True
    except IOError:
        return False
    else:
        return False


IS_DOCKER = running_in_docker()

# get the current directory that CloudBolt is in
ROOTDIR = os.path.abspath(os.path.dirname(__file__))

# disable the deprecation warnings that get spewed due to pytwist
warnings.simplefilter("ignore", DeprecationWarning)

ALLOWED_HOSTS = ["*"]

# RELEASE_VERSION_PREFIX". Used to determine download path for cloudbolt installer.
VERSION_INFO = {
    "VERSION": "9.4.7",
    "BUILD": "25fd3b9",
    "RELEASE_DATE": "2022-02-16 ",
    "DOWNLOAD_BASE_URL": "http://downloads.cloudbolt.io/",
    "RELEASE_VERSION_PREFIX": "cloudbolt9plus",
}

# LOW_CONSOLE_PORT and HIGH_CONSOLE_PORT define the range of ports that
# CloudBolt will use on the CB server to provide users access to console on
# VMs. Users' browsers will need to be able to connect to on the CB server on
# this range of ports.
# If you override these, it is recommended that you do it in customer_settings.py
# so the new values survive CB upgrades.
LOW_CONSOLE_PORT = 5900
HIGH_CONSOLE_PORT = 6900

# This is a fix for hard-coded Network Card labels in vCenter RHs
# note that currently this can only be set globally for all vCenter RHs here
VMWARE_NIC_LABEL_PREFIX = "Network adapter"

# For VMware, we have seen that fetching the tags during VM sync at scale can sometimes cause
# issues. Setting this to False will disable fetching the tags when refreshing info on a single
# VM and when syncing all VMs from an RH.
SYNC_VMWARE_TAGS = True

LOGIN_REDIRECT_URL = "/"
# login url defaults to accounts/login
# To enable PKI auth use the below value for LOGIN_URL:
# LOGIN_URL = "/pki/login/"
# For unified login, change the host below to match the voltron-ui deployment:
# LOGIN_URL = "http://localhost:3000/ui/unified-ui/login/username"

# To enable logout redirection, set the below value to the desired url:
# LOGOUT_REDIRECT_URL = "http://localhost:3000/ui/logout"

# The number of times a user can attempt to log in before their account is locked
LOGIN_FAILURE_LOCKOUT_LIMIT = 5
# The number of minutes failures can occur before a lock out happens. Also the lock's timeout.
LOGIN_FAILURE_LOCKOUT_TIMEOUT = 15

if "USER" in os.environ:
    USERNAME = os.environ["USER"]
else:
    USERNAME = "default"

# Allow session creation while retrieving Auth Token from API
# ALLOW_API_AUTH_TO_PERSIST_SESSION = True

# Customer assets such as templates, hook scripts, and styles reside under the
# 'pro services' directory and are preserved across CB upgrades.
VARDIR = os.environ.get("CB_VARDIR") or "/var/"
try:
    # allow for overriding of the VARDIR before it is used
    from settings_local import VARDIR
except ImportError:
    pass
PROSERV_DIR = os.path.join(VARDIR, "opt/cloudbolt/proserv/")
RUN_DIR = os.path.join(VARDIR, "run/cloudbolt/")
LOCKFILES_DIR = RUN_DIR
TMP_DIR = os.path.join(RUN_DIR, "tmp")
MAINTENANCE_MODE_FILE = os.path.join(RUN_DIR, "maintenance_mode")

#  CONTENT LIBRARY SETTINGS ###
#
# On 7.1 Content library is introduced
# This controls which content is exposed to end-users
#
#
CONTENT_LIBRARY_COLLECTIONS = [
    "blueprints",
    "orchestration-actions",
    "recurring-jobs",
    "rules",
    "server-actions",
    "resource-actions",
    "ui-extension-packages",
]
# end of CONTENT LIBRARY SETTINGS ###

DEBUG = False
# Print render time and query counts in page footer
SHOW_PAGE_STATS = DEBUG
# Enable to show the Django Debug Toolbar to troubleshoot long page loads w/ support
TOOLBAR = False
# Enable to show fake translations (for language 'xx') to debug i18n issues
DEBUG_I18N = False
# Enable to use the django-silk profiler
USE_SILK = False
# Enable To enable all the management commands in the dev_tools folder
ENABLE_DEV_TOOLS = False

# Allow for CORS ( cross origin resource sharing ) to be enabled.  By default the white list
# is empty.   You will also need to update the CORS_ORIGIN_WHITELIST below and add your
# domain(s) you want to allow to share resources.
CORS_ENABLED = False

# Enable to allow app.swaggerhub.com api browser to hit resources, require CORS cross
# origin resource sharing.   Note:  Enabling this also Enables CORS_ENABLED
ENABLE_SWAGGERHUB = False

# This controls whether the `About` dialog for CB shows the codename for the release & the
# textual description of the champion.
ENABLE_CHAMPION = True

# This variable is used to determine the columns that are shown in the server
# table
SERVER_TABLE_COLUMNS = [
    # Makes rows clickable and enables bulk server actions
    # Do not move this: Checkbox must come first
    "Checkbox",
    # 'Card',  # Visual representation includes OS family, hostname, power status
    "Power",  # "Pictograph" showing power state & CPU/mem/disk bars with tooltip
    "Hostname",
    "IP",
    "Family",
    "Status",
    "Owner",
    "Group",
    "Environment",
    # 'Rate',
    "Tags",
    "Added",  # Date CloudBolt first placed server under management
    # 'CPUs',
    # 'Disk',
    # 'Storage',  # synonym for 'Disk': total disk size in GB
    # 'Memory',
    "Power Schedule",
]

MAX_JOB_CONCURRENCY = 200

# List tuples for filtering out entire classes of events that appear in the
# Dashboard item "Recent Activity". Must be passed as (regex, display title).
# These items are selected by an admin in "Admin/Misc. Settings".
RECENT_ACTIVITY_EVENT_CLASSES = (
    (r"^Server discovered during a scan of.*", "Server Discovered"),
    (r"^Server created.*", "Server Created"),
    (r"Server record set to historical.*", "Server Deletion"),
    (r"^Server was decommissioned$", "Server Decommissioned"),
    (r"Server's IP has changed from.*", "Server IP Changed"),
    (r".*was added to network .*", "NIC Added"),
    (r"The network for .* was changed to.*", "NIC Changed"),
    (r"NIC.*was removed from server", "NIC Deletion"),
    (r"Adding new .* disk to server", "Disk Added"),
    (r"Size of disk \'.*\'\schanged to.*", "Disk Size Changed"),
    (r"Disk \'.*\' was deleted from server", "Disk Deleted"),
    (r".* was discovered on server.*", "Disk Message Duplicated"),
    (r"^CPUs has changed from.*", "CPU Changed"),
    (r"Mem Size has changed from.*to.*", "Memory Changed"),
    (r"^Rate changed$", "Rate Changed"),
    (r"Remote script hook .* failed when run on server", "Remote Script Failed"),
)


# VMware Resource Handlers only!
# When set to True remote scripts will be run using VMware tools.
# When set to False remote scripts will be run using SSH/WinRM.
# You can enable tech-specific script execution for non-vmware resource
# handlers by adding the "Use Tech-Specific Script Execution" parameter to
# servers, environments, etc.
TECH_SPECIFIC_SCRIPT_EXECUTION = True

# override this in settings_local.py
ADMINS = ((USERNAME, "%s@cloudboltsoftware.com" % USERNAME),)

MANAGERS = ADMINS
CB_ADMIN_ENABLED = False

# the following pages will bypass our global login requirement (which
# is specified in utilities.middleware.RequireLoginMiddleware)
LOGIN_REQUIRED_URLS_EXCEPTIONS = (
    r"^/about/",
    r"^/accounts/login/",
    r"^/accounts/unified-login/",
    r"^/accounts/logout/",
    r"^/accounts/password/reset/(done/|confirm/){0,1}",
    r"^/accounts/expired/",
    r"^/c2reports/",
    r"^/gradient.svg",
    r"^/pki/login/",
    r"^/api",
    r"^/setup_complete/",
    r"^/static",
    r"^/portal.css",  # Dynamically generated CSS
    r"^/product_license/upload$",
    r"^/product_license/confirm$",
    r"^/login",
    r"^/complete/google-oauth2",
    # Matches /authentication/saml2/<any whole number>/[acs|login|metadata]/
    r"^/authentication/saml2/\d+/(acs/|login/|metadata/){1}",
    r"^/_/features/",
)

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("api.permissions.CloudBoltAPIPermission",),
    "PAGE_SIZE": 10,
    "MAX_PAGE_SIZE": 100,
    # Some Renderer classes are configured in viewsets, e.g., CamelCaseJSONRenderer
    "DEFAULT_RENDERER_CLASSES": (
        "api.renderers.CloudBoltJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    # Most Parser classes are configured in viewsets, e.g., CamelCaseJSONParser
    # "DEFAULT_PARSER_CLASSES": (,),
    "DEFAULT_PAGINATION_CLASS": "api.v2.pagination.HALPagination",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
        # BasicAuthentication is turned off b/c it is inherently insecure, use JWT authentication
        # If you truly need BasicAuth you can enable it in customer_settings.py
        # "rest_framework.authentication.BasicAuthentication",
        # The session authentication is used for the API Browser and Swagger (API Console),
        # which are accessed from the CB Web UI and use a different approach to authentication
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "EXCEPTION_HANDLER": "api.exceptions.custom_handle_exception",
    "URL_FIELD_NAME": "href",
}

# Defaults https://jpadilla.github.io/django-rest-framework-jwt/#additional-settings
JWT_AUTH = {
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_ALLOW_REFRESH": True,
    "JWT_AUTH_COOKIE": "jwt",
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=1),
    "JWT_EXPIRATION_DELTA": timedelta(minutes=5),
}

JWT_AUTH_COOKIE_SETTINGS = {
    "JWT_HTTP_ONLY": True,
    "JWT_SAME_SITE": "Lax",
    "JWT_SECURE_COOKIE": True,
}

# override this in settings_local.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "%s_cloudbolt" % USERNAME,
        "USER": "cb_dba",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

# This variable is used as the default value when users are choosing a scheduled
# time for changing resources on a server. It should be in the format HH:MM:SS,
# on 24 hour time, and the default will be the next occurrence of that time
DEFAULT_CHANGE_TIME = "04:00:00"  # 4:00 AM

# First column is the value to pass to VMware via the -wintz flag; second
# column is what we store in the database as CustomFieldValue for the time_zone
# field.  For Microsoft Time Zone indecies, see
# http://msdn.microsoft.com/en-us/library/ms912391(v=winembedded.11).aspx
# For names see: http://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TZ_CHOICES = (
    (1, "US/Samoa"),
    (2, "US/Hawaii"),
    (2, "US/Aleutian"),
    (3, "US/Alaska"),
    (4, "US/Pacific"),
    (10, "US/Mountain"),
    (20, "US/Central"),
    (35, "US/Eastern"),
    (50, "America/Halifax"),
    (70, "America/Buenos_Aires"),
    (85, "UTC"),
    (85, "Europe/London"),
    (100, "Europe/Oslo"),
    (110, "Europe/Amsterdam"),
    (130, "Europe/Athens"),
    (145, "Europe/Moscow"),
    (165, "Asia/Dubai"),
    (185, "Asia/Karachi"),
    (190, "Asia/Kolkata"),
    (205, "Asia/Bangkok"),
    (225, "Australia/Perth"),
    (235, "Asia/Tokyo"),
    (245, "Australia/Darwin"),
    (250, "Australia/Adelaide"),
    (290, "Pacific/Auckland"),
)
# FIXME we should be able to use some third-party library to map these
# time zone names to the Microsoft time zone indecies.

SITE_ID = 1


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"
LANGUAGES = [("en", _lazy("English"))]
LOCALE_PATHS = [os.path.join(PROSERV_DIR, "locale"), os.path.join(ROOTDIR, "locale")]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
try:
    from tzlocal import get_localzone

    local_zone = get_localzone().zone
except ImportError:
    local_zone = None
TIME_ZONE = local_zone

USE_I18N = True

# Format of datetimes in CloudBolt tables and compact UI layouts
# https://docs.djangoproject.com/en/2.2/ref/templates/builtins/#std:templatefilter-date

SHORT_DATE_FORMAT = "m/d/Y"  # 01/26/2015
SHORT_DATE_FORMAT = "n/j/y"  # 1/26/15

SHORT_TIME_FORMAT = "P"  # 2:31 p.m.
SHORT_TIME_FORMAT = "g:i A"  # 2:31 PM


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/


# The paths for directories containing static assets differs between deployment
# and test. When `DEBUG` is set, we use paths that won't conflict with those of
# other developers.
#   STATIC_ROOT --- the absolute path to the directory where `collectstatic`
#     collects static files for deployment. The contents of this directory
#     should only be managed by the `collectstatic` command and not manually.
#     To have files appear in this directory, add them to your application's
#     static/ dir.
#   MEDIA_ROOT --- absolute path where user-uploaded are stored. Must not be a
#     a subdirectory of STATIC_ROOT; that dir is under full control of
#     `collectstatic` and should be considered volatile except for the purposes
#     of serving `collectstatic`'d files
#   STATIC_TESTS_DIR --- where the Robot logs are stored
STATIC_ROOT = os.path.join(VARDIR, "www/html/cloudbolt/static/collected/")
MEDIA_ROOT = os.path.join(VARDIR, "www/html/cloudbolt/static/uploads/")
STATIC_TESTS_DIR = os.path.join(VARDIR, "www/html/cloudbolt/static/functional_tests/")

# URL prefix for static files.
# Each new release forces browsers to fetch a new set of static resources
STATIC_URL = "/static-{}/".format(VERSION_INFO["BUILD"])

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/static/uploads/"

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = "/static/admin/"

# Additional locations of static files
# override this in settings_local.py
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    PROSERV_DIR + "static",
    ROOTDIR + "/static",
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Paths to the PEM-formatted SSL certs used by the webserver to provide HTTPS.
# These are used for encrypting the console feature's websockify connections.
# If the customer updates "/etc/httpd/conf.d/ssl.conf" to install real SSL
# certs, these values need to be updated (in
# /var/opt/cloudbolt/proserv/customer_settings.py) as well, or else console
# will cease to work. `SSL_KEY_PATH` may be set to `None` if the SSL key is
# combined into the file at `SSL_CERT_PATH`.
SSL_CERT_PATH = "/etc/pki/tls/certs/localhost.crt"
SSL_KEY_PATH = "/etc/pki/tls/private/localhost.key"

# Encrypted console requires trusted and valid certificates in some browsers;
# adding the cert to the browser's whitelist may not be sufficient: it /seems/
# that browsers that aren't Chrome will have difficulty using encrypted console
# (WSS) with CB's pre-packaged self-signed cert (even though HTTPS pages can
# load) because the cert has expired. This is why we set encryption to False,
# preferring that the feature works and be unencrypted vs not working.
ENCRYPT_CONSOLE = True

# Encrypted WinRM initial support
ENCRYPT_WINRM = False

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
        # Ensure each CB instance on this memcached uses its own namespace
        "KEY_PREFIX": USERNAME,
    }
}

# Time to cache the code file when generating fields on the order form
OPTIONS_CACHE_TIMEOUT = 30

# django-crispy-forms has a template pack for Bootstrap 3
CRISPY_TEMPLATE_PACK = "bootstrap3"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # Use absolute paths, not relative paths.
            PROSERV_DIR + "templates",
            PROSERV_DIR + "xui",
            "{}/templates".format(ROOTDIR),
            # This is for ps1 scripts used for MS Active Directory
            f"{ROOTDIR}/driven_apps/microsoft_active_directory/scripts",
            f"{ROOTDIR}/driven_apps/dns/scripts",
            f"{ROOTDIR}/driven_apps/fuse_ipam/scripts",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                # 'django.template.context_processors.i18n',
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "utilities.context_processors.global_vars",
            ]
        },
    }
]
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# BLEACH SETTINGS ###

BLEACH_ALLOWED_TAGS = ALLOWED_TAGS
BLEACH_ALLOWED_TAGS += [
    "br",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "mark",
    "p",
    "pre",
    "small",
    "sub",
    "sup",
    "table",
    "tbody",
    "thead",
    "tr",
    "td",
    "th",
]
# Safe global attributes per OWASP
BLEACH_DEFAULT_ALLOWED_ATTRS = [
    "align",
    "alink",
    "alt",
    "background-color",
    "border",
    "cellpadding",
    "cellspacing",
    "class",
    "color",
    "cols",
    "colspan",
    "coords",
    "dir",
    "face",
    "height",
    "hspace",
    "ismap",
    "lang",
    "margin",
    "multiple",
    "nohref",
    "noresize",
    "noshade",
    "nowrap",
    "ref",
    "rel",
    "rev",
    "rows",
    "rowspan",
    "scrolling",
    "shape",
    "span",
    "summary",
    "tabindex",
    "title",
    "usemap",
    "valign",
    "value",
    "vlink",
    "vspace",
    "width",
]
BLEACH_ALLOWED_ATTRS = {
    "*": BLEACH_DEFAULT_ALLOWED_ATTRS,
    "a": ["href", "title"],
    "abbr": ["title"],
    "acronym": ["title"],
}
BLEACH_ALLOWED_STYLES = []
BLEACH_ALLOWED_PROTOCOLS = ["http", "https", "mailto"]

# end BLEACH SETTINGS ###

# SameSiteCookieWorkaroundMiddleware is before the SessionMiddleware as we're manipulating the session cookie

MIDDLEWARE = [
    "utilities.middleware.SameSiteCookieWorkaroundMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "product_license.middleware.LicenseMiddleware",
    "quick_setup.middleware.QuickSetupMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "utilities.middleware.UserActivityMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "driven_apps.middleware.UpgradeMiddleware",
    "utilities.middleware.RequireLoginMiddleware",
    "utilities.middleware.CacheHeaderMiddleware",
    "utilities.middleware.DetectedTimeZoneMiddleware",
    "utilities.middleware.PasswordExpirationMiddleware",
    "utilities.middleware.AcceptEulaMiddleware",
    "utilities.middleware.SetChallengeMiddleware",
    "utilities.middleware.LegalNoticeMiddleware",
    "waffle.middleware.WaffleMiddleware",
    "utilities.get_current_userprofile.UserProfileMiddleware",
    "utilities.middleware.SamlSessionMiddleware",
]

# Remove middlewares that shouldn't run for (most) unit tests, because they
# interferes with their redirects.
if "test" in sys.argv or "pytest" in sys.modules:
    MIDDLEWARE.remove("utilities.middleware.SetChallengeMiddleware")
    MIDDLEWARE.remove("product_license.middleware.LicenseMiddleware")

# SESSION config
if DEBUG:
    SESSION_COOKIE_AGE = 12096000  # 20 weeks, in seconds
    SESSION_EXPIRE_AT_BROWSER_CLOSE = False
else:
    SESSION_COOKIE_AGE = 12096000  # 20 weeks, in seconds
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# This removes the explicit CSRF cookie and puts it in the session
# This is important:
# 1. Some security reviewers don't like seeing separate CSRF and SESSION cookies
# 2. We only have 1 cookie to deal with when manipulating SameSite visibility (for Embedded Mode)
CSRF_USE_SESSIONS = True

# Email Templates
"""
Uncomment the following lines to only send emails to a certain list of users.
This is useful if you want to test sending emails on a staging server but you
don't want to risk sending emails to addresses outside of your organization.
"""
# EMAILTEMPLATES_DEBUG = True
# EMAILTEMPLATES_DEBUG_WHITELIST = ['cloudbolt.io', 'cloudboltsoftware.com']


ROOT_URLCONF = "urls"

INSTALLED_APPS = (
    # Django Apps
    # Uncomment the next line to enable the admin:
    "django.contrib.admin",
    # Uncomment the next line to enable admin documentation:
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.sessions",
    # 'django.contrib.sites',
    "django.contrib.staticfiles",
    "django.forms",
    # 3rd Party Apps
    "django_extensions",
    "formtools",
    "rest_framework",
    "drf_yasg",
    "django_gravatar",
    "crispy_forms",
    "whoosh",
    "haystack",
    "taggit",
    "remote",
    "markdownx",
    "waffle",
    # General-purpose Apps
    "extensions",
    "tabs",
    "tags",
    "wizards",
    "reversion",
    # CloudBolt Apps
    "utilities",
    "accounts",
    "alerts",
    "analytics",
    "api",
    "authentication",
    "authentication.sso",
    "behavior_mapping",
    "bookmarks",
    "cb_secrets",
    "cbadmin",
    "connectors.ansible",
    "connectors.chef",
    "connectors.puppet",
    "connectors.puppet_ent",
    "console",
    "costs",
    "dashboard",
    "dataprotection",
    "dataprotection.cohesity",
    "dataprotection.rubrik",
    "dataprotection.azure_backup",
    "dataprotection.commvault",
    "content_library",
    "externalcontent",
    "history",
    "infrastructure",
    "ipam",
    "ipam.infoblox",
    "ipam.phpipam",
    "ipam.bluecat",
    "ipam.solarwindsipam",
    "itsm",
    "itsm.servicenow",
    "jobengine",
    "jobs",
    "licenses",
    "loadbalancers",
    "emailtemplates",
    "maps",
    "networks",
    "networks.nicira",
    "network_virtualization",
    "network_virtualization.nsx_t",
    "orchestrationengines",
    "orchestrationengines.hpoo",
    "orchestrationengines.vco",
    "orders",
    "pki",
    "portals",
    "product_license",
    "product_license.eula",
    "provisionengines",
    "provisionengines.razor",
    "quota",
    "resourcehandlers",
    "resourcehandlers.acropolis",
    "resourcehandlers.alibaba",
    "resourcehandlers.aws",
    "resourcehandlers.aws_private",
    "resourcehandlers.azure_arm",
    "resourcehandlers.azure_stack",
    "resourcehandlers.dimensiondata",
    "resourcehandlers.dellblade",
    "resourcehandlers.gce",
    "resourcehandlers.gcp",
    "resourcehandlers.helion",  # HP Helion
    "resourcehandlers.hpblade",
    "resourcehandlers.hyperv",
    "resourcehandlers.ipmi",
    "resourcehandlers.libcloudhandler",
    "resourcehandlers.maas",
    "resourcehandlers.manualpowerserver",
    # Nebula models were removed 4/7/2015 for 5.0.1.  After all customers are
    # on 5.0.1 or later (and we know they have run the migrations to remove the
    # models and the ResourceTechnology), we should remove nebula from the list
    # of installed_apps
    "resourcehandlers.nebula",
    "resourcehandlers.openstack",
    "resourcehandlers.outscale",
    "resourcehandlers.oci",
    "resourcehandlers.qemu",
    "resourcehandlers.slayer",  # IBM SoftLayer
    "resourcehandlers.vcloud_director",
    "resourcehandlers.vmware",
    "resourcehandlers.vmware_cloud_aws",
    "resourcehandlers.vmware.nsx",
    "resourcehandlers.xen",
    "resourcehandlers.scvmm",
    # 'uiconfigelements', on hold until after 2.1
    "quick_setup",
    "reportengines",
    "reportengines.jasper",
    "reportengines.internal",
    "cbhooks",
    "servicecatalog",
    "siem",
    "siem.splunk",
    "resources",
    # The resources app replaces the services app, but we need to keep services
    # around for awhile to keep old migrations there
    "services",
    "tenants",
    "cscv",
    "common",
    "connectors",
    "containerorchestrators",
    "containerorchestrators.kuberneteshandler",
    "files",
    "health_check",
    "features",
    "driven_apps.ansible_tower",
    "driven_apps.blueprint_based_modules",
    "driven_apps.naming",
    "driven_apps.microsoft_active_directory",
    "driven_apps.property_sets",
    "driven_apps.user_interface",
    "driven_apps.validators",
    "driven_apps.credentials",
    "driven_apps.fuse_ipam",
    "driven_apps.fuse_scripting",
    "driven_apps.fuse_servicenow",
    "driven_apps.templating",
    "driven_apps.fuse_jobs",
    "driven_apps.dns",
    "driven_apps.ingest",
    "driven_apps.vra",
    "webpack_loader",
)

# Global search
HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.whoosh_backend.WhooshEngine",
        "PATH": os.path.join(VARDIR, "opt", "cloudbolt", "search_index"),
        "STORAGE": "file",
    }
}
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 20

TAGGIT_CASE_INSENSITIVE = True

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
logdir = os.path.join(VARDIR, "log/cloudbolt")
if not os.path.isdir(logdir):
    os.makedirs(logdir)

if os.access(logdir, os.W_OK):
    logfile = os.path.join(logdir, "application.log")
    jobengine_logfile = os.path.join(logdir, "jobengine.log")
    # this needs to be CAPS so Django's settings framework makes it visible to
    # the rest of the app
    JOBTHREAD_LOGPATH = os.path.join(logdir, "jobs")
    authentication_logfile = os.path.join(logdir, "authentication.log")
else:
    print("Could not write to the log dir %s" % logdir)
    sys.exit(1)
default_handlers = ["logfile", "console"]
jobengine_handlers = ["jobengine_logfile"]
logfilelevel = "DEBUG"
non_console_handlers = ["jobengine_logfile"]
authentication_handlers = ["authentication_logfile"]

if DEBUG is False:
    # Set the log ownership and group to apache
    try:
        log_owner = pwd.getpwnam("apache")
        log_group = pwd.getpwnam("apache")
        os.chown(logfile, log_owner[2], log_group[3])
        os.chown(jobengine_logfile, log_owner[2], log_group[3])
    except Exception:
        # TODO: this should be logged
        pass

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        "json": {
            "()": jsonlogger.JsonFormatter,
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "logfile": {
            "level": logfilelevel,
            "class": "utilities.handlers.CloudBoltLogFileHandler",
            "filename": logfile,
            "formatter": "json",
        },
        "jobengine_logfile": {
            "level": logfilelevel,
            "class": "utilities.handlers.CloudBoltLogFileHandler",
            "filename": jobengine_logfile,
            "formatter": "json",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "authentication_logfile": {
            "level": logfilelevel,
            "class": "utilities.handlers.CloudBoltLogFileHandler",
            "filename": authentication_logfile,
            "formatter": "json",
        },
    },
    "loggers": {
        "": {"handlers": default_handlers, "level": "DEBUG", "propagate": True},
        # Override the default django logger so it doesn't send email.
        # Instead, propagate errors to the root logger's default handlers.
        # https://docs.djangoproject.com/en/2.2/topics/logging/#django-s-default-logging-configuration
        "amqp": {"handlers": jobengine_handlers, "level": "INFO", "propagate": False},
        "asyncio": {"handlers": default_handlers, "level": "INFO", "propagate": False},
        # For login and logout
        "authentication": {
            "handlers": authentication_handlers,
            "level": "DEBUG",
            "propagate": True,
        },
        # Boto produces tons of DEBUG-level logs; only log those when needed
        # Has no handlers: events will be propagated to the root handler
        "boto": {
            "handlers": [],
            "level": "DEBUG" if DEBUG else "WARNING",
            "propagate": True,
        },
        "django": {"handlers": [], "level": "INFO", "propagate": True},
        "jobengine": {
            "handlers": jobengine_handlers,
            "level": "DEBUG",
            "propagate": False,
        },
        # Logger for individual jobs
        "jobengine.job": {
            "handlers": [],  # Must be populated uniquely, per job
            "level": "DEBUG",
            "propagate": False,
        },
        # Logger for individual workers
        "jobengine.worker": {
            "handlers": jobengine_handlers,
            "level": "DEBUG",
            "propagate": False,
        },
        "jobs.management": {
            "handlers": jobengine_handlers,
            "level": "DEBUG",
            "propagate": False,
        },
        "jobs.tasks": {
            "handlers": jobengine_handlers,
            "level": "DEBUG",
            "propagate": False,
        },
        # keyring.backend spews logs when loading backends.
        # We want to surpress this all of the time; it is noisy and uninformative.
        "keyring.backend": {
            "handlers": default_handlers,
            "level": "CRITICAL",
            "propagate": False,
        },
        # msrest produces many long DEBUG-level logs.
        # Only log INFO level and up.
        "msrest": {"handlers": default_handlers, "level": "INFO", "propagate": False},
        # Spams INFO with "Resource 'XMLSchema.xsd' is already loaded"
        "xmlschema": {
            "handlers": default_handlers,
            "level": "WARNING",
            "propagate": False,
        },
    },
}

ONE_FUSE_URL = "/ui/"
if IS_DOCKER:
    DATABASES["default"]["NAME"] = "cloudbolt"
    ONE_FUSE_URL = "http://localhost:3000/ui/"

# AWS regions and endpoints (for EC2 service) are now a setting so they
# can be customized for private deployments of Amazon EC2.
EC2_REGIONS = (
    ("us-west-1", "US West (N. California)"),
    ("us-west-2", "US West (Oregon)"),
    ("us-east-1", "US East (N. Virginia)"),
    ("us-east-2", "US East (Ohio)"),
    ("ca-central-1", "Canada (Central)"),
    ("eu-west-1", "EU (Ireland)"),
    ("eu-west-2", "EU (London)"),
    ("eu-west-3", "EU (Paris)"),
    ("eu-central-1", "EU (Frankfurt)"),
    ("eu-north-1", "EU (Stockholm)"),
    ("eu-south-1", "EU (Milan)"),
    ("ap-east-1", "Asia Pacific (Hong Kong)"),
    ("ap-southeast-1", "Asia Pacific (Singapore)"),
    ("ap-southeast-2", "Asia Pacific (Sydney)"),
    ("ap-northeast-1", "Asia Pacific (Tokyo)"),
    ("ap-northeast-2", "Asia Pacific (Seoul)"),
    ("ap-northeast-3", "Asia Pacific (Osaka-Local)"),
    ("ap-south-1", "Asia Pacific (Mumbai)"),
    ("af-south-1", "Africa (Cape Town)"),
    ("me-south-1", "Middle East (Bahrain)"),
    ("sa-east-1", "South America (Sao Paulo)"),
    ("us-gov-west-1", "AWS GovCloud (US-West)"),
    ("us-gov-east-1", "AWS GovCloud (US-East)"),
    ("cn-north-1", "China (Beijing)"),
    ("cn-northwest-1", "China (Ningxia)"),
)

EMAIL_BASE_URL = ""

# Remote user authentication support
AUTHENTICATION_BACKENDS = (
    "utilities.backend.PKIBackend",
    "utilities.backend.RADIUSBackend",
    "utilities.backend.LDAPBackend",
    "utilities.backend.CBModelBackend",
    "authentication.sso.backends.Saml2Backend",
)

# Use Django's default password validators
# More info: https://docs.djangoproject.com/en/2.2/topics/auth/passwords/#module-django.contrib.auth.password_validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "common.validators.password.CBMinimumLengthValidator",
        "OPTIONS": {"min_length": 9},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {
        "NAME": "common.validators.password.ComplexPasswordValidator",
        "OPTIONS": {
            "min_matches": 3,
            "validators": [
                {"NAME": "common.validators.password.NumberValidator"},
                {"NAME": "common.validators.password.UppercaseValidator"},
                {"NAME": "common.validators.password.LowercaseValidator"},
                {
                    "NAME": "common.validators.password.SymbolValidator",
                    "OPTIONS": {
                        "special_chars": "|\\`~!@#$%^&*_\-+=;:'\",<>./?"  # noqa: W605
                    },
                },
            ],
        },
    },
]

PASSWORD_HISTSIZE = 10
PASSWORD_EXPIRATION_HOURS = 0
PASSWORD_RESET_TIMEOUT_DAYS = 1
EMAIL_VERIFICATION_TIMEOUT_DAYS = 1

# Avatars
# NOTE: This setting is deprecated; use Admin > Miscellaneous Settings > Show User Avatars instead.
#
# CloudBolt integrates with the service hosted at gravatar.com (not affiliated).
# Avatar images are managed by users and looked up by email address.
#
# To disable, set this to False in your customer_settings.py
ENABLE_AVATARS = True


# from django.contrib.messages import constants as messages_constants

# Add a 'confirm' CSS class to messages framework so we can apply a
# question icon to it.
MESSAGE_TAGS = {100: "confirm"}

# For the secrets app. OWNER tells secrets who the owner of the secret key file
# should be. The value OWNER will also determine the key's filename. Setting
# this constant in settings is useful so that in production, we can set the
# owner to apache so that scripts run as both root and as apache will use the
# same key file. If OWNER is not specified (suggested for development
# environments) then a separate key file will automatically be created for the
# Django process's current effective user.
SECRETS = {"OWNER": "apache"}

# Guacamole runs behind Apache by default, but guacd can be configured to run
# on a secondary server by modifying these parameters in customer-specific
# settings files (see below). For examples, see the /etc/init.d/guacg and guacd
# services. Note that if CloudBolt is SSL-encrypted, guacg will need to be
# SSL-encrypted as well.
# GUACD_HOST = '127.0.0.1'  # guacd server (guacg needs to be able to reach here)
# GUACD_PORT = 4822  # guacd port
# GUAC_TUNNEL_HOST = GUACD_HOST  # guacg server (browser will connect here)
# GUAC_TUNNEL_PORT = 6060  # guacg port

MAX_IP_RETRIES = 50
MAX_HOSTNAME_RETRIES = 20

MAX_RECENTLY_VIEWED_ITEMS_TO_TRACK = 5

SHELL_PLUS = "ipython"
SHELL_PLUS_DONT_LOAD = ["auth.Group"]  # load accounts.Group instead
# Extra args for ipython to use in shell plus and jupyter
IPYTHON_ARGUMENTS = [
    "-c",
    "import os; os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'",
    "--TerminalIPythonApp.force_interact=True",
]

# DEFAULT_NEW_SERVER_BLUEPRINT_NAME is only used to look up the default
# blueprint in cb_minimal, so it should never be changed.
# NEW_SERVER_BLUEPRINT_NAME is used by the /new_server/ view and can be
# overridden in customer_settings.py.
DEFAULT_NEW_SERVER_BLUEPRINT_NAME = "Custom Server"
NEW_SERVER_BLUEPRINT_NAME = DEFAULT_NEW_SERVER_BLUEPRINT_NAME

# This token is used for the iframe to authenticate with Jupyter Notebook. If you wish to override this, copy all
# NOTEBOOK_* entries into your /var/opt/cloudbolt/proserv/customer_settings.py file and `service jupyterd restart` and
# `service httpd restart` to pick up the changes.
NOTEBOOK_TOKEN = "04d82becd886fe7ef0448cf6af7d80c04615415b74d05530"
NOTEBOOK_PORT = "55555"
# These arguments are used by ./manage.py shell_plus --notebook (if it were
# used):
NOTEBOOK_ARGUMENTS = [
    "--ip=127.0.0.1",
    "--port={}".format(NOTEBOOK_PORT),
    "--no-browser",
    "--NotebookApp.base_url=/shell",
    "--NotebookApp.allow_origin=*",
    "--NotebookApp.token={}".format(NOTEBOOK_TOKEN),
    "--NotebookApp.tornado_settings={'headers': {'Content-Security-Policy': \"frame-ancestors https://* 'self' \" }}",
]

# Set to True to fail CloudBolt hooks when their remote source code can't be
# reached. By default, the last known version of the code will be run.
FAIL_IF_REMOTE_SOURCE_INACCESSIBLE = False

# Override this in customer_settings to enable eventlet blocking detection for
# job engine troubleshooting purposes. Not for production use!
EVENTLET_BLOCKING_DETECTION = False
EVENTLET_BLOCKING_DETECTION_SECONDS = 10

###
# Terraform configuration
###
TERRAFORM_DIR = os.path.join(
    VARDIR, "opt", "cloudbolt", "terraform"
)  # /var/opt/cloudbolt/terraform
# Manually download and unpack the `terraform` executable here. Something like this:
#
# wget https://releases.hashicorp.com/terraform/0.12.1/terraform_0.12.1_linux_amd64.zip
# unzip terraform_0.12.1_linux_amd64.zip
# mv terraform {{TERRAFORM_BINARY}}

TERRAFORM_BINARY_DIR = os.path.join(
    TERRAFORM_DIR, "bin"
)  # /var/opt/cloudbolt/terraform/bin/
TERRAFORM_BINARY = os.path.join(
    TERRAFORM_BINARY_DIR, "terraform"
)  # /var/opt/cloudbolt/terraform/bin/terraform

# Sub-directories containing Terraform `.tf` plan files should be placed under TERRAFORM_PLANS_DIR.
# Where users can manually copy their plans in the filesystem
# with the base dir being /var/opt/cloudbolt/terraform/plans
# Example usage:
#   {{TERRAFORM_PLANS_DIR}}/my_plan/main.tf
#   {{TERRAFORM_PLANS_DIR}}/other_plan/content.tf
TERRAFORM_PLANS_DIR = os.path.join(TERRAFORM_DIR, "plans")
# For plans extracted by cloudbolt post-uploading a zip file
TERRAFORM_EXTRACTED_PLANS_DIR = os.path.join(TERRAFORM_DIR, "extracted_plans")
# Copies of the above plans are put into this directory.
# Example:
#   /var/opt/cloudbolt/terraform/resources/resource_id/job_id/your_plan_files.tf
TERRAFORM_RESOURCES_DIR = os.path.join(
    TERRAFORM_DIR, "resources"
)  # /var/opt/cloudbolt/terraform/resources
# Temporarily stores `.tfplan` files
# More info: https://www.terraform.io/docs/commands/plan.html#out-path
TERRAFORM_TFPLANS_DIR = os.path.join(
    TERRAFORM_DIR, "tfplans"
)  # /var/opt/cloudbolt/terraform/tfplans
# Initialize these directories
for directory in [
    TERRAFORM_DIR,
    TERRAFORM_BINARY_DIR,
    TERRAFORM_PLANS_DIR,
    TERRAFORM_EXTRACTED_PLANS_DIR,
    TERRAFORM_RESOURCES_DIR,
    TERRAFORM_TFPLANS_DIR,
]:
    try:
        os.makedirs(directory, mode=0o755)
    except OSError:
        # it probably already exists
        pass

# Kubernetes configuration
##########################
KUBERNETES_DIR = os.path.join(VARDIR, "opt", "cloudbolt", "kubernetes")

KUBERNETES_BINARY_DIR = os.path.join(KUBERNETES_DIR, "bin")

RKE_BINARY = os.path.join(KUBERNETES_BINARY_DIR, "rke")

KUBECTL_BINARY = os.path.join(KUBERNETES_BINARY_DIR, "kubectl")

###
# Feature flag settings
# Access this through the `features` app
###
FEATURE_REGISTRY = {}
FEATURE_REGISTRY["currency::conversion"] = False
FEATURE_REGISTRY["terraform::serviceitem"] = False

###
# Timeout And Polling Interval settings for Deporovisioning a managed object in Onefuse
###
ROLLBACK_RETRY_POLLING_INTERVAL = 30  # time in seconds
ROLLBACK_RETRY_TIMEOUT = 7200  # time in seconds, 120 minutes total

# Rollback retry polling interval and timeout, specifically for AT
# By default set to the general timeouts
ANSIBLE_TOWER_ROLLBACK_RETRY_POLLING_INTERVAL = ROLLBACK_RETRY_POLLING_INTERVAL
ANSIBLE_TOWER_ROLLBACK_RETRY_TIMEOUT = ROLLBACK_RETRY_TIMEOUT

# See DEV-16893, an issue with jobs being erronously cancelled in a HA setup.
# This feature disables orphan job cleanup, which allows these jobs to
# complete. Should only be set to False in HA environments with multiple
# JobEngine instances, and where parent jobs are cancelled by the JobEngine
# while child jobs are still running. This feature should be removed once this
# bug is resolved.
FEATURE_REGISTRY["jobengine::cancel_orphan_jobs"] = True

# Doing a forceful kill of the Job Engine when something has been running
# well past the timeout, indicating that the attempt to cancel it has likely
# failed and we need to ensure the Job Engine can restart, will begin as an
# opt-in feature and then be changed to opt-out in the next release
FEATURE_REGISTRY["jobengine::hard_reset_past_timeout"] = False

# See DEV-15578. Feature is only for limited set of customers
FEATURE_REGISTRY["resourcehandler::outscale"] = False

# Waffle settings back FEATURE toggles
WAFFLE_CREATE_MISSING_SWITCHES = True
WAFFLE_LOG_MISSING_SWITCHES = True

# This should be overridden in src/settings.py customer_settings by a uuid created automatically
# either on upgrade or install.
UNIQUE_TOKEN = "override_this_in_customer_settings"

# Note: SECRET_KEY must be defined before the license check below!
# Make this unique, and don't share it with anybody.
SECRET_KEY = "(ylmg$u@ne=ih!@81=*vxmxq8!away@7a#012#3ak0h1^bx%bk"

# Swagger UI Settings
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"},
        "basic": {"type": "basic"},
    },
    # -1 means don't show models on the Swagger UI page
    "DEFAULT_MODEL_DEPTH": -1,
    "USE_SESSION_AUTH": False,
    # these settings are used in urls.py in the drf_yasg.views.get_schema_view function
    "title": "CloudBolt Appliance API",
    "desc": "",
    "default_version": "v2",
}

# The Hostname and Hostname Preview fields are special and not treated the same as standard Parameters
# Using the two fields below, you can overwrite the tooltip used for each of these fields.  When blank, the Out
# Of The Box behavior persists.
HOSTNAME_TOOLTIP = ""
HOSTNAME_PREVIEW_TOOLTIP = ""

# There was a previous setting of "b7d17ed5eab268dde9e3644262c02c59"
# that was used for "CloudBolt Dev" if a particular license attribute was
# set. That check has been removed and we are using a single token now.
MIXPANEL_TOKEN = "2f8e5fffdae85115798fdf970b766aa4"  # CloudBolt Prod


#  ********************ATTENTION: Avoid placing more settings below this line. Doing so could *********************
#  ********************* override settings_local.py and customer_settings.py **************************************


if os.path.isfile(os.path.join(ROOTDIR, "settings_local.py")):
    # this will override any of the settings defined above with what
    # you have in settings_local.py
    # settings_local.py should not be in source control, as it should
    # contain your personal settings for your Django dev instance
    from settings_local import *  # noqa: F403, F401

# this setting allows users to have the same username in in different domains login as different users
# otherwise CB throws an error, if this setting is changed to true and there already exist
# one or more LDAP users in CB, new users with concatenated usernames
# will be created the next time that they log in
ENABLE_DUPLICATE_USERNAMES_FROM_MULTIPLE_DOMAINS = False

if os.path.isdir(PROSERV_DIR):
    # Always add this to support extensions
    sys.path.insert(0, PROSERV_DIR)

    if os.path.isfile(os.path.join(PROSERV_DIR, "customer_settings.py")):
        # if an exception is thrown, we will just let it be raised and let the
        # customer fix the issue
        from customer_settings import *  # noqa: F403, F401

#  ****************************************************************************************************************
#  ****************************************************************************************************************

# Set JWT_AUTH["JWT_SECRET_KEY"] after loading customer_settings to make sure we are using any user-defined keys
JWT_AUTH["JWT_SECRET_KEY"] = UNIQUE_TOKEN

# If the proserv static dir doesn't exist, create it now. This avoids errors that are thrown when
# building the CB installer/upgrader after freshly checking out the repo.
proserv_static_dir = os.path.join(VARDIR, "opt/cloudbolt/proserv/static")
try:
    os.makedirs(proserv_static_dir, mode=0o755)
except OSError:
    # it probably already exists
    pass

# This must get checked after customer_settings is loaded.
# Enable by doing "TOOLBAR=1 ./dev_tools/startdev.sh" or adding TOOLBAR=True to customer_settings
if os.environ.get("TOOLBAR") or TOOLBAR is True:
    INSTALLED_APPS += ("debug_toolbar",)

    DEBUG_TOOLBAR_PANELS = [
        # Comment out any of these to SIGNIFICANTLY speed up your toolbar!
        # 'debug_toolbar.panels.versions.VersionsPanel',
        # 'debug_toolbar.panels.timer.TimerPanel',
        # 'debug_toolbar.panels.settings.SettingsPanel',
        # 'debug_toolbar.panels.headers.HeadersPanel',
        # 'debug_toolbar.panels.request.RequestPanel',
        "debug_toolbar.panels.sql.SQLPanel",
        # 'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        # 'debug_toolbar.panels.templates.TemplatesPanel',
        # 'debug_toolbar.panels.cache.CachePanel',
        # 'debug_toolbar.panels.signals.SignalsPanel',
        # 'debug_toolbar.panels.logging.LoggingPanel',
        # 'debug_toolbar.panels.redirects.RedirectsPanel',
    ]

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        # ProfileMiddleware is useful for performance analysis.
        # Add a "prof" key to the query string by appending ?prof (or &prof=)
        # and you'll see the profiling results in your browser
        # For more info see https://pypi.python.org/pypi/django-snippetscream
        # 8/29/16 commenting out for now because it interferes with debug toolbar
        # 'snippetscream.ProfileMiddleware',
    ]

    def custom_show_toolbar(request):
        """Only show toolbar in debug mode"""
        return DEBUG

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": custom_show_toolbar,
        # 'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
        # 'HIDE_DJANGO_SQL': False,
        # 'TAG': 'div',
    }

# Enable by doing "DEBUG_I18N=1 ./dev_tools/startdev.sh" or adding DEBUG_I18N=True to customer_settings
if os.environ.get("DEBUG_I18N") or DEBUG_I18N is True:
    # Add dev_tools to INSTALLED_APPS so we can run the translate_xx command
    if "dev_tools" not in INSTALLED_APPS:
        INSTALLED_APPS += ("dev_tools",)
    LANGUAGES.append(("xx", "Debug Language"))
    # Like LocaleMiddleware, debug_i18n_middleware needs to come before
    # CommonMiddleware but after SessionMiddleware.
    # https://docs.djangoproject.com/en/2.2/topics/i18n/translation/#how-django-discovers-language-preference
    index = MIDDLEWARE.index("django.middleware.common.CommonMiddleware")
    MIDDLEWARE.insert(index, "utilities.middleware.debug_i18n_middleware")

if os.environ.get("ENABLE_DEV_TOOLS") or ENABLE_DEV_TOOLS is True:
    if "dev_tools" not in INSTALLED_APPS:
        INSTALLED_APPS += ("dev_tools",)


# Set up testing specific options that enhance test speed
TEST_RUNNER = "utilities.test.runner.NoLoggingTestRunner"
if TESTING:
    INSTALLED_APPS += ("test",)
    # Use SQLite for testing. Django will set this up in-memory.
    DATABASES = {
        "default": {
            "NAME": ":memory:",
            "ENGINE": "django.db.backends.sqlite3",
            # Naming a test database causes sqlite to create files on disk
            # instead of using in-memory mode. This enables concurrent usage.
            "TEST": {"NAME": "test_db"},
            # Avoids the occasional "database is locked" error.
            "OPTIONS": {"timeout": 10},
        }
    }

    # Disable migrations for all apps. Approach taken from
    # https://simpleisbetterthancomplex.com/tips/2016/08/19/django-tip-12-disabling-migrations-to-speed-up-unit-tests.html
    MIGRATION_MODULES = {app.split(".")[-1]: None for app in INSTALLED_APPS}

    # Disable caching so objects don't persist between tests
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
    # Save files to a special directory so we know they're ok to delete
    MEDIA_ROOT += "unit_tests/"


if "raven.contrib.django.raven_compat" in INSTALLED_APPS:
    # Send ERROR-level messages to Sentry
    LOGGING["handlers"]["sentry"] = {
        "level": "ERROR",
        "class": "raven.contrib.django.raven_compat.handlers.SentryHandler",
        "formatter": "standard",
    }
    LOGGING["loggers"][""]["handlers"] += ["sentry"]
    LOGGING["loggers"]["jobengine.job"]["handlers"] += ["sentry"]
    # Don't write Raven/Sentry messages to log file
    console_only = {"level": "DEBUG", "handlers": ["console"], "propagate": False}
    LOGGING["loggers"]["raven"] = console_only
    LOGGING["loggers"]["sentry.errors"] = console_only

if os.environ.get("USE_SILK") or USE_SILK is True:
    INSTALLED_APPS += ("silk",)
    MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")
    SILKY_PYTHON_PROFILER = True
    SILKY_PYTHON_PROFILER_BINARY = True

VUE_FRONTEND_DIR = os.path.join(ROOTDIR, "static/js/vue")

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "js/vue/",  # must end with slash
        "STATS_FILE": os.path.join(VUE_FRONTEND_DIR, "webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    }
}

ONEFUSE_DYNAMIC_PROPERTY_SET_PREFIX = "1FPS_"
ONEFUSE_DYNAMIC_PROPERTY_SET_RECURSION_LIMIT = 3

if (
    os.environ.get("CORS_ENABLED")
    or CORS_ENABLED is True
    or os.environ.get("ENABLE_SWAGGERHUB")
    or ENABLE_SWAGGERHUB is True
):
    # Add the CORS App to the list
    INSTALLED_APPS += ("corsheaders",)
    #  Needs to be at the top of the Middleware List
    MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")
    CORS_ALLOW_HEADERS = list(default_headers) + ["SOURCE"]
    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_WHITELIST = []
    CORS_ORIGIN_ALLOW_ALL = False

if os.environ.get("ENABLE_SWAGGERHUB") or ENABLE_SWAGGERHUB is True:
    CORS_ORIGIN_WHITELIST.append("https://app.swaggerhub.com")

# Django 3.2 upgrade set default AutoField
# See the following links for more info:
#   https://docs.djangoproject.com/en/3.2/releases/3.2/
#   https://dev.to/rubyflewtoo/upgrading-to-django-3-2-and-fixing-defaultautofield-warnings-518n
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

SILENCED_SYSTEM_CHECKS = ["fields.W903"]
