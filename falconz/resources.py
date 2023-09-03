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

FALCON_BINARIES = {
    "falcon-windows-x86_64": {
        "url": "https://greedy.s3.eu.cloud-object-storage.appdomain.cloud/falcon-windows-x86_64.zip",
        "filename": "falcon-windows-x86_64.zip",
        "directory": "falcon-windows-x86_64",
    },
    "falcon-linux-x86_64": {
        "url": "https://greedy.s3.eu.cloud-object-storage.appdomain.cloud/falcon-linux-x86_64.zip",
        "filename": "falcon-linux-x86_64.zip",
        "directory": "falcon-linux-x86_64",
    },
    "falcon-mac-x86_64": {
        "url": "https://greedy.s3.eu.cloud-object-storage.appdomain.cloud/falcon-mac-x86_64.zip",
        "filename": "falcon-mac-x86_64.zip",
        "directory": "falcon-mac-x86_64",
    },
    "falcon-mac-arm64": {
        "url": "https://greedy.s3.eu.cloud-object-storage.appdomain.cloud/falcon-mac-arm64.zip",
        "filename": "falcon-mac-arm64.zip",
        "directory": "falcon-mac-arm64",
    },
}
