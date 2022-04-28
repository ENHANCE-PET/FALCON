#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ***********************************************************************************************************************
# File: sysUtil.py
# Project: ENHANCE-PET
# Created: 26.04.2022
# Author: Sebastian Gutschmayer
# Email: sebastian.gutschmayer@meduniwien.ac.at
# Institute: Quantitative Imaging and Medical Physics, Medical University of Vienna
# Description: System utilization functions to perform concurrent processing and system resource monitoring
# License: Apache 2.0
# **********************************************************************************************************************

import time

import psutil
import tqdm


def get_number_of_possible_jobs(process_memory: int, process_threads: int) -> int:
    """
    Gets the number of available jobs based on system specifications and process parameters
    :param process_memory: Specify how much memory a process needs
    :param process_threads: Specify how many threads a process needs
    :return: Number of possible concurrent jobs as integer number
    """

    # Calculates minimum memory and thread number for process
    min_memory = process_memory * 1024 * 1024 * 1024  # GB
    min_threads = process_threads

    # Get currently available resources
    available_memory = psutil.virtual_memory().available
    available_threads = psutil.cpu_count()

    # Calculate number (integer) of possible jobs based on memory and thread number
    possible_jobs_memory = available_memory // min_memory
    possible_jobs_threads = available_threads // min_threads

    # Get the smallest value to determine number of jobs
    number_of_jobs = min(possible_jobs_memory, possible_jobs_threads)

    # Set number of jobs to 1, if it was 0 before
    if number_of_jobs == 0:
        number_of_jobs = 1

    return number_of_jobs


def display_system_load(refresh_interval=0.5) -> None:
    """
    Displays the utilized system load as two bars. Keep in mind that this call locks a thread
    """
    with tqdm.tqdm(total=100, desc='CPU%', position=1, bar_format='{l_bar}{bar}|') as cpu_bar, \
         tqdm.tqdm(total=100, desc='RAM%', position=0, bar_format='{l_bar}{bar}|') as ram_bar:
        while True:
            # Get current utilization
            ram_bar.n = psutil.virtual_memory().percent
            cpu_bar.n = psutil.cpu_percent()
            # Refresh bars
            ram_bar.refresh()
            cpu_bar.refresh()
            time.sleep(refresh_interval)
