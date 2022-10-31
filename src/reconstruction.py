#!/usr/bin/env python
# -*- coding: utf-8 -*-

# **********************************************************************************************************************
# File: greedy.py
# Project: falcon
# Created: 21.09.2022
# Author: Lalith Kumar Shiyam Sundar
# Email: lalith.shiyamsundar@meduniwien.ac.at
# Institute: Quantitative Imaging and Medical Physics, Medical University of Vienna
# Description: Falcon (FALCON) is a tool for the performing dynamic PET motion correction. It is based on the greedy
# algorithm developed by the Paul Yushkevich. The algorithm is capable of performing fast rigid/affine/deformable
# registration.
# License: Apache 2.0
# **********************************************************************************************************************

# Libraries to import
import logging
import os
import subprocess
import fileOp as fop
import imageOp as iop
import imageIO as iio
import greedy
import argparse
from mpire import WorkerPool
import pathlib


def inverse_align(fixed_img: str, moving_img: str, affine_mat: str, inverse_warp: str, interpolation: str):
    """
    Inverse align a moving image to a fixed image using the affine matrix and the inverse warp
    :param fixed_img: Fixed image
    :param moving_img: Moving image
    :param affine_mat: Affine matrix
    :param inverse_warp: Inverse warp
    :param interpolation: Interpolation method
    """
    cmd = f'greedy -d 3 -rf {fixed_img} -rm {moving_img} -r {affine_mat} {inverse_warp} -n {interpolation} -dof 6'
    logging.info(f'Running command: {cmd}')
    subprocess.run(cmd, shell=True)


# Main Function for performing the reconstruction with motion imposed ct dynamic images


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--moco_folder",
        type=str,
        help="path containing the images that are motion corrected by falcon",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--transform_folder",
        type=str,
        help="Folder that contains the warp files",
        required=True,
    )
    parser.add_argument(
        "-ct",
        "--ct_folder",
        type=str,
        help="Folder that contains the CT images in DICOM",
        required=True,
    )
    parser.add_argument(
        "-pt",
        "--pt_folder",
        type=str,
        help="Folder that contains the PET images in list mode or sinogram format",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--parameter_file",
        type=str,
        help="Parameter file that contains the parameters for the siemens reconstruction",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output_folder",
        type=str,
        help="Folder that contains the reconstructed images",
        required=True,
    )
    args = parser.parse_args()

    # Parse the arguments
    moco_folder = args.moco_folder
    transform_folder = args.transform_folder
    ct_folder = args.ct_folder
    pt_folder = args.pt_folder
    parameter_file = args.parameter_file
    output_folder = args.output_folder

    # Check if the output folder exists, if not create it
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # Convert the DICOM CT images to NIFTI format
    ct_nifti_file = iio.dcm2nii(ct_folder)

    # Get the list of the PT motion corrected images
    pt_moco_list = fop.get_files(moco_folder, ".nii.gz")

    # Align the CT image to the last image in the moco folder rigidly
    logging.info("- Aligning the CT image to the last image in the moco folder rigidly")
    print("- Aligning the CT image to the last image in the moco folder rigidly")
    dyn_ct_folder = fop.make_dir(ct_folder, "Dynamic-CT")
    ct_to_pt_mat_file = greedy.rigid(fixed_img=pt_moco_list[-1], moving_img=ct_nifti_file,
                                     cost_function='NCC 2x2x2',
                                     multi_resolution_iterations='100x25x10')
    ref_ct_nifti_file = os.path.join(dyn_ct_folder, str(len(pt_moco_list)) + "-CT.nii.gz")
    greedy.resample(fixed_img=pt_moco_list[-1], moving_img=ct_nifti_file,
                    resampled_moving_img=ref_ct_nifti_file, registration_type='rigid')
