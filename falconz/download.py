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
import os
import zipfile

import requests
from rich.console import Console
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
    url = item_info["url"]
    filename = os.path.join(item_path, item_info["filename"])
    directory = os.path.join(item_path, item_info["directory"])

    if not os.path.exists(directory):
        logging.info(f" Downloading {directory}")

        # show progress using rich
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("Content-Length", 0))
        chunk_size = 1024 * 10

        console = Console()
        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            FileSizeColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
            expand=True
        )

        with progress:
            task = progress.add_task(f"[white] Downloading system specific binaries: {item_name}", total=total_size)
            for chunk in response.iter_content(chunk_size=chunk_size):
                open(filename, "ab").write(chunk)
                progress.update(task, advance=chunk_size)

        # Unzip the item
        progress = Progress(  # Create new instance for extraction task
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            FileSizeColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
            expand=True
        )

        with progress:
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                total_size = sum((file.file_size for file in zip_ref.infolist()))
                task = progress.add_task(f"[white] Extracting system specific binaries: {item_name}",
                                         total=total_size)
                # Get the parent directory of 'directory'
                parent_directory = os.path.dirname(directory)
                for file in zip_ref.infolist():
                    zip_ref.extract(file, parent_directory)
                    extracted_size = file.file_size
                    progress.update(task, advance=extracted_size)

        logging.info(f" {os.path.basename(directory)} extracted.")

        # Delete the zip file
        os.remove(filename)
        print(f"{constants.ANSI_GREEN} Binaries - download complete. {constants.ANSI_RESET}")
        logging.info(f" Binaries - download complete.")
    else:
        print(f"{constants.ANSI_GREEN} A local instance of {item_name} binaries has been detected. "
              f"{constants.ANSI_RESET}")
        logging.info(f" A local instance of {item_name} has been detected.")

    return os.path.join(item_path, item_name)
