#!/usr/bin/env python

import json
import shutil
import subprocess
import sys
import uuid
from argparse import RawTextHelpFormatter
from contextlib import ContextDecorator
from os import environ
from pathlib import Path
from subprocess import CompletedProcess
from tempfile import TemporaryDirectory
from typing import Dict, List, Optional, Tuple

import django
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone


# IF MAKING FUNCTIONAL CHANGES TO THIS FILE #
# Follow the instructions in this doc
# https://docs.google.com/document/d/16Cgul037MmarJK4nRd4WKTmFS2EPgJlXi10PuwMG4AU
# to update our hosted docs with a new downloadable version of this file

HELP_TEXT: str = """Export utility to collect and compress everything necessary to configure a new CloudBolt
instance such that it matches this one. The export will always include the following directories:
    * VARDIR/opt/cloudbolt, where VARDIR is defined in Django settings
    * MEDIA_ROOT and STATIC_TESTS_DIR, where each is defined in Django settings

The tool will not run if either httpd or the jobengine is active. The tool will enable maintenance mode
when it starts and turn it off when it completes, much like an upgrade.

By default, the export will include the job logs directory defined by the JOBTHREAD_LOGPATH
Django setting, which defaults to /var/log/cloudbolt/jobs/. This can be turned off with the
-nj option. If your job log directory is too large, you might wish to handle transferring
your job logs outside of this export process.

You can view what will be included in the default export with the -l command. This will also
list the sizes of those files and directories.

By default, the export will include a database dump of the MySQL database this CloudBolt uses,
but this can be turned off with the -nm option. This utility uses the "mysqldump" command for the
database dump. If including the database dump in the export, the exporter will use the 'default'
database defined in the DATABASES Django setting for database, username, and password. If the password
is not defined in those settings, then the user will be prompted for this password as this utility runs.

By default, includes the following configuration files and directories, but these can be excluded
with -na and -nm options
    * Apache/httpd configuration files: /etc/httpd/conf/httpd.conf, /etc/httpd/conf.d/ssl.conf,
      /etc/httpd/conf.d/wsgi.conf
    * MySQL configuration files: /etc/my.cnf, /etc/mysql/my.cnf

By default, the CloudBolt secrets directory (/var/opt/cloudbolt/secrets) is excluded from the
export, but it can be included with the -is option. The directory contains secret keys used to
encrypt and decrypt sensitive fields stored on the CloudBolt database. CloudBolt will need the
keys in this directory to properly access sensitive fields included in the database dump. If you
do not include the secrets directory in this export, then you must transfer it to your new
CloudBolt in a different manner.

Users can include the -ic option to add certificates to the export. The -ic will tell this utility
to include the following directories: /etc/pki/tls/certs and /etc/pki/tls/private. Including
certificates in an unencrypted .tar.gz file has security implications because secret information
will be saved in a format that anyone can read, so be sure you want to include this information
before using this flag.

Users can specify their own files and directories to include as arguments. They will be extracted
to the same paths on the destination machine by the cb_import utility.

Users can specify specific files and directories to exclude from the import (including default
CloudBolt directories or their children) using the -ex option. Users can include this option as
many times as they want. Excluded directories that are within included directories will be
temporarily moved to /var/tmp/cb_export_tmp while their parent directory is archived and
compressed. Paths to exclude will ALWAYS override default paths and paths to include.

By default, the final compressed export will be saved to the /var/tmp/ directory. This can be
overridden with the -o parameter. The file will be named cbdumpv1_YYYYMMDD_HHMMSS.tgz, where
the YYYYMMDD_HHMMSS is a timestamp.
"""

DEFAULT_MESSAGE: str = """  - CLOUDBOLT DIRECTORIES TO EXPORT:
        {cb_paths}
  - INCLUDE DATABASE DUMP: {db_dump}
  - MYSQL CONF FILES TO EXPORT:
        {mysql_paths}
  - APACHE FILES AND DIRECTORIES TO EXPORT:
        {apache_paths}
"""

