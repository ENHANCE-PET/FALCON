#!/usr/bin/env python3
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
import timeit
from datetime import datetime
import checkArgs
import constants as cnst
import fileOp as fop
import greedy
import imageIO
import imageOp
import sysUtil as su

logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO,
                    filename= datetime.now().strftime('falcon-%H%M%d%m%Y.log'),
                    filemode='w')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--main_folder",
        type=str,
        help="path containing the images to motion correct",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--start_frame",
        type=int,
        default=0,
        help="frame from which the motion correction will be performed"
    )
    parser.add_argument(
        "-r",
        "--registration",
        type=str,
        choices=["rigid", "affine", "deformable"],
        default='affine',
        help="Type of registration: rigid | affine | deformable"
    )
    parser.add_argument(
        "-a",
        "--alignment_strategy",
        type=str,
        choices=['fixed', 'rolling'],
        default='fixed',
        help="Type of alignment: fixed | rolling"
    )
    parser.add_argument(
        "-i",
        "--multi_resolution_iterations",
        type=str,
        default='100x50x25',
        help="Number of iterations for each resolution level"
    )
    args = parser.parse_args()

    working_dir = args.main_folder
    if not checkArgs.dir_exists(working_dir):
        logging.error("Main folder does not exist")
        print("Main folder does not exist")
        exit(1)

    start_frame = args.start_frame
    if not checkArgs.is_non_negative(start_frame):
        logging.error("Start frame must be non-negative")
        print("Start frame must be non-negative")
        exit(1)

    registration = args.registration
    alignment_strategy = args.alignment_strategy

    multi_resolution_iterations = args.multi_resolution_iterations
    if checkArgs.is_string_alpha(checkArgs.remove_char(multi_resolution_iterations, 'x')):
        logging.error("Multi-resolution iterations must be a string of integers separated by 'x'")
        print("Multi-resolution iterations must be a string of integers separated by 'x'")
        exit(1)

    # Figure out the number of jobs that can be run in parallel
    njobs = 1
    if registration.__eq__('rigid'):
        njobs = su.get_number_of_possible_jobs(process_memory=cnst.MINIMUM_RAM_REQUIRED_RIGID,
                                               process_threads=cnst.MINIMUM_THREADS_REQUIRED_RIGID)
    elif registration.__eq__('affine'):
        njobs = su.get_number_of_possible_jobs(process_memory=cnst.MINIMUM_RAM_REQUIRED_AFFINE,
                                               process_threads=cnst.MINIMUM_THREADS_REQUIRED_AFFINE)
    elif registration.__eq__('deformable'):
        njobs = su.get_number_of_possible_jobs(process_memory=cnst.MINIMUM_RAM_REQUIRED_DEFORMABLE,
                                               process_threads=cnst.MINIMUM_THREADS_REQUIRED_DEFORMABLE)
    else:
        logging.error("Registration type not recognized")
        exit(1)

    logging.info('****************************************************************************************************')
    logging.info('                                       STARTING FALCON V.01                                             ')
    logging.info('****************************************************************************************************')
    start = timeit.default_timer()
    fop.display_logo()
    logging.info(' ')
    logging.info('INPUT ARGUMENTS')
    logging.info('-----------------')
    logging.info(' - Working directory: ' + working_dir)
    logging.info(' - Starting frame: ' + str(start_frame))
    logging.info(' - Registration type: ' + registration)
    logging.info(' - Alignment strategy: ' + alignment_strategy)
    logging.info(' - Multi-resolution iterations: ' + multi_resolution_iterations)
    logging.info(' ')
    logging.info('SANITY CHECKS AND DATA PREPARATION')
    logging.info('-----------------------------------')
    logging.info(' ')
    if njobs > 1:
        logging.info(f"Based on the available RAM and available threads, FALCON will run in parallel with {njobs} jobs "
                     f"at a time")
        print(f"Based on the available RAM and available threads, FALCON will run in parallel with {njobs} jobs at a "
              f"time")
    else:
        logging.info("Due to the available RAM and available threads, FALCON will run in serial")
        print("Due to the available RAM and available threads, FALCON will run in serial")

    # -----------------------------------SANITY CHECKS AND DATA-PREPARATION---------------------------------------------

    nifti_dir, input_image_type = imageIO.convert_all_non_nifti(working_dir)

    # Check if the nifti files are 3d or 4d

    nifti_files = fop.get_files(nifti_dir, '*nii*')
    split3d_folder = []
    if len(nifti_files) == 1:
        logging.info(f"Number of nifti files: {len(nifti_files)}")
        img_dimensions = imageOp.get_dimensions(nifti_files[0])
        if img_dimensions == 3:
            logging.error('Single 3d nifti file found: Cannot perform motion correction!')
        elif img_dimensions == 4:
            logging.info('Type of nifti file : 4d')
            imageIO.split4d(nifti_files[0], nifti_dir)
            split3d_folder = (fop.make_dir(nifti_dir, 'split3d'))
            fop.move_files(nifti_dir, split3d_folder, 'vol*.nii*')
            logging.info(f"PET files to motion correct are stored here: {split3d_folder}")
    elif len(nifti_files) > 1:
        logging.info('Multiple nifti files found, assuming we have 3d nifti files!')
        split3d_folder = nifti_dir
        logging.info(f"PET files to motion correct are stored here: {split3d_folder}")
    else:
        split3d_folder = []
        logging.error('No nifti files found: Cannot perform motion correction!')
        exit(1)

    logging.info(' ')

    # Motion correction starts here
    logging.info('MOTION CORRECTION')
    print('')
    print("Motion correction starts here")
    print()
    logging.info('--------------------')
    logging.info('Resampling parameters - Images: Linear interpolation  | Segmentations: Nearest neighbor ')
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
        logging.info(f"Reference image (is fixed): {reference_img}")
        moving_imgs = []
        for y in range(start_frame, len(non_moco_files) - 1):
            moving_imgs.append(non_moco_files[y])
        greedy.align(fixed_img=reference_img, moving_imgs=moving_imgs, registration_type=registration,
                     multi_resolution_iterations=multi_resolution_iterations, njobs=njobs, moco_dir=moco_dir)
        if start_frame != 0:
            for x in range(0, start_frame):
                fop.copy_files(split3d_folder, moco_dir, pathlib.Path(non_moco_files[x]).name)
                logging.info(f"Copying files {pathlib.Path(non_moco_files[x]).name} to {moco_dir}")
                print(f"Copying files {pathlib.Path(non_moco_files[x]).name} to {moco_dir}")
                os.chdir(moco_dir)
                os.rename(pathlib.Path(non_moco_files[x]).name, 'moco-' + pathlib.Path(non_moco_files[x]).name)
        else:
            logging.info('No files to copy! Motion correction is being performed from first frame.')
            print('Motion correction is being performed from first frame...')
    elif alignment_strategy == 'rolling':
        logging.info(f"Alignment strategy: {alignment_strategy}")
        for x in range(len(non_moco_files) - 2, start_frame, -1):
            logging.info(f"Reference image (is rolling): {reference_img}")
            greedy.registration(fixed_img=reference_img, moving_img=non_moco_files[x],
                                registration_type=registration, multi_resolution_iterations=multi_resolution_iterations)
            moving_img_filename = pathlib.Path(non_moco_files[x]).name
            greedy.resample(fixed_img=reference_img, moving_img=non_moco_files[x], resampled_moving_img=os.path.join(
                moco_dir, 'moco-' + moving_img_filename), registration_type=registration)
            reference_img = os.path.join(moco_dir, 'moco-' + moving_img_filename)
        for x in range(0, start_frame + 1):
            fop.copy_files(split3d_folder, moco_dir, pathlib.Path(non_moco_files[x]).name)
            os.chdir(moco_dir)
            os.rename(pathlib.Path(non_moco_files[x]).name, 'moco-' + pathlib.Path(non_moco_files[x]).name)

    # Merge the split 3d motion corrected file into a single 4d file using fsl.

    imageIO.merge3d(nifti_dir=moco_dir, wild_card='moco-*nii*', nifti_outfile='4d-moco.nii.gz')
    logging.info(f"Merged 3d motion corrected files into a single 4d file: {moco_dir}/4d-moco.nii.gz")
    print(f"Merged 3d motion corrected files into a single 4d file: {moco_dir}/4d-moco.nii.gz")
    stop = timeit.default_timer()
    logging.info(' ')
    logging.info('MOTION CORRECTION DONE!')
    print('MOTION CORRECTION DONE!')
    logging.info(f"Total time taken for motion correction: {(stop - start) / 60:.2f} minutes")
    print(f"Total time taken for motion correction: {(stop - start) / 60:.2f} minutes")
    logging.info(' ')
