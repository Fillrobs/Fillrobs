#!/usr/bin/env python

import json
import re
import shutil
import subprocess
import sys
import tarfile
from argparse import RawTextHelpFormatter
from os import environ, statvfs
from pathlib import Path
from tempfile import gettempdir, TemporaryDirectory
from typing import Dict, List, Optional

import django
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser


# IF MAKING FUNCTIONAL CHANGES TO THIS FILE #
# Follow the instructions in this doc
# https://docs.google.com/document/d/16Cgul037MmarJK4nRd4WKTmFS2EPgJlXi10PuwMG4AU
# to update our hosted docs with a new downloadable version of this file

HELP_TEXT: str = """Import utility to apply an export created by cb_export

You MUST verify values for the following Django settings before running
this utility: DATABASES, VARDIR, MEDIA_ROOT, and STATIC_TESTS_DIR.
These settings have default values, but this utility will use these settings
to determine which database to connect to and where to extract certain
directories.

EXTRACTION
This utility will extract the import file specified in the command invocation
and then copy the files and directories from the extracted import to their
destinations.

The import file will be extracted to temporary directory that will be deleted
once this command finishes running. Files in the extracted import are deleted
as they are processed to conserve space.

Space requirements are estimated cautiously to prevent a failure mid-import
that leaves CloudBolt in a broken state.

DRY RUN
If running the utility in dry run mode using the -d option, then the import
will be extracted to a temporary directory that will be deleted once the utility
has run. No other changes will be made to the file system or the database.

BACKUPS
By default, the utility will create backups of existing files and directories
before potentially overwriting them. Files will be backed up in place by moving
the existing file to <FILE_NAME>.bak. Directories will be backed up in place as
tarballs with the name <DIR_NAME>.bak.tar.gz. Backups can be turned off with the
-nb option.

OVERWRITING
All files and directories that are written by this utility will maintain owner,
group, permission, and timestamp information. Existing files that match those
in the export will be overwritten. Files within existing directories that the
import utility is writing to will not be deleted, only updated or created.

DATABASE
If the extracted directory contains a cb_mysql_dump.sql file, then that will
be used to load the database, overwriting any existing database that matches
the default defined in the DATABASES Django setting. The database load can
be skipped with the -nd option. If the database load fails, the cb_mysql_dump.sql
file will be copied to the system's temp directory so that it can be run manually
later with `mysql < /<TEMP_DIR>/cb_mysql_dump.sql` where <TEMP_DIR> is the directory
returned by the Python Standard Library function `tempfile.gettempdir()`."""


SPACE_ERR_MSG: str = """Not enough space on system for import. Please free space{no_backups_msg}.

Available space on disk: {available_space}

Import Space Requirements
=========================
    Initial Extract: {initial_extract}
    Backups: {backups}
    Extracted Size of Largest Compressed Directory: {largest_extract}

Space estimates err on the side of caution to prevent failing mid-import
"""


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


def get_extracted_size(path: Path) -> int:
    """Return the extracted size of a .tar or .tar.gz file/directory

    Does not actually extract the input file. If the input file is not a tar
    file, then uses get_file_or_dir_size to determine the file's size and
    returns that.
    """
    try:
        tar = tarfile.open(path)
    except tarfile.ReadError:
        return get_file_or_dir_size(path)
    return sum([m.size for m in tar])


def get_file_or_dir_size(path: Path) -> int:
    """Return the size of a file or directory in bytes

    Recursively calls itself to calculate directory size
    """
    if not path.exists():
        return 0
    size: int = path.stat().st_size
    if path.is_dir():
        return sum((get_file_or_dir_size(p) for p in path.iterdir())) + size
    else:
        return size


def get_available_system_bytes(path_str: str) -> int:
    """Return the number of bytes available on the system's disk"""
    svfs = statvfs(path_str)
    # block size * number of free blocks
    return svfs.f_bsize * svfs.f_bfree


class CBImportError(Exception):
    pass


