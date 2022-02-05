#!/usr/bin/env python
# -*- coding: utf-8 -*-


# **********************************************************************************************************************
# File: run_falcon.py
# Project: falcon
# Created: 27.01.2022
# Author: Lalith Kumar Shiyam Sundar
# Email: lalith.shiyamsundar@meduniwien.ac.at
# Institute: Quantitative Imaging and Medical Physics, Medical University of Vienna
# Description: Falcon (FALCON) is a tool for the performing dynamic PET motion correction. It is based on the greedy
# algorithm developed by the Paul Yushkevich. The algorithm is capable of performing fast rigid/affine/deformable
# registration.
# License: Apache 2.0
# **********************************************************************************************************************


import argparse
import logging
import os
import pathlib

import fileop as fop
import greedy
import imageio

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, filename='falcon.log',
                    filemode='w')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--main_folder",
        help="path containing all the subjects with the required structure",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--start_frame",
        default=0,
        help="frame to which the motion correction need to be performed"
    )
    parser.add_argument(
        "-r",
        "--registration",
        default='affine',
        help="Type of registration: rigid | affine | deformable"
    )
    parser.add_argument(
        "-a",
        "--alignment_strategy",
        default='fixed',
        help="Type of alignment: fixed | rolling"
    )
    args = parser.parse_args()
    working_dir = args.main_folder
    start_frame = int(args.start_frame)
    registration = args.registration
    alignment_strategy = args.alignment_strategy
    logging.info('****************************************************************************************************')
    logging.info('                                       Starting FALCON                                              ')
    logging.info('****************************************************************************************************')
    fop.display_logo()
    logging.info('Input arguments:')
    logging.info(' - Working directory: ' + working_dir)
    logging.info(' - Starting frame: ' + str(start_frame))
    logging.info(' - Registration type: ' + registration)
    logging.info(' - Alignment strategy: ' + alignment_strategy)
    logging.info('----------------------------------------------------------------------------------------------------')
    logging.info('                                       SANITY CHECKS                                                ')
    logging.info('----------------------------------------------------------------------------------------------------')

    # -----------------------------------SANITY CHECKS AND DATA-WRANGLING-----------------------------------------------

    # Getting unique extensions in a given folder to check if the folder has multiple image formats

    unique_extensions = imageio.check_unique_extensions(
        directory=working_dir)

    # If the folder has multiple image formats, conversion is a hassle. Therefore, throw an error to clean up the given
    # directory

    if len(unique_extensions) > 1:
        logging.error(f"Multiple file formats found: {unique_extensions} - please check the "
                      f"directory!")

    # If the folder has only one unique image format (e.g, dicom, nifti, analyze, metaimage), convert the non-nifti
    # files to nifti files

    elif len(unique_extensions) == 1:
        logging.info(f"Found files with following extension: {unique_extensions[0]}")
        image_type = imageio.check_image_type(*unique_extensions)
        logging.info(f"Image type: {image_type}")
        if image_type == 'Dicom':  # if the image type is dicom, convert the dicom files to nifti files
            nifti_dir = fop.make_dir(working_dir, 'nifti')
            imageio.dcm2nii(dicom_dir=working_dir)
            nifti_file = fop.get_files(working_dir, wildcard='*nii*')
            fop.move_files(working_dir, nifti_dir, '*.nii*')
        elif image_type == 'Nifti':  # do nothing if the files are already in nifti
            logging.info('Files are already in nifti format!')
            nifti_dir = working_dir
        else:  # any other format (analyze or metaimage) convert to nifti
            nifti_dir = fop.make_dir(working_dir, 'nifti')
            imageio.nondcm2nii(medimg_dir=working_dir, file_extension=unique_extensions[0], new_dir=nifti_dir)

    # Check if the nifti files are 3d or 4d

    nifti_files = fop.get_files(nifti_dir, '*nii*')
    if len(nifti_files) == 1:
        logging.info(f"Number of nifti files: {len(nifti_files)}")
        img_dimensions = imageio.check_dimensions(nifti_files[0])
        if img_dimensions == 3:
            logging.error('Single 3d nifti file found: Cannot perform motion correction!')
        elif img_dimensions == 4:
            logging.info('Type of nifti file : 4d')
            imageio.split4d(nifti_files[0])
            split3d_folder = (fop.make_dir(nifti_dir, 'split3d'))
            fop.move_files(nifti_dir, split3d_folder, 'vol*.nii*')
            logging.info(f"PET files to motion correct are stored here: {split3d_folder}")
    elif len(nifti_files) > 1:
        logging.info('Multiple nifti files found, assuming we have 3d nifti files!')
        split3d_folder = nifti_dir
        logging.info(f"PET files to motion correct are stored here: {split3d_folder}")
    logging.info('----------------------------------------------------------------------------------------------------')
    logging.info('                                      MOTION CORRECTION                                             ')
    logging.info('----------------------------------------------------------------------------------------------------')
    non_moco_files = fop.get_files(split3d_folder, '*nii*')
    logging.info(f"Number of files to motion correct: {len(non_moco_files) - 1}")
    moco_dir = fop.make_dir(split3d_folder, 'moco')
    fop.copy_files(split3d_folder, moco_dir, non_moco_files[-1])
    os.chdir(moco_dir)
    fixed_img_filename = pathlib.Path(non_moco_files[-1]).name
    os.rename(fixed_img_filename, 'moco-' + fixed_img_filename)
    reference_img = fop.get_files(moco_dir, '*nii*')[0]
    if alignment_strategy == 'fixed':
        logging.info(f"Alignment strategy: {alignment_strategy}")
        for y in range(start_frame, len(non_moco_files) - 1):
            greedy.registration(fixed_img=reference_img, moving_img=non_moco_files[y], registration_type=registration)
            moving_img_filename = pathlib.Path(non_moco_files[y]).name
            greedy.resample(fixed_img=reference_img, moving_img=non_moco_files[y], resampled_moving_img=os.path.join(
                moco_dir, 'moco-' + moving_img_filename), registration_type=registration)
        for x in range(0, start_frame):
            fop.copy_files(split3d_folder, moco_dir, pathlib.Path(non_moco_files[x]).name)
            os.chdir(moco_dir)
            os.rename(pathlib.Path(non_moco_files[x]).name, 'moco-' + pathlib.Path(non_moco_files[x]).name)
    elif alignment_strategy == 'rolling':
        logging.info(f"Alignment strategy: {alignment_strategy}")
        for x in range(len(non_moco_files) - 2, start_frame, -1):
            greedy.registration(fixed_img=reference_img, moving_img=non_moco_files[x], registration_type=registration)
            moving_img_filename = pathlib.Path(non_moco_files[x]).name
            greedy.resample(fixed_img=reference_img, moving_img=non_moco_files[x], resampled_moving_img=os.path.join(
                moco_dir, 'moco-' + moving_img_filename), registration_type=registration)
            reference_img = os.path.join(moco_dir, 'moco-' + moving_img_filename)
        for x in range(0, start_frame + 1):
            fop.copy_files(split3d_folder, moco_dir, pathlib.Path(non_moco_files[x]).name)
            os.chdir(moco_dir)
            os.rename(pathlib.Path(non_moco_files[x]).name, 'moco-' + pathlib.Path(non_moco_files[x]).name)

    # Merge the split 3d motion corrected file into a single 4d file using fsl.

    imageio.merge3d(nifti_dir=moco_dir, wild_card='moco-*nii*', nifti_outfile='4d-moco.nii.gz')
