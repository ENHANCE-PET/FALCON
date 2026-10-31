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
        "url": "https://github.com/ENHANCE-PET/FALCON/releases/download/falconz-v-2.2.2/beast-binaries-windows-x86_64.zip",
        "filename": "beast-binaries-windows-x86_64.zip",
        "sha256": "4b0419e401bf4e9a65c1f25f421a4301b413d3d380002794b3d637ed413363dc",
        "directory": "beast-binaries-windows-x86_64",
    },
    "falcon-linux-x86_64": {
        "url": "https://github.com/ENHANCE-PET/FALCON/releases/download/falconz-v-2.2.2/beast-binaries-linux-x86_64.zip",
        "filename": "beast-binaries-linux-x86_64.zip",
        "sha256": "41409bef70d42048bfb63dab8884f50bf856b757c149aedd61deb7031ad18dff",
        "directory": "beast-binaries-linux-x86_64",
    },
    "falcon-mac-x86_64": {
        "url": "https://github.com/ENHANCE-PET/FALCON/releases/download/falconz-v-2.2.2/beast-binaries-mac-x86_64.zip",
        "filename": "beast-binaries-mac-x86_64.zip",
        "sha256": "e7ecd6ab2eeb6cbc5c562adda801c12d3a3833f0bdfe8a9bc578577afc3b4659",
        "directory": "beast-binaries-mac-x86_64",
    },
    "falcon-mac-arm64": {
        "url": "https://github.com/ENHANCE-PET/FALCON/releases/download/falconz-v-2.2.2/beast-binaries-mac-arm64.zip",
        "filename": "beast-binaries-mac-arm64.zip",
        "sha256": "f5985f10bf27bcd0e1ab218ec4b164e3550d19efcdb9d82c0eaf4d6781116b8a",
        "directory": "beast-binaries-mac-arm64",
    },
}


# Create a function to get CPU and Memory usage
def get_system_stats():
    cpu_percent = psutil.cpu_percent(interval=None)
    memory_info = psutil.virtual_memory()
    memory_percent = memory_info.percent
    return cpu_percent, memory_percent

