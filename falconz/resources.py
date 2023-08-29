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

GREEDY_BINARIES = {
    "greedy-windows-x86_64": {
        "url": "https://greedy.s3.eu.cloud-object-storage.appdomain.cloud/greedy-windows-x86_64.zip",
        "filename": "greedy-windows-x86_64.zip",
        "directory": "greedy-windows-x86_64",
    },
    "greedy-linux-x86_64": {
        "url": "https://greedy.s3.eu.cloud-object-storage.appdomain.cloud/greedy-linux-x86_64.zip",
        "filename": "greedy-linux-x86_64.zip",
        "directory": "greedy-linux-x86_64",
    },
    "greedy-mac-x86_64": {
        "url": "https://greedy.s3.eu.cloud-object-storage.appdomain.cloud/greedy-mac-x86_64.zip",
        "filename": "greedy-mac-x86_64.zip",
        "directory": "greedy-mac-x86_64",
    },
    "greedy-mac-arm64": {
        "url": "https://greedy.s3.eu.cloud-object-storage.appdomain.cloud/greedy-mac-arm64.zip",
        "filename": "greedy-mac-arm64.zip",
        "directory": "greedy-mac-arm64",
    },
}

C3D_BINARIES = {
    "c3d-windows-x86_64": {
        "url": "https://greedy.s3.eu.cloud-object-storage.appdomain.cloud/c3d-windows-x86_64.zip",
        "filename": "c3d-windows-x86_64.zip",
        "directory": "c3d-windows-x86_64",
    },
    "c3d-linux-x86_64": {
        "url": "https://greedy.s3.eu.cloud-object-storage.appdomain.cloud/c3d-linux-x86_64.zip",
        "filename": "c3d-linux-x86_64.zip",
        "directory": "c3d-linux-x86_64",
    },
    "c3d-mac-x86_64": {
        "url": "https://greedy.s3.eu.cloud-object-storage.appdomain.cloud/c3d-mac-x86_64.zip",
        "filename": "c3d-mac-x86_64.zip",
        "directory": "c3d-mac-x86_64",
    },
    "c3d-mac-arm64": {
        "url": "https://greedy.s3.eu.cloud-object-storage.appdomain.cloud/c3d-mac-arm64.zip",
        "filename": "c3d-mac-arm64.zip",
        "directory": "c3d-mac-arm64",
    },
}
