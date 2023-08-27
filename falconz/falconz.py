#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# Author: Lalith Kumar Shiyam Sundar
# Institution: Medical University of Vienna
# Research Group: Quantitative Imaging and Medical Physics (QIMP) Team
# Date: 04.07.2023
# Version: 0.1.0
#
# Description:
# The main module of the falconz. It contains the main function that is executed when the falconz is run.
#
# Usage:
# The variables in this module can be imported and used in other modules within the falconz.
#
# ----------------------------------------------------------------------------------------------------------------------


import argparse
import logging
import os
import sys
import time
from datetime import datetime
import colorama
import emoji

from falconz import display
from falconz import constants
from falconz import file_utilities
from falconz import download
from falconz import resources
from falconz import image_conversion
from falconz import input_validation
from falconz.input_validation import InputValidation

logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO,
                    filename=datetime.now().strftime('falconz-v.1.0.0.%H-%M-%d-%m-%Y.log'),
                    filemode='w')


def main():
    colorama.init()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--main_folder",
        type=str,
        help="path containing the images to motion correct",
        required=True,
    )
    parser.add_argument(
        "-rf",
        "--reference_frame_index",
        type=int,
        default=-1,
        help="index of the reference frame [index starts from 0]",
    )
    parser.add_argument(
        "-sf",
        "--start_frame",
        type=int,
        default=99,
        help="frame from which the motion correction will be performed"
    )
    parser.add_argument(
        "-r",
        "--registration",
        type=str,
        choices=constants.ALLOWED_REGISTRATION_PARADIGMS,
        required=True,
        help="Type of registration: rigid  | affine  | deformable"
    )
    parser.add_argument(
        "-i",
        "--multi_resolution_iterations",
        type=str,
        default=constants.MULTI_RESOLUTION_SCHEME,
        help="Number of iterations for each resolution level"
    )
    args = parser.parse_args()
    validator = InputValidation(args)
    validator.validate()

    display.logo()
    display.citation()

    logging.info('----------------------------------------------------------------------------------------------------')
    logging.info('                                     STARTING FALCON-Z V.2.0.0                                      ')
    logging.info('----------------------------------------------------------------------------------------------------')

    # ----------------------------------
    # INPUT VALIDATION AND PREPARATION
    # ----------------------------------

    print(' ')
    print(f'{constants.ANSI_VIOLET} {emoji.emojize(":memo:")} NOTE:{constants.ANSI_RESET}')
    print(' ')
    display.expectations()
    display.default_parameters(args)
    display.derived_parameters(args)

    # ----------------------------------
    # DOWNLOADING THE BINARIES
    # ----------------------------------

    print('')
    print(f'{constants.ANSI_VIOLET} {emoji.emojize(":globe_with_meridians:")} BINARIES DOWNLOAD:{constants.ANSI_RESET}')

    print('')
    binary_path = constants.BINARY_PATH
    file_utilities.create_directory(binary_path)
    system_os, system_arch = file_utilities.get_system()
    print(f'{constants.ANSI_ORANGE} Detected system: {system_os} | Detected architecture: {system_arch}'
          f'{constants.ANSI_RESET}')
    download.download(item_name=f'greedy-{system_os}-{system_arch}', item_path=binary_path,
                      item_dict=resources.GREEDY_BINARIES)
    file_utilities.set_permissions(constants.GREEDY_PATH, system_os)

    # ----------------------------------
    # INPUT STANDARDIZATION
    # ----------------------------------

    print('')
    print(f'{constants.ANSI_VIOLET} {emoji.emojize(":magnifying_glass_tilted_left:")} STANDARDIZING INPUT DATA TO '
          f'NIFTI:{constants.ANSI_RESET}')
    print('')
    logging.info(' ')
    logging.info(' STANDARDIZING INPUT DATA TO NIFTI:')
    logging.info(' ')
    image_conversion.standardize_to_nifti(args.main_folder)
    print(f"{constants.ANSI_GREEN} Standardization complete.{constants.ANSI_RESET}")
    logging.info(" Standardization complete.")

    # ----------------------------------
