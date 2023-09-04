#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: display
   :platform: Unix, Windows
   :synopsis: A module with predefined display messages for the falconz.

.. moduleauthor:: Lalith Kumar Shiyam Sundar <lalith.shiyamsundar@meduniwien.ac.at>
.. moduleauthor:: Sebastian Gutschmayer <sebastian.gutschmayer@meduniwien.ac.at>

This module shows predefined display messages for the falconz.

Usage:
    The functions in this module can be imported and used in other modules within the falconz to show predefined display messages.
"""

import logging

import pyfiglet

from falconz import constants
from falconz import file_utilities


def logo():
    """
    Display FALCON logo.

    :return: None
    """
    print(' ')
    logo_color_code = constants.ANSI_VIOLET
    slogan_color_code = constants.ANSI_VIOLET
    result = logo_color_code + pyfiglet.figlet_format("FALCON 2.0", font="speed").rstrip() + "\033[0m"
    text = slogan_color_code + "A part of the ENHANCE community. Join us at https://enhance.pet to build the future " \
                               "of " \
                               "PET imaging together." + "\033[0m"
    print(result)
    print(text)
    print(' ')


def citation():
    """
    Display manuscript citation.

    :return: None
    """
    print(
        " Shiyam Sundar, L. K., Lassen, M. L., Muzik, O. (2023, June 8). Fully automated, fast motion correction of "
        "dynamic whole-body and total-body PET/CT Imaging Studies. Journal of Nuclear Medicine. "
        "https://jnm.snmjournals.org/content/early/2023/06/08/jnumed.122.265362 ")
    print(" Copyright 2022, Quantitative Imaging and Medical Physics Team, Medical University of Vienna")


def expectations():
    """
    Display expected modalities for FALCON. This is used to check if the user has provided the correct set of modalities for each tracer set.

    :return: None
    """
    print(
        f"{constants.ANSI_ORANGE} Warning: Only 4D images will be considered in the analysis. {constants.ANSI_RESET}")

    warning_message = "Only 4D images will be considered in the analysis."
    logging.warning(warning_message)


def default_parameters(input_args):
    """
    Display default parameters for FALCON.

    :param input_args: Input arguments for FALCON.
    :type input_args: argparse.Namespace
    :return: None
    """
    if input_args.reference_frame_index == -1:
        reference_frame_message = " Reference frame: Last frame"
    else:
        reference_frame_message = f" Reference frame: {input_args.reference_frame_index}"
    if input_args.multi_resolution_iterations.__eq__(constants.MULTI_RESOLUTION_SCHEME):
        multi_resolution_scheme_message = f" Multi-resolution scheme: {constants.MULTI_RESOLUTION_SCHEME}"
    else:
        multi_resolution_scheme_message = f" Multi-resolution scheme: {input_args.multi_resolution_iterations}"

    print(f' Registration type: {input_args.registration} | Shrink level: {constants.SHRINK_LEVEL} | '
          f'{multi_resolution_scheme_message} | {reference_frame_message}')


def derived_parameters(input_args):
    """
    Display derived parameters for FALCON.

    :param input_args: Input arguments for FALCON.
    :type input_args: argparse.Namespace
    :return: None
    """
    if input_args.registration.__eq__('rigid'):
        num_jobs, avail_memory, avail_threads = file_utilities.get_number_of_possible_jobs(
            process_memory=constants.MINIMUM_RAM_REQUIRED_RIGID,
            process_threads=constants.MINIMUM_THREADS_REQUIRED_RIGID)
    elif input_args.registration.__eq__('affine'):
        num_jobs, avail_memory, avail_threads = file_utilities.get_number_of_possible_jobs(
            process_memory=constants.MINIMUM_RAM_REQUIRED_AFFINE,
            process_threads=constants.MINIMUM_THREADS_REQUIRED_AFFINE)
    elif input_args.registration.__eq__('deformable'):
        num_jobs, avail_memory, avail_threads = file_utilities.get_number_of_possible_jobs(
            process_memory=constants.MINIMUM_RAM_REQUIRED_DEFORMABLE,
            process_threads=constants.MINIMUM_THREADS_REQUIRED_DEFORMABLE)
    else:
        raise ValueError('Unsupported registration paradigm')

    print(f' Available memory: {avail_memory} GB | Available threads: {avail_threads} | Number of motion correction '
          f'done in parallel: {int(avail_threads * constants.PROPORTION_OF_CORES)}')
    logging.info(f' Available memory: {avail_memory} GB | Available threads: {avail_threads} | Number of motion '
                 f'correction done in parallel: {int(avail_threads * constants.PROPORTION_OF_CORES)}')
    # if input arguments doesn't have start frame, display message saying it will be calculated on the fly
    if input_args.start_frame == 99:
        print(f' {constants.ANSI_ORANGE}Warning: Start frame not provided. It will be calculated on the fly. '
              f'{constants.ANSI_RESET}')
