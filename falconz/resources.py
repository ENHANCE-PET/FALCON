#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: resources
   :platform: Unix, Windows
   :synopsis: A module for storing urls and filenames of the binaries required for the falconz.

.. moduleauthor:: Lalith Kumar Shiyam Sundar <lalith.shiyamsundar@meduniwien.ac.at>

This module contains the urls and filenames of the binaries that are required for the falconz.

Usage:
    The variables in this module can be imported and used in other modules within the falconz to download the necessary
    binaries for the falconz.
"""
import psutil

FALCON_BINARIES = {
    "falcon-windows-x86_64": {
        "url": "https://enhance-pet.s3.eu-central-1.amazonaws.com/awesome/beast-binaries-windows-x86_64.zip",
        "filename": "beast-binaries-windows-x86_64.zip",
        "directory": "beast-binaries-windows-x86_64",
    },
    "falcon-linux-x86_64": {
        "url": "https://enhance-pet.s3.eu-central-1.amazonaws.com/awesome/beast-binaries-linux-x86_64.zip",
        "filename": "beast-binaries-linux-x86_64.zip",
        "directory": "beast-binaries-linux-x86_64",
    },
    "falcon-mac-x86_64": {
        "url": "https://enhance-pet.s3.eu-central-1.amazonaws.com/awesome/beast-binaries-mac-x86_64.zip",
        "filename": "beast-binaries-mac-x86_64.zip",
        "directory": "beast-binaries-mac-x86_64",
    },
    "falcon-mac-arm64": {
        "url": "https://enhance-pet.s3.eu-central-1.amazonaws.com/awesome/beast-binaries-mac-arm64.zip",
        "filename": "beast-binaries-mac-arm64.zip",
        "directory": "beast-binaries-mac-arm64",
    },
}


# Create a function to get CPU and Memory usage
def get_system_stats():
    cpu_percent = psutil.cpu_percent(interval=None)
    memory_info = psutil.virtual_memory()
    memory_percent = memory_info.percent
    return cpu_percent, memory_percent