class Command(BaseCommand):

    help: str = HELP_TEXT

    def create_parser(self, *args: str) -> CommandParser:
        """Override to use the RawTextHelpFormatter to preserve formatting of the general helptext"""
        parser: CommandParser = super().create_parser(*args)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "source", type=str, help="Absolute or relative path of the import file"
        )
        parser.add_argument(
            "-nd",
            "--no-database-load",
            action="store_true",
            help="Option to skip loading the database from the MySQL dump, if one "
            "exists in the import file",
        )
        parser.add_argument(
            "-nb",
            "--no-backups",
            action="store_true",
            help="Do NOT create backups for files and directories in the import "
            "that already exist on the file system",
        )
        parser.add_argument(
            "-d",
            "--dry-run",
            action="store_true",
            help="Run the import and print out what changes WOULD be made, but "
            "don't actually make any changes",
        )

    def get_version(self) -> str:
        """Return version of the CBExporter class"""
        return CBImporter.get_version()

    def handle(self, *args: str, **options) -> None:
        importer = CBImporter(**options)
        importer.do_import()


def _setting_replacer(match_obj) -> str:
    """Utility function to pass into `re.sub`

    Accepts a re.Match object and returns the string value of the setting_name in the match
    Counts on being passed into re.sub to actually work
    """
    setting_name: str = match_obj.groupdict()["setting_name"]
    setting_val: Optional[str] = getattr(settings, setting_name, None)
    if not setting_val:
        raise CBImportError(f"No setting value found for setting {setting_name}")
    print(f"\tReplacing setting placeholder for {setting_name} with {setting_val}")
    return setting_val