START_MESSAGE: str = """  - INCLUDE DATABASE DUMP: {db_dump}
  - FILES AND DIRECTORIES TO EXPORT:
        {paths}
"""


class CBExportError(Exception):
    """Exception for errors during the export"""

    pass


def human_readable_size(num_bytes: int) -> str:
    """Turn a number of bytes into a human readable form. Uses multiple of 1024 and not 1000"""
    kbyte: float = 1024.0
    mbyte: float = kbyte * 1024
    gbyte: float = mbyte * 1024
    if num_bytes < kbyte:
        return f"{num_bytes}B"
    if num_bytes < mbyte:
        return f"{num_bytes / kbyte:.0f}K"
    if num_bytes < gbyte:
        return f"{num_bytes / mbyte:.1f}M"
    return f"{num_bytes / gbyte:.2f}G"


def file_or_dir_size(path: Path) -> int:
    """Return the size of a file or directory in bytes

    Recursively calls itself to calculate directory size
    """
    size: int = path.stat().st_size
    if path.is_dir():
        return sum((file_or_dir_size(p) for p in path.iterdir())) + size
    else:
        return size


def get_path_names_with_size(paths: List[Path], width: int = 70) -> str:
    """Builds a string summary of a list of Paths with their sizes and a summary total size

    Format is:

    path/name/file.txt........................3.4M
    path/name/dir/............................12.5M
    Estimated total size: 15.9M

    :param paths: List[Path], list of paths
    :param width: int, default 70, minimum total width of a row, if path name and size are
        longer nothing is truncated
    """
    path_strs: List[str] = []
    total_size: int = 0
    for p in paths:
        try:
            p_size: int = file_or_dir_size(p)
            total_size += p_size
        except FileNotFoundError:
            p_size = 0
        p_str: str = str(p)
        size_str: str = human_readable_size(p_size)
        pad_size: int = width - len(p_str) - len(size_str)
        pad_size = 0 if pad_size < 1 else pad_size
        path_strs.append(f"{p_str}{'.' * pad_size or 3}{size_str}")
    path_strs.append(f"Estimated total size: {human_readable_size(total_size)}")
    return "\n\t".join(path_strs)


class ExcludeSubPaths(ContextDecorator):
    """Context manager for temporarily copying files/dirs to a temporary location while a parent dir is archived"""

    temp_storage = Path("/var", "tmp", "cb_export_temp")

    def __init__(self, this_path: Path, excluded_paths: List[Path]):
        """Make sure the paths are absolute and that the temp storage location exists"""
        super().__init__()
        self.this_path: Path = this_path.absolute()
        self.excluded_paths: List[Path] = [p.absolute() for p in excluded_paths]
        self.tmp_to_dest_map: Dict[Path, Path] = {}
        if not self.temp_storage.exists():
            self.temp_storage.mkdir()

    def __enter__(self):
        """Copy excluded paths to temporary storage

        If any paths in `self.excluded_paths` are inside of `self.this_path`, then copy
        them to temporary storage and track them in `self.tmp_to_dest_map`
        """
        ex_p: Path
        for ex_p in self.excluded_paths:
            try:
                ex_p.relative_to(self.this_path)
            except ValueError:
                continue
            new_path: Path = Path(self.temp_storage, ex_p.name)
            print(
                f"\t\tTemporarily moving {ex_p} to {new_path} to exclude it from the export",
                end="...",
            )
            ex_p.replace(new_path)
            print("done")
            self.tmp_to_dest_map[new_path] = ex_p
        return self

    def __exit__(self, *exc):
        """Copy files/dirs in temporary storage back to their homes and delete temporary storage"""
        for source, dest in self.tmp_to_dest_map.items():
            print(f"\t\tMoving {dest} back to where it started", end="...")
            source.replace(dest)
            print("done")
        self.temp_storage.rmdir()
        return False


