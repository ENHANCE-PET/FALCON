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
from falconz.image_conversion import ImageConverter
from falconz.constants import FALCON_WORKING_FOLDER
from falconz.image_processing import FrameSelector
import multiprocessing

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
    image_dir = args.main_folder
    parent_dir = os.path.dirname(image_dir)
    falcon_dir = os.path.join(parent_dir, FALCON_WORKING_FOLDER)
    file_utilities.create_directory(falcon_dir)
    image_converter = ImageConverter(input_directory=image_dir, output_directory=falcon_dir)
    split_nifti_dir = image_converter.convert()
    print(f"{constants.ANSI_GREEN} Standardization complete.{constants.ANSI_RESET}")
    logging.info(" Standardization complete.")

    # ----------------------------------
    # MOTION CORRECTION
    # ----------------------------------

    org_nifti_files = [os.path.join(split_nifti_dir, f) for f in os.listdir(split_nifti_dir)
                       if f.endswith(('.nii', '.nii.gz')) and os.path.isfile(os.path.join(split_nifti_dir, f))]
    reference_file = org_nifti_files[args.reference_frame_index]
    moving_files = [f for f in org_nifti_files if f != reference_file]
    start_frame = args.start_frame
    if args.start_frame == 99:
        n_jobs = multiprocessing.cpu_count()
        frame_selector = FrameSelector(n_jobs)
        start_frame = frame_selector.determine_candidate_frames(org_nifti_files, reference_file, falcon_dir)

    print('')
    print(f'{constants.ANSI_VIOLET} {emoji.emojize(":running:")} PERFORMING MOTION CORRECTION:{constants.ANSI_RESET}')
    print('')
    logging.info(' ')
    logging.info(' PERFORMING MOTION CORRECTION:')
    logging.info(' ')
    print(f' Number of files to motion correct: {len(moving_files)} | Reference file: '
          f'{os.path.basename(reference_file)} | Start frame: {start_frame}')