class CBImporter:
    """Tool for exporting CB configuration files/dirs and the database"""

    # in case we have later versions that aren't compatible
    version: str = "1.0"

    def __init__(
        self,
        source: str,
        no_database_load: bool = False,
        no_backups: bool = False,
        dry_run: bool = False,
        **kwargs,
    ) -> None:
        path_obj: Path = Path(source)
        if not path_obj.exists():
            raise FileNotFoundError(f"Cannot find import file '{source}'")
        self.source_path: Path = path_obj
        self.no_database_load: bool = no_database_load
        self.do_backups: bool = not no_backups
        self.dry_run: bool = dry_run
        # get number of available bytes on the disk
        self.available_system_space: int = get_available_system_bytes(
            getattr(settings, "PROSERV_DIR", "/var/opt/cloudbolt")
        )

        self.temp_dir: Optional[TemporaryDirectory] = None
        self.import_dir_path: Optional[Path] = None
        self.extracted_import_path: Path = Path()
        self.manifest: Dict[str, str] = {}
        self.file_map: Dict[Path, Path] = {}
        self.dir_map: Dict[Path, Path] = {}

    @classmethod
    def get_version(cls) -> str:
        return cls.version

    def get_import_dir(self) -> Path:
        """Return a path to the temporary directory to which the import should be extracted

        return: Path
        """
        # always use a temporary directory for a dry run
        print("Creating a temporary directory to store the extracted import", end="...")
        self.temp_dir = TemporaryDirectory()
        print(f"{self.temp_dir.name}")
        return Path(self.temp_dir.name).absolute()

    @staticmethod
    def replace_setting_name(path_str: str) -> str:
        """Replaces the setting name in a path with the value of that setting

        If there is no <cbsetting>SETTING<cbsetting> in the path, the original path is returned
        If there is a <cbsetting>SETTING<cbsetting>, then that part of the path will be replaced
        with the value of the setting.

        For example "<cbsetting>MEDIA_ROOT<cbsetting>/foo/bar/" will become
        "/var/www/html/cloudbolt/static/uploads/foo/bar/" if MEDIA_ROOT is defined as
        /var/www/html/cloudbolt/static/uploads/ in settings.py or customer_settings.py
        """
        print(f"\tChecking for setting name in {path_str}")
        pattern: str = r"(?P<whole_match>\<cbsetting\>(?P<setting_name>.*)\<cbsetting\>)"
        return re.sub(pattern, _setting_replacer, path_str)

    def initial_extract(self):
        """Extract the CloudBolt import file to the path specified by self.get_import_dir

        Sets self.extracted_import_path
        """
        self.import_dir_path = self.get_import_dir()
        print(
            f"Unpacking archive {self.source_path} into {self.import_dir_path}",
            end="...",
        )
        try:
            shutil.unpack_archive(
                str(self.source_path.absolute()), extract_dir=str(self.import_dir_path)
            )
        except OSError as exc:
            raise CBImportError(
                "Encountered system error while extracting import .tar.gz file. You "
                "might need to free space on disk to perform the import."
            ) from exc
        print("done")
        # first and only item in the extracted import should be a dir of all the import stuff
        self.extracted_import_path = next(self.import_dir_path.iterdir())

    def verify_extract(self) -> None:
        """Verify that everything in manifest.json is in the extracted import directory

        Build the dir_map and file_map instance attribute dicts to track which files
        and directories are associated with which files in the import. Pass each destination
        file name through CBImporter.replace_setting_name to get the right setting values
        for paths that use a setting value.
        """
        print("Searching for manifest.json in extracted import", end="...")
        manifest_path: Path = Path(self.extracted_import_path, "manifest.json")
        if not manifest_path.exists():
            raise CBImportError(
                "No 'manifest.json' found in extracted import! This is necessary "
                "to extract files and directories to the right places. Quitting..."
            )
        self.manifest = json.loads(manifest_path.read_text())
        print("found")

        print(
            f"Verifying contents of {manifest_path} and checking disk space", end="..."
        )
        total_extracted_size: int = 0
        largest_extract_size: int = 0
        backups_size: int = 0
        for local, dest in self.manifest.items():
            # check for non-compressed file
            local_path: Path = Path(self.extracted_import_path, local)
            print(f"\n\tChecking for file {local_path.name}", end="...")
            if not local_path.exists():
                # if no plain file, check for tarball with this name
                local_path = local_path.with_suffix(".tar.gz")
                print(
                    f"\n\tChecking for compressed directory {local_path.name}",
                    end="...",
                )

            if not (local_path and local_path.exists()):
                raise CBImportError(
                    f"No file with name '{local}' exists in the extracted import, but "
                    f"is listed in the manifest.json as linked to {dest}. Quitting..."
                )
            else:
                print("found")
            # will only replace a setting if it actually exists in the destination
            dest_with_setting_replaced: Path = Path(self.replace_setting_name(dest))
            # only compressed dirs have a suffix in our export format
            print(
                f"Mapping import path {local_path.name} to {dest_with_setting_replaced}"
            )
            if local_path.suffix:
                # this is a compressed directory
                self.dir_map[local_path] = Path(dest_with_setting_replaced)
            else:
                self.file_map[local_path] = Path(dest_with_setting_replaced)

            # do size calculations
            if self.do_backups:
                backups_size += get_file_or_dir_size(dest_with_setting_replaced)
            local_extracted_size: int = get_extracted_size(local_path)
            total_extracted_size += local_extracted_size
            if local_extracted_size > largest_extract_size:
                largest_extract_size = local_extracted_size
        self.check_available_space(
            total_extracted_size, largest_extract_size, backups_size
        )

    def check_available_space(
        self,
        total_extracted_size: int,
        largest_extract_size: int,
        backups_size: int = 0,
    ) -> None:
        """Check that the import will not run out of space during its run

        This method does not make any changes to the file system.

        Because the import is a .tar.gz file that contains other .tar.gz files. This method
        expects the OUTER .tar.gz file to have already been extracted to `extracted_import_path`

        Raises a very verbose CBImportError if the sum of total_extracted_size,
        largest_extract_size, and backups_size exceeds the available space on the file system.
        This sum is an estimate of the greatest amount of space that might be required at a
        single time as the import runs.

        :param total_extracted_size: the total number of bytes required by the fully extracted
            import directory
        :param largest_extract_size: the extracted size (in bytes) of the largest file/dir in
            the initial extract
        :param backups_size: total number of bytes required by backups
        """
        print("Checking available space", end="...")
        # prepare the error message frame
        err_message: str = SPACE_ERR_MSG
        if backups_size:
            no_backups_msg: str = " and/or run the utility with the --no-backups option"
        else:
            no_backups_msg = ""

        if (
            total_extracted_size + largest_extract_size + backups_size
        ) >= self.available_system_space:
            initial_extract_size: int = get_file_or_dir_size(self.extracted_import_path)
            raise CBImportError(
                err_message.format(
                    no_backups_msg=no_backups_msg,
                    available_space=human_readable_size(self.available_system_space),
                    initial_extract=human_readable_size(initial_extract_size),
                    backups=human_readable_size(backups_size),
                    largest_extract=human_readable_size(largest_extract_size),
                )
            )
        print("done")

    def copy_files(self, do_backups: bool = True) -> None:
        """Copy files in self.file_map to their destinations

        By default, backup files that already exist in place, by appending .bak. All files,
        both those coming from the import and those being backed up will have their owner,
        group, permissions, and update times preserved

        :param do_backups: bool, optional, default True, whether to backup files
        """
        # source and dest should be Path instances
        for source, dest in self.file_map.items():
            # if we're doing backups and this file exists
            if do_backups and dest.exists():
                print(f"Backing up existing file {dest} to {dest}.bak")
                if not self.dry_run:
                    # move existing file to a backup and append .bak to the name
                    dest.replace(f"{dest}.bak")
            else:
                print(f"Creating parent directory {dest.parent}")
                if not self.dry_run:
                    # make sure the destination parent directory exists, creating it if necessary
                    dest.parent.mkdir(exist_ok=True)
            print(f"Moving {source} to {dest}", end="...")
            if not self.dry_run:
                shutil.move(str(source), str(dest))
            print("done\n")

    def copy_dirs(self, do_backups: bool = True) -> None:
        """Copy directories in self.dir_map to their destinations

        By default, backs up directories that already exist in place in a file named
        <NAME>.bak.tar.gz. Will overwrite files that already exist in the destination dir
        if those files are ALSO in the extracted directory. Files that ONLY exist
        in the destination dir will not be touched.

        :param do_backups: bool, optional, default True, whether to backup dirs
        """
        # source and dest should be Path instances
        for source, dest in self.dir_map.items():
            # if we're doing backups and this file exists
            if do_backups and dest.exists():
                print(
                    f"Backing up existing directory {dest} to {dest}.bak.tar.gz",
                    end="...",
                )
                if not self.dry_run:
                    # make an in-place backup tarball named <NAME>.bak.tar.gz
                    shutil.make_archive(
                        f"{dest}.bak",
                        format="gztar",
                        root_dir=dest.parent,
                        base_dir=dest.name,
                    )
                print("done")
            else:
                print(f"Creating parent directory {dest.parent}")
                if not self.dry_run:
                    # make sure the destination parent directory exists, creating it if necessary
                    dest.parent.mkdir(exist_ok=True)

            # unpack the archive
            print(
                f"Unpacking {source} into {dest.parent} and deleting {source}",
                end="...",
            )
            if not self.dry_run:
                shutil.unpack_archive(str(source), str(dest.parent))
                source.unlink()
            print("done\n")

    def load_database(self) -> None:
        """If there is a database dump in the import dir, try to load it into MySQL

        Basically runs "mysql < cb_mysql_dump.sql" in the command line with the various
        options to specify the right user, password, host, and port. If no database dump
        exists in the import directory, prints a message and moves on.
        """
        dump_file_name: str = "cb_mysql_dump.sql"
        dump_path: Path = Path(self.extracted_import_path, dump_file_name)
        if not dump_path.exists():
            print(f"No file '{dump_file_name}' found. Skipping MySQL import")
            return
        # get Database settings
        print("Getting Django DATABASE setting", end="...")
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
            raise ValueError("Need database and user in Django settings")
        print("done")

        sub_env: Dict[str, str] = {}
        if password:
            sub_env["MYSQL_PWD"] = password
        command_args: List[str] = ["mysql", "-u", user]
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

        # command_args += [database, "<", str(dump_path)]
        print(f"Starting MySQL load from {dump_path}...")
        if not self.dry_run:
            # pass the an open file of the dump_path as input to MySQL to run the database load
            out: subprocess.CompletedProcess = subprocess.run(
                command_args,
                stdin=open(dump_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=sub_env,
            )

            if out.stderr:
                new_path: Path = Path(gettempdir(), dump_path.name)
                shutil.move(str(dump_path), str(new_path))
                raise Exception(
                    f"Failed to run MySQL load.\nCopied MySQL dump from import {self.source_path} "
                    f" to {new_path} so that it can be run manually with 'mysql < {new_path}'."
                    f"\nMySQL error details: '{out.stderr}'"
                )
        print("MySQL load complete!")

    def do_import(self) -> None:
        """Main function for running the import"""
        if self.dry_run:
            print("---STARTING DRY RUN---")
        self.initial_extract()
        print()
        try:
            self.verify_extract()
        except CBImportError as exc:
            print(
                "\nERROR: Import failed during initial verification. NO CHANGES WERE MADE. Details follow..."
            )
            print(exc)
            return

        print()
        self.copy_files(do_backups=self.do_backups)
        print()
        self.copy_dirs(do_backups=self.do_backups)
        if not self.no_database_load:
            self.load_database()
        self.temp_dir.cleanup()
        if self.dry_run:
            print("\n---ENDING DRY RUN---")


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
