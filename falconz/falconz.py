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

logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO,
                    filename=datetime.now().strftime('falconz-v.1.0.0.%H-%M-%d-%m-%Y.log'),
                    filemode='w')


def main():
    colorama.init()

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--image4d_directory", type=str,
                        help="Subject directory containing the 4d PET images",
                        required=True)
    parser.add_argument("-r", "--registration", type=str,
                        help="Registration method to use. Options: 'rigid', 'affine', 'deformable'",
                        required=True)
    parser.add_argument("-rf", "--reference_frame", type=str,
                        help="Reference frame to use. Default is the last frame",
                        required=False)
    parser.add_argument("-sf", "--start_frame", type=str,
                        help="Start frame to use, if not provided it will be calculated automatically",
                        required=False)

    args = parser.parse_args()

    image_directory = os.path.abspath(args.image4d_directory)
    registration = args.registration


    display.logo()
    display.citation()

    logging.info('----------------------------------------------------------------------------------------------------')
    logging.info(
        '                                     STARTING FALCON-Z V.2.0.0                                       ')
    logging.info('----------------------------------------------------------------------------------------------------')

    # ----------------------------------
    # INPUT VALIDATION AND PREPARATION
    # ----------------------------------

    logging.info(' ')
    logging.info('- Subject directory: ' + image_directory)
    logging.info(' ')
    print(' ')
    print(f'{constants.ANSI_VIOLET} {emoji.emojize(":memo:")} NOTE:{constants.ANSI_RESET}')
    print(' ')
    display.expectations()

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
    image_conversion.standardize_to_nifti(image_directory)
    print(f"{constants.ANSI_GREEN} Standardization complete.{constants.ANSI_RESET}")
    logging.info(" Standardization complete.")

    # # -------------------------------------------------
    # # RUNNING PREPROCESSING AND REGISTRATION PIPELINE
    # # -------------------------------------------------
    # # calculate elapsed time for the entire procedure below
    # start_time = time.time()
    # print('')
    # print(f'{constants.ANSI_VIOLET} {emoji.emojize(":rocket:")} RUNNING PREPROCESSING AND REGISTRATION PIPELINE:{constants.ANSI_RESET}')
    # print('')
    # logging.info(' ')
    # logging.info(' RUNNING PREPROCESSING AND REGISTRATION PIPELINE:')
    # logging.info(' ')
    # puma_dir, ct_dir, pt_dir = image_processing.preprocess(puma_compliant_subjects)
    # image_processing.align(puma_dir, ct_dir, pt_dir)
    # end_time = time.time()
    # elapsed_time = end_time - start_time
    # # show elapsed time in minutes and round it to 2 decimal places
    # elapsed_time = round(elapsed_time / 60, 2)
    # print(f'{constants.ANSI_GREEN} {emoji.emojize(":hourglass_done:")} Preprocessing and registration complete. Elapsed time: {elapsed_time} minutes!')
