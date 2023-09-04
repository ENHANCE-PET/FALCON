#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: File Operations
   :platform: Unix, Windows
   :synopsis: A module with utilities to handle file operations for falconz.

.. moduleauthor:: Lalith Kumar Shiyam Sundar <email@example.com>

This module provides various utilities to handle file operations necessary for the falconz project.

Usage:
    The functions in this module can be imported and used in other modules within the falconz to perform file operations.
"""

import glob
import os
import platform
import shutil
import stat
import subprocess
import sys
from multiprocessing import Pool

import psutil


def set_permissions(file_path, system_type):
    """
    Sets permissions for a file based on the system type.

    :param file_path: The path to the file.
    :type file_path: str
    :param system_type: The type of the system.
    :type system_type: str
    :raises ValueError: If the system type is not supported.
    """
    if system_type == "windows":
        subprocess.check_call(["icacls", file_path, "/grant", "Everyone:(F)"])
    elif system_type in ["linux", "mac"]:
        os.chmod(file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)  # equivalent to 'chmod u+x'
    else:
        raise ValueError("Unsupported OS")


def get_virtual_env_root():
    """
    Gets the root directory of the virtual environment.

    :return: The root directory of the virtual environment.
    :rtype: str
    """
    python_exe = sys.executable
    virtual_env_root = os.path.dirname(os.path.dirname(python_exe))
    return virtual_env_root


def get_system():
    """
    Gets the system and architecture information.

    :return: A tuple containing the system and architecture information.
    :rtype: tuple
    :raises ValueError: If the system or architecture is not supported.
    """
    system = platform.system().lower()
    architecture = platform.machine().lower()

    # Convert system output to match your keys
    if system == "darwin":
        system = "mac"
    elif system == "windows":
        system = "windows"
    elif system == "linux":
        system = "linux"
    else:
        raise ValueError("Unsupported OS type")

    # Convert architecture output to match your keys
    if architecture in ["x86_64", "amd64"]:
        architecture = "x86_64"
    elif "arm" in architecture:
        architecture = "arm64"
    else:
        raise ValueError("Unsupported architecture")

    return system, architecture


def create_directory(directory_path: str):
    """
    Creates a directory at the specified path.

    :param directory_path: The path to the directory.
    :type directory_path: str
    """
    if not os.path.isdir(directory_path):
        os.makedirs(directory_path)


def get_files(directory_path: str, wildcard: str):
    """
    Gets the files from the specified directory using the wildcard.

    :param directory_path: The path to the directory.
    :type directory_path: str
    :param wildcard: The wildcard to be used.
    :type wildcard: str
    :return: The list of files.
    :rtype: list
    """
    return sorted(glob.glob(os.path.join(directory_path, wildcard)))


def copy_file(file, destination):
    """
    Copies a file to the destination directory.

    :param file: The path to the file.
    :type file: str
    :param destination: The path to the destination directory.
    :type destination: str
    """
    shutil.copy(file, destination)


def copy_files_to_destination(files: list, destination: str):
    """
    Copies the files inside the list to the destination directory in a parallel fashion.

    :param files: The list of files to be copied.
    :type files: list
    :param destination: The path to the destination directory.
    :type destination: str
    """
    with Pool(processes=len(files)) as pool:
        pool.starmap(copy_file, [(file, destination) for file in files])


def select_files_by_modality(tracer_dirs: list, modality_tag: str) -> list:
    """
    Selects the files with the selected modality tag from the tracer directory.

    :param tracer_dirs: Path to the tracer directory.
    :type tracer_dirs: list
    :param modality_tag: The modality tag to be selected.
    :type modality_tag: str
    :return: The list of selected files.
    :rtype: list
    """
    selected_files = []
    for tracer_dir in tracer_dirs:
        files = os.listdir(tracer_dir)
        for file in files:
            if file.startswith(modality_tag) and file.endswith('.nii') or file.endswith('.nii.gz'):
                selected_files.append(os.path.join(tracer_dir, file))
    return selected_files


def organise_files_by_modality(tracer_dirs: list, modalities: list, pumaz_dir) -> None:
    """
    Organises the files by modality.

    :param tracer_dirs: The list of tracer directories.
    :type tracer_dirs: list
    :param modalities: The list of modalities.
    :type modalities: list
    :param pumaz_dir: The path to the pumaz directory.
    :type pumaz_dir: str
    """
    for modality in modalities:
        files_to_copy = select_files_by_modality(tracer_dirs, modality)
        copy_files_to_destination(files_to_copy, os.path.join(pumaz_dir, modality))


def move_file(file, destination):
    """
    Moves a file to the destination directory.

    :param file: The path to the file.
    :type file: str
    :param destination: The path to the destination directory.
    :type destination: str
    """
    shutil.move(file, destination)


def get_number_of_possible_jobs(process_memory: int, process_threads: int) -> int:
    """
    Gets the number of available jobs based on system specifications and process parameters.

    :param process_memory: Specify how much memory a process needs.
    :type process_memory: int
    :param process_threads: Specify how many threads a process needs.
    :type process_threads: int
    :return: Number of possible concurrent jobs as integer number.
    :rtype: int
    """

    # Calculates minimum memory and thread number for process
    min_memory = process_memory * 1024 * 1024 * 1024  # GB
    min_threads = process_threads

    # Get currently available resources
    available_memory = psutil.virtual_memory().available
    available_memory = round(available_memory / 1024 / 1024 / 1024)
    available_threads = psutil.cpu_count()

    # Calculate number (integer) of possible jobs based on memory and thread number
    possible_jobs_memory = available_memory // min_memory
    possible_jobs_threads = available_threads // min_threads

    # Get the smallest value to determine number of jobs
    number_of_jobs = min(possible_jobs_memory, possible_jobs_threads)

    # Set number of jobs to 1, if it was 0 before
    if number_of_jobs == 0:
        number_of_jobs = 1

    return number_of_jobs, available_memory, available_threads
