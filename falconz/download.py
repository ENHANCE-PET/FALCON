#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: download
   :synopsis: This module downloads the necessary binaries and models for the falconz.

.. moduleauthor:: Lalith Kumar Shiyam Sundar <lalith.email@example.com>

.. note::
   Research Group: Quantitative Imaging and Medical Physics (QIMP) Team

**Version**: 0.1.0

**Date**: 04.07.2023

Usage
-----
The functions in this module can be imported and used in other modules within the falconz to download the necessary
binaries and models for the falconz.
"""

import logging
import hashlib
import os
import zipfile
import stat
import tempfile
from pathlib import Path, PurePosixPath

import requests
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, FileSizeColumn, TransferSpeedColumn

from falconz import constants


def download(item_name, item_path, item_dict):
    """
    Downloads the item (model or binary) for the current system.

    :param item_name: The name of the item to download.
    :type item_name: str
    :param item_path: The path to store the item.
    :type item_path: str
    :param item_dict: The dictionary containing item info.
    :type item_dict: dict
    :return: The path to the downloaded item.
    :rtype: str
    """
    item_info = item_dict[item_name]
    root = Path(item_path)
    bundle_name = item_info["directory"]
    if not bundle_name or bundle_name in {".", ".."} or any(c in bundle_name for c in "/\\:"):
        raise ValueError("Binary directory must be a single directory name")
    directory = root / bundle_name
    expected_digest = item_info.get("sha256")
    marker_name = ".falcon-archive-sha256"
    if directory.is_symlink():
        raise ValueError("Binary directory must not be a symbolic link")
    if directory.exists():
        if not directory.is_dir():
            raise ValueError("Binary destination is not a directory")
        marker = directory / marker_name
        if (expected_digest and marker.is_file() and not marker.is_symlink()
                and marker.read_text().strip() == expected_digest):
            logging.info("A verified local instance of %s binaries has been detected", item_name)
            return os.path.join(item_path, item_name)

    root.mkdir(parents=True, exist_ok=True)
    # A private staging directory avoids following existing files or symlinks and
    # keeps incomplete downloads out of the executable installation directory.
    with tempfile.TemporaryDirectory(prefix=".falcon-download-", dir=root) as staging:
        archive = Path(staging) / "download.zip"
        digest = hashlib.sha256()
        with requests.get(item_info["url"], stream=True, timeout=(10, 120)) as response:
            response.raise_for_status()
            with archive.open("wb") as output, Progress(
                TextColumn("[bold blue]{task.description}"), BarColumn(),
                FileSizeColumn(), TransferSpeedColumn(), TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task(
                    f"Downloading system specific binaries: {item_name}",
                    total=int(response.headers.get("Content-Length", 0)),
                )
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
                    progress.update(task, advance=len(chunk))

        if expected_digest and digest.hexdigest() != expected_digest:
            raise ValueError("Binary archive SHA-256 does not match the published digest")

        extracted = Path(staging) / "extracted"
        with zipfile.ZipFile(archive) as zip_ref:
            # Validate the entire archive before writing any member. Only the
            # expected bundle may be installed; other virtualenv files are off limits.
            for member in zip_ref.infolist():
                name = PurePosixPath(member.filename)
                mode = stat.S_IFMT(member.external_attr >> 16)
                if (not name.parts or name.is_absolute() or ".." in name.parts
                        or "\\" in member.filename or ":" in member.filename
                        or name.parts[0] != bundle_name
                        or mode not in {0, stat.S_IFREG, stat.S_IFDIR}):
                    raise ValueError(f"Unsafe binary archive member: {member.filename!r}")
            zip_ref.extractall(extracted)
        bundle = extracted / bundle_name
        if not bundle.is_dir():
            raise ValueError("Archive does not contain the expected binary directory")
        if expected_digest:
            (bundle / marker_name).write_text(expected_digest + "\n")
        # Replace legacy bundles rather than retaining their old Windows ACLs.
        # Keep the prior installation until the verified replacement is ready.
        backup = Path(staging) / "previous"
        if directory.is_symlink():
            raise ValueError("Binary directory must not be a symbolic link")
        if directory.exists():
            directory.rename(backup)
        try:
            bundle.rename(directory)
        except OSError:
            if backup.exists():
                backup.rename(directory)
            raise

    print(f"{constants.ANSI_GREEN} Binaries - download complete. {constants.ANSI_RESET}")
    logging.info("Binaries - download complete")
    return os.path.join(item_path, item_name)