class MaintenanceMode(ContextDecorator):
    """Context manager to turn maintenance mode on and off"""

    def __enter__(self):
        """Start maintenance mode when entering the context"""
        from utilities.maintenance_mode import activate_maintenance_mode

        print("Activating maintenance mode", end="...")
        activate_maintenance_mode()
        print("done")
        return self

    def __exit__(self, *exc):
        """End maintenance mode when leaving the context"""
        from utilities.maintenance_mode import deactivate_maintenance_mode

        print("Deactivating maintenance mode", end="...")
        deactivate_maintenance_mode()
        print("done")
        return False


class Command(BaseCommand):

    help: str = HELP_TEXT

    @staticmethod
    def pre_checks(is_dry_run: bool = False) -> bool:
        """Check that httpd and the jobengine are not running

        Print a warning about pre-9.0 blueprints with container objects

        Return True checks pass, print an error and return False if this is not a dry run
        and httpd or the job engine are running

        :param is_dry_run: bool, optional, default False, whether this is a dry run or not
        """
        from common.methods import is_version_newer
        from servicecatalog.models import ServiceBlueprint

        CB_VERSION = settings.VERSION_INFO["VERSION"]
        # check whether they have IPSIs on CB < 9.0 and warn if so
        if is_version_newer("9.0", CB_VERSION):
            bps_with_ipsis = ServiceBlueprint.objects.filter(
                status="ACTIVE", serviceitem__real_type__model="installpodserviceitem"
            )
            bp_count = bps_with_ipsis.count()
            if bp_count > 0:
                bp_names_and_ids = ", ".join(
                    [f"{bp.name} ({bp.id})" for bp in bps_with_ipsis]
                )
                print(
                    f"You have {bp_count} blueprints with container objects in them. In 9.0+, you will have to "
                    "modify the container objects within these blueprint to associate them with environment(s) "
                    f"before they can be deployed: {bp_names_and_ids}."
                )

        # only do httpd and jobengine checks if this is not a dry run
        if not is_dry_run:
            # check that httpd is off
            httpd_args: List[str] = ["service", "httpd", "status"]
            out: CompletedProcess = subprocess.run(
                httpd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if out.returncode == 0:
                print(
                    "Cannot run the export while Apache (httpd) is running. Please stop httpd with "
                    "'service httpd stop' and then try again."
                )
                return False

            # check that the jobengine is off
            jobengine_args: List[str] = ["pgrep", "jobengine"]
            out: CompletedProcess = subprocess.run(
                jobengine_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if out.returncode == 0:
                print(
                    "Cannot run the export while the job engine is running. Please stop jobengine "
                    "with one of the following commands:"
                    "\n\tCB 8.8: 'supervisorctl stop jobengine:*'"
                    "\n\tCB 8.4-8.7: 'supervisorctl stop celeryd:*'"
                    "\n\tCB 8.0-8.3: 'service crond stop'"
                )
                return False
        return True

    def create_parser(self, *args: str) -> CommandParser:
        """Override to use the RawTextHelpFormatter to preserve formatting of the general helptext"""
        parser: CommandParser = super().create_parser(*args)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-o",
            "--output-dir",
            default="/var/tmp",
            help="Output directory for the export tarball. Will create the directory,"
            " if necessary. Default: /var/tmp",
        )
        parser.add_argument(
            "-nm",
            "--no-mysql",
            action="store_true",
            help="Leave MySQL conf files and the database dump OUT of the export",
        )
        parser.add_argument(
            "-na",
            "--no-apache",
            action="store_true",
            help="Leave Apache/httpd configuration files and directories OUT "
            "of the exoort",
        )
        parser.add_argument(
            "-nj",
            "--no-job-logs",
            action="store_true",
            help="Leave job log files OUT of the exoort",
        )
        parser.add_argument(
            "-ic",
            "--include-certs",
            action="store_true",
            help="Include public and private certificates from /etc/pki/tls. "
            "There are security implications for this because secrets will "
            "be saved to an unencrypted tar.gz file, so be sure you want to "
            "include them",
        )
        parser.add_argument(
            "-is",
            "--include-secrets",
            action="store_true",
            help="Include the CloudBolt secrets directory, which contains key "
            "information used to encrypt and decrypt sensitive fields on "
            "the CloudBolt database",
        )
        parser.add_argument(
            "-ex",
            "--exclude",
            action="append",
            help="Specific files and directories to exclude from the import. "
            "These paths can be sub-directories or file children of directories "
            "being included. This option can be used multiple times",
        )
        parser.add_argument(
            "-l",
            "--list-defaults",
            action="store_true",
            help="List the files and directories that are included by default",
        )
        parser.add_argument(
            "-d",
            "--dry-run",
            action="store_true",
            help="List files that will be included and try to connect to MySQL",
        )
        parser.add_argument(
            "files",
            metavar="CONF_FILE",
            type=str,
            nargs="*",
            help="Specify your own configuration files and dirs to be included in"
            " the export along with the defaults, unless the -s option is set,"
            " in which case the default conf files will NOT be included",
        )

    def get_version(self) -> str:
        """Return version of the CBExporter class"""
        return CBExporter.get_version()

    def handle(self, *args: str, list_defaults: bool = False, **options) -> None:
        if list_defaults:
            CBExporter.print_defaults()
        else:
            is_dry_run: bool = options.get("dry_run", False)
            # if it's a dry run, skip pre-checks and maintenance mode
            if self.pre_checks(is_dry_run):
                if is_dry_run:
                    exporter = CBExporter(**options)
                    exporter.do_archive()
                # turn on maintenance mode if this is NOT a dry run
                else:
                    with MaintenanceMode():
                        exporter = CBExporter(**options)
                        exporter.do_archive()


class CBExporter:
    """Tool for exporting CB configuration files/dirs and the database"""

    default_settings_dirs: List[str] = ["MEDIA_ROOT", "STATIC_TESTS_DIR"]
    job_log_setting: str = "JOBTHREAD_LOGPATH"
    cert_paths: List[str] = ["/etc/pki/tls/certs/", "/etc/pki/tls/private"]
    default_apache_conf_paths: List[str] = [
        "/etc/httpd/conf/httpd.conf",
        "/etc/httpd/conf.d/ssl.conf",
        "/etc/httpd/conf.d/wsgi.conf",
    ]
    default_mysql_conf_paths: List[str] = ["/etc/my.cnf", "/etc/mysql/my.cnf"]
    # tracks mapping from CloudBolt settings to paths on the filesystem
    # {PathObject: (SETTING_NAME, PathObjectWithinSettingDir or None)
    cloudbolt_settings_dirs: Dict[Path, Tuple[str, Optional[Path]]] = {}
    # in case we have later versions that aren't compatible
    version: str = "1.0"

    def __init__(
        self,
        output_dir: str = "/var/tmp",
        no_mysql: bool = False,
        no_apache: bool = False,
        no_job_logs: bool = False,
        include_certs: bool = False,
        include_secrets: bool = False,
        exclude: Optional[List[str]] = None,
        dry_run: bool = False,
        files: Optional[List[str]] = None,
        **kwargs,
    ) -> None:
        # tracks source files/directories and the unique file names we generate for each
        self.path_map: Dict = {}
        self.dry_run: bool = dry_run

        # generate the file name for the export
        export_name: str = self.get_dump_file_name()
        self.tmp_dir: TemporaryDirectory = TemporaryDirectory(prefix=f"{export_name}-")
        self.tmp_dir_path: Path = Path(self.tmp_dir.name)
        # default export directory is /var/tmp
        export_dir: Path = self.get_or_create_export_dir(output_dir)
        self.dest: Path = Path(export_dir, export_name)

        self.exclude_db_dump: bool = no_mysql

        self.paths_to_exclude: List[Path] = []
        if exclude:
            self.paths_to_exclude.extend([Path(p) for p in exclude])
        if not include_secrets:
            secrets_dir: Optional[Path] = self.get_cb_secrets_dir()
            if secrets_dir:
                self.paths_to_exclude.append(secrets_dir)

        # gather the default files and directories to export
        self.paths_to_archive: List[Path] = self.get_default_cb_dirs(
            no_job_logs=no_job_logs
        )
        self.paths_to_archive.extend(
            self.get_default_conf_files(
                no_apache=no_apache, no_mysql=no_mysql, include_certs=include_certs
            )
        )

        # include user-specified files and directories
        custom_paths: List[str] = files or list()
        custom_path_objs: List[Path] = self.verify_custom_paths(custom_paths)
        self.paths_to_archive.extend(custom_path_objs)

        # ensure absolute Paths, remove duplicates, and sort alphabetically
        self.paths_to_archive = sorted(
            set([p.absolute() for p in self.paths_to_archive]),
            key=lambda path: str(path).lower(),
        )

    def do_archive(self) -> None:
        """Do all of the exporting: files/dirs, MySQL dump, compress everything"""
        if self.dry_run:
            print("---STARTING DRY RUN---")
        print("Initializing CloudBolt export with the following settings:")
        print(self.get_starting_status())

        print("Collecting files and directories to export...")
        self.collect_archive_paths()
        print("Collection complete!")

        if not self.exclude_db_dump:
            print("Beginning MySQL dump...")
            self.dump_database()
            print("MySQL dump complete!")

        if not self.dry_run:
            print("Compressing files to export...")
            archive: str = shutil.make_archive(
                str(self.dest),
                format="gztar",
                root_dir=self.tmp_dir_path.parent,
                base_dir=self.tmp_dir_path.name,
            )

        print("Export complete!")

        if self.dry_run:
            print("---ENDING DRY RUN---")
        else:
            print(f"Compressed export is here: {archive}")

    @classmethod
    def print_defaults(cls) -> None:
        cb_paths: List[Path] = sorted(cls.get_default_cb_dirs())
        formatted_cb_paths: str = get_path_names_with_size(cb_paths)

        default_mysql_confs: List[Path] = sorted(
            cls.get_default_conf_files(
                print_status=False, exclude_missing=False, no_apache=True
            )
        )
        formatted_mysql_confs: str = get_path_names_with_size(default_mysql_confs)

        default_apache_confs: List[Path] = sorted(
            cls.get_default_conf_files(
                print_status=False, exclude_missing=False, no_mysql=True
            )
        )
        formatted_apache_confs: str = get_path_names_with_size(default_apache_confs)

        print(
            DEFAULT_MESSAGE.format(
                db_dump=True,
                cb_paths=formatted_cb_paths,
                mysql_paths=formatted_mysql_confs,
                apache_paths=formatted_apache_confs,
            )
        )

    @classmethod
    def get_version(cls) -> str:
        return cls.version

    @classmethod
    def get_cb_secrets_dir(cls) -> Optional[Path]:
        """Return an absolute Path to the CloudBolt secrets directory"""
        var_dir: str = settings.VARDIR
        p: Path = Path(var_dir, "opt", "cloudbolt", "secrets")
        if p.exists():
            return p.absolute()
        return None

    @classmethod
    def get_or_create_export_dir(cls, path: str) -> Path:
        """Get or create the export directory"""
        export_dir_path: Path = Path(path)
        if not (export_dir_path.exists() and export_dir_path.is_dir()):
            try:
                export_dir_path.mkdir()
            except FileExistsError:
                raise CBExportError(
                    f"Cannot export to a specific file, only a directory. '{path}' is a file."
                    f" Please specify a directory."
                ) from None
        return export_dir_path

    @classmethod
    def get_dump_file_name(cls) -> str:
        """Generate the export file name, include version number and timestamp"""
        timestamp: str = timezone.now().strftime("%Y%m%d_%H%M%S")
        return f"cbdump-v{cls.version}_{timestamp}"

    @classmethod
    def get_default_cb_dirs(cls, no_job_logs: bool = False) -> List[Path]:
        """Gather the CloudBolt directories that customers can change

        Track which settings are pointing to which directories in `cloudbolt_settings_dirs`
        so that we can use the setting name in manifest.json instead of the absolute path
        in case the setting points to a different path on the importing CloudBolt

        :param no_job_logs: bool, optional, default False, whether to leave Job logs out
        """
        var_dir: str = settings.VARDIR
        p: Path = Path(var_dir, "opt", "cloudbolt")
        paths: List[Path] = [p]
        cls.cloudbolt_settings_dirs[p] = ("VARDIR", Path("opt", "cloudbolt"))

        setting_dir_names: List[str] = cls.default_settings_dirs
        if not no_job_logs:
            setting_dir_names.append(cls.job_log_setting)

        for setting_name in setting_dir_names:
            p = Path(getattr(settings, setting_name))
            paths.append(p)
            cls.cloudbolt_settings_dirs[p] = (setting_name, None)
        return paths

    @classmethod
    def get_default_conf_files(
        cls,
        print_status: bool = True,
        exclude_missing: bool = True,
        no_apache: bool = False,
        no_mysql: bool = False,
        include_certs: bool = False,
    ) -> List[Path]:
        """Gather the non-CloudBolt configuration files, ignore any that don't exist

        :param print_status: bool, optional, default True, whether to print status messages
        :param exclude_missing: bool, optional, default True, whether to leave nonexistent
            files/dirs out of the list of paths returned
        :param no_apache: bool, optional, default False, whether to leave Apached/httpd
            files and dirs out
        :param no_mysql: bool, optional, default False, whether to leave MySQL
            files and dirs out
        :param include_certs: bool, optional, default False, whether to include certificates
        """
        if print_status:
            print("Collecting configuration files and directories...")
        path_strs: List[str] = []
        path_objs: List[Path] = []
        if not no_apache:
            path_strs.extend(cls.default_apache_conf_paths)
        if not no_mysql:
            path_strs.extend(cls.default_mysql_conf_paths)
        if include_certs:
            path_strs.extend(cls.cert_paths)

        for ps in path_strs:
            path_obj: Path = Path(ps)
            if not path_obj.exists():
                if print_status:
                    print(f"\t{ps} does not exist, leaving out of export")
                if exclude_missing:
                    continue
            path_objs.append(path_obj)
        return path_objs

    def verify_custom_paths(self, custom_paths) -> List[Path]:
        """Gather the user-specified files/dirs and verify that they exist

        :param custom_paths: list of strings that point to files/dirs

        :raises CBExportError: if one of the paths in custom_paths does not exist
        """
        paths: List[Path] = []
        for path_str in custom_paths:
            path_obj: Path = Path(path_str)
            if path_obj.exists():
                paths.append(path_obj)
            else:
                raise CBExportError(
                    f"User-specified path {path_str} does not exist! Please"
                    f" correct or remove from command invocation."
                )
        return paths

    def is_path_excluded(self, path: Path):
        """Returns True if path is on or contained within a path on self.paths_to_exclude"""
        path = path.absolute()
        for exc_path in self.paths_to_exclude:
            try:
                # if path is either in or equal to exc_path
                path.relative_to(exc_path)
                return True
            except ValueError:
                # if path is outside of exc_path
                pass
        return False

    def get_starting_status(self) -> str:
        """Print starting status message that describes what will be included"""
        formatted_paths: str = "\n\t".join([str(p) for p in self.paths_to_archive])
        return START_MESSAGE.format(
            db_dump=(not self.exclude_db_dump), paths=formatted_paths
        )

    def collect_archive_paths(self) -> None:
        """Copy all the files/dirs into our temporary directory

        Each file and dir will receive a UUID as a name to ensure uniqueness.
        Directories will be compressed.
        The manifest.json file records the mapping from the unique name to the original path.
        """
        for path_obj in self.paths_to_archive:
            unique: str = uuid.uuid4().hex

            print(f"\t{path_obj} -> {unique}")

            if self.dry_run:
                continue

            # if this path is specifically excluded or in an excluded path, don't include it
            if self.is_path_excluded(path_obj):
                print(f"\tSkipping excluded path {path_obj}...")
                continue

            unique_path: Path = self.tmp_dir_path.joinpath(unique)
            if path_obj.is_file():
                # copy2 tries to preserve file metadata
                shutil.copy2(path_obj, unique_path)
            elif path_obj.is_dir():
                # this context manager temporarily moves any `paths_to_exclude` that
                # are inside of this dir so that they are not included in the archive
                with ExcludeSubPaths(path_obj, self.paths_to_exclude):
                    shutil.make_archive(
                        str(unique_path),
                        format="gztar",
                        root_dir=path_obj.parent,
                        base_dir=path_obj.name,
                    )
            else:
                print(f"Path {path_obj} is not a file or directory, leaving out...")
                continue

            if path_obj in self.cloudbolt_settings_dirs:
                setting_name, path_within_setting_dir = self.cloudbolt_settings_dirs[
                    path_obj
                ]
                # mark the setting name with a pair of tags
                setting_name_path: Path = Path(f"<cbsetting>{setting_name}<cbsetting>")
                if path_within_setting_dir:
                    # include the path within the setting if it exists
                    setting_name_path = Path(setting_name_path, path_within_setting_dir)
                self.path_map[unique] = str(setting_name_path)
            else:
                self.path_map[unique] = str(path_obj)

        if not self.dry_run:
            manifest_path: Path = Path(self.tmp_dir_path, "manifest.json")
            manifest_path.write_text(json.dumps(self.path_map))

    def dump_database(self) -> None:
        """Dump the CloudBolt database using mysqldump

        Requires that there is an item in the Django DATABASE settings with the key 'default'
        and that it has a 'name' and 'user' defined.

        The use must enter the password when prompted because including it in the command that
        we run is insecure.

        Also includes the HOST and PORT as arguments to mysqldump if those are specified in
        the DATABASE settings
        """
        db_settings: Dict = settings.DATABASES
        database, user, host, port, password = ("",) * 5
        for db_name, db_details in db_settings.items():
            if db_name == "default":
                database = db_details.get("NAME")
                password = db_details.get("PASSWORD")
                user = db_details.get("USER")
                host = db_details.get("HOST")
                port = db_details.get("PORT")
                break

        if not database or not user:
            raise CBExportError("Need database and user in Django settings")

        sub_env: Dict[str, str] = {}
        if password:
            sub_env["MYSQL_PWD"] = password
        command_args: List[str] = ["mysqldump", "-u", user]
        if not password:
            # ask user for password
            print(
                f"Please enter the password for MySQL user '{user}' on database '{database}' when prompted"
            )
            command_args.append("-p")
        if host:
            command_args += ["-h", host]
        if port:
            command_args += ["-P", port]
        command_args += ["--databases", database, "--add-drop-database"]
        out: CompletedProcess = subprocess.run(
            command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=sub_env
        )

        if out.stderr:
            raise CBExportError(f"Failed to run MySQL dump. Got error '{out.stderr}'")
        if not out.stdout:
            raise CBExportError("Failed to run MySQL dump. Received no output")

        if not self.dry_run:
            dump_file_path: Path = Path(self.tmp_dir_path, "cb_mysql_dump.sql")
            dump_file_path.write_bytes(out.stdout)


if __name__ == "__main__":
    # special handling to make sure this runs like a management command regardless
    # of where it is called from
    cloudbolt_home_dir: str = "/opt/cloudbolt"
    if cloudbolt_home_dir not in sys.path:
        sys.path.append(cloudbolt_home_dir)
    environ["DJANGO_SETTINGS_MODULE"] = "settings"
    django.setup()

    command: Command = Command()
    command.run_from_argv(["manage.py"] + sys.argv)
