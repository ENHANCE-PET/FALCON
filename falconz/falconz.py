#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: falconz
   :platform: Unix, Windows
   :synopsis: Main module for the FalconZ project.

.. moduleauthor:: Lalith Kumar Shiyam Sundar <lalith.shiyamsundar@meduniwien.ac.at>

"""

# Importing necessary libraries and modules

import argparse
import logging
import multiprocessing
import os
import shutil
import sys
from datetime import datetime

import colorama
import emoji
from falconz.constants import FALCON_WORKING_FOLDER
from falconz.image_conversion import NiftiConverter, NiftiConverterError, merge3d
from falconz.image_processing import determine_candidate_frames, align
from falconz.input_validation import InputValidation
from rich.console import Console
from rich.progress import Progress, TextColumn, TimeElapsedColumn

from falconz import constants
from falconz import display
from falconz import download
from falconz import file_utilities
from falconz import resources

logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO,
                    filename=datetime.now().strftime('falconz-v.1.0.0.%H-%M-%d-%m-%Y.log'),
                    filemode='w')


def main():
    """
    Main function to execute the FalconZ motion correction pipeline.
    
    It involves the following steps:
    
    1. Initialization (e.g. argument parsing)
    2. Input validation and preparation
    3. Downloading necessary binaries
    4. Standardizing input data
    5. Performing motion correction
    6. Cleaning up and finalizing results
    
    :param None: This function doesn't take any direct arguments, but processes command line arguments.

    :returns: None. But as a side-effect, produces motion-corrected images and other outputs.
    """
    colorama.init()

    # Initialization: Setting up arguments, parsers, etc.

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
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
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default='cruise',
        choices=constants.ALLOWED_MODES,
        help="Mode of operation: cruise | dash"
    )
    args = parser.parse_args()
    validator = InputValidation(args)
    validator.validate()
    # change the multi-resolution scheme if the mode of operation is dash
    if args.mode == 'dash':
        args.multi_resolution_iterations = constants.MULTI_RESOLUTION_SCHEME_DASH


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
    download.download(item_name=f'falcon-{system_os}-{system_arch}', item_path=binary_path,
                      item_dict=resources.FALCON_BINARIES)
    file_utilities.set_permissions(constants.GREEDY_PATH, system_os)
    file_utilities.set_permissions(constants.C3D_PATH, system_os)
    file_utilities.set_permissions(constants.DCM2NIIX_PATH, system_os)

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
    image_dir = os.path.normpath(args.directory)
    parent_dir = os.path.dirname(image_dir)
    falcon_dir = os.path.join(parent_dir, FALCON_WORKING_FOLDER)
    file_utilities.create_directory(falcon_dir)
    split_nifti_dir = os.path.join(falcon_dir, constants.SPLIT_FOLDER)
    file_utilities.create_directory(split_nifti_dir)

    console = Console()

    with Progress(
            TextColumn("[cyan]{task.fields[text]}"),
            TimeElapsedColumn(),
            console=console
    ) as progress:

        base_text = " Standardizing images to NIFTI format • Time elapsed:"
        task = progress.add_task("[cyan]" + base_text,
                                 text=base_text, total=100)

        try:
            image_converter = NiftiConverter(input_directory=image_dir, output_directory=split_nifti_dir)

            # Update the task text to "Standardization complete" in green after the task is done
            progress.update(task, text="[green] Standardization complete • Elapsed time:")
            logging.info(" Standardization complete.")

        except NiftiConverterError as e:
            # Update the task text to "Standardization failed" in red on error
            progress.update(task, text="[red] Standardization failed.")
            logging.error(" Standardization failed.")
            logging.error(e)
            sys.exit(1)

    # ----------------------------------
    # MOTION CORRECTION
    # ----------------------------------

    org_nifti_files = file_utilities.get_files(split_nifti_dir, '*.nii')
    if len(org_nifti_files) == 0:
        org_nifti_files = file_utilities.get_files(split_nifti_dir, '*.nii.gz')
    reference_file = org_nifti_files[args.reference_frame_index]
    candidate_frames = org_nifti_files.copy()
    candidate_frames.remove(reference_file)
    start_frame = args.start_frame
    # choose start frame automatically if not specified
    if args.start_frame == 99:
        n_jobs = multiprocessing.cpu_count()
        start_frame_file = determine_candidate_frames(candidate_frames, reference_file, falcon_dir,
                                                      round(n_jobs / 2))
        # find the index of the start_frame_file in the org_nifti_files list
        start_frame = org_nifti_files.index(start_frame_file)
    # everything from and after start_frame will be motion corrected and will be called moving frames
    moving_frames = org_nifti_files[start_frame:]
    moving_frames.remove(reference_file)
    # everything before that will not be motion corrected and will be called non-moco frames
    non_moco_frames = org_nifti_files[:start_frame]
    print('')
    print(f'{constants.ANSI_VIOLET} {emoji.emojize(":eagle:")} PERFORMING MOTION CORRECTION:{constants.ANSI_RESET}')
    print('')
    logging.info(' ')
    logging.info(' PERFORMING MOTION CORRECTION:')
    logging.info(' ')
    print(f' Number of files to motion correct: {len(moving_frames)} | Reference file: '
          f'{os.path.basename(reference_file)} | Start frame: {start_frame}')
    moco_dir = os.path.join(falcon_dir, constants.MOCO_FOLDER)
    file_utilities.create_directory(moco_dir)
    align(fixed_img=reference_file, moving_imgs=moving_frames, registration_type=args.registration,
          multi_resolution_iterations=args.multi_resolution_iterations, moco_dir=moco_dir)

    # ----------------------------------
    # CLEANING UP
    # ----------------------------------

    # CLEAN TRANSFORMS
    transforms_dir = os.path.join(falcon_dir, constants.TRANSFORMS_FOLDER)
    file_utilities.create_directory(transforms_dir)
    for transform_keyword in constants.TRANSFORMS_KEYWORD:
        transform_files = file_utilities.get_files(split_nifti_dir, transform_keyword)
        if len(transform_files) > 0:
            for transform_file in transform_files:
                shutil.move(transform_file, transforms_dir)
        else:
            continue

    # COPY THE REFERENCE FRAME FROM THE SPLIT NIFTI FOLDER TO THE MOCO FOLDER WITH MOCO PREFIX
    reference_file_name = os.path.basename(reference_file)
    moco_reference_file = os.path.join(moco_dir, constants.MOCO_PREFIX + reference_file_name)
    shutil.copy(reference_file, moco_reference_file)

    # COPY THE NON-MOCO FRAMES FROM THE SPLIT NIFTI FOLDER TO THE MOCO FOLDER WITH MOCO PREFIX
    for non_moco_frame in non_moco_frames:
        non_moco_frame_name = os.path.basename(non_moco_frame)
        moco_non_moco_frame = os.path.join(moco_dir, constants.MOCO_PREFIX + non_moco_frame_name)
        shutil.copy(non_moco_frame, moco_non_moco_frame)

    # MERGE THE 3D MOCO FRAMES TO A 4D NIFTI FILE
    merge3d(moco_dir, constants.MOCO_PREFIX + '*', os.path.join(moco_dir, constants.MOCO_4D_FILE_NAME))
    print(f'{constants.ANSI_GREEN} Motion correction complete: '
          f'Results in {moco_dir} | 4D MoCo file: {constants.MOCO_4D_FILE_NAME}{constants.ANSI_RESET}')
