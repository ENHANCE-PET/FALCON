#!/usr/bin/env python
# -*- coding: utf-8 -*-


# **********************************************************************************************************************
# File: imageIO.py
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


import logging
import os
import pathlib
import re

import SimpleITK
from halo import Halo

import fileOp as fop


def check_unique_extensions(directory: str) -> list:
    """Check the number of unique file extensions in a directory by getting all the file extensions
    :param directory: Directory to check
    :return: Identified unique file extensions
    """
    extensions = []
    for file in os.listdir(directory):
        if file.endswith(".nii") or file.endswith(".nii.gz"):
            extensions.append(".nii")
        elif file.endswith(".DCM") or file.endswith(".dcm"):
            extensions.append(".dcm")
        elif file.endswith(".IMA") or file.endswith(".ima"):
            extensions.append(".ima")
        elif file.endswith(".hdr") or file.endswith('.img'):
            extensions.append(".hdr")
        elif file.endswith(".mha"):
            extensions.append(".mha")
        else:
            extensions.append("unknown")
    extensions_set = set(extensions)
    unique_extensions = list(extensions_set)
    return unique_extensions


def check_image_type(file_extension: str) -> str:
    """Check if a given extension is nifti, dicom, analyze or metaimage in a given directory
    :param file_extension: File extension to check
    :return: Image type
    """
    if file_extension == ".nii":
        return "Nifti"
    elif file_extension == ".dcm" or file_extension == ".ima":
        return "Dicom"
    elif file_extension == ".hdr":
        return "Analyze"
    elif file_extension == ".mha":
        return "Metaimage"
    else:
        return "Unknown"


def nondcm2nii(medimg_dir: str, file_extension: str, new_dir: str) -> None:
    """Convert non-DICOM images to NIFTI
    :param medimg_dir: Directory containing the non-DICOM images (e.g. Analyze, Metaimage)
    :param file_extension: File extension of the non-DICOM images (e.g. .hdr, .mha)
    :param new_dir: Directory to save the converted images
    """
    non_dcm_files = fop.get_files(medimg_dir, wildcard='*' + file_extension)
    for file in non_dcm_files:
        file_stem = pathlib.Path(file).stem
        nifti_file = os.path.join(new_dir, file_stem + ".nii.gz")
        cmd_to_run = f"c3d {file} -o {nifti_file}"
        logging.info(f"Converting {file} to {nifti_file}")
        spinner = Halo(text=f"Running command: {cmd_to_run}", spinner='dots')
        spinner.start()
        os.system(cmd_to_run)
        spinner.succeed()
        logging.info("Done")


def dcm2nii(dicom_dir: str) -> None:
    """Convert DICOM images to NIFTI using dcm2niix
    :param dicom_dir: Directory containing the DICOM images
    """
    cmd_to_run = f"dcm2niix {re.escape(dicom_dir)}"
    logging.info(f"Converting DICOM images in {dicom_dir} to NIFTI")
    spinner = Halo(text=f"Running command: {cmd_to_run}", spinner='dots')
    spinner.start()
    os.system(cmd_to_run)
    spinner.succeed()
    logging.info("Done")


def split4d(nifti_file: str) -> None:
    """Split a 4D NIFTI file into 3D NIFTI files using fslsplit
    :param nifti_file: 4D NIFTI file to split
    """
    nifti_file_escaped = re.escape(nifti_file)
    cmd_to_run = f"fslsplit {nifti_file_escaped}"
    logging.info(f"Splitting {nifti_file} into 3D nifti files")
    spinner = Halo(text=f"Running command: {cmd_to_run}", spinner='dots')
    spinner.start()
    os.chdir(pathlib.Path(nifti_file).parent)
    os.system(cmd_to_run)
    spinner.succeed()
    logging.info("Done")


def merge3d(nifti_dir: str, wild_card: str, nifti_outfile: str) -> None:
    """
    Merge 3D NIFTI files into a 4D NIFTI file using fslmerge
    :param nifti_dir: Directory containing the 3D NIFTI files
    :param wild_card: Wildcard to use to find the 3D NIFTI files
    :param nifti_outfile: User-defined output file name for the 4D NIFTI file
    """
    os.chdir(nifti_dir)
    cmd_to_run = f"fslmerge -t {nifti_outfile} {wild_card}"
    logging.info(f"Merging 3D nifti files in {nifti_dir} with wildcard {wild_card}")
    logging.info(f"Running command: {cmd_to_run}")
    os.chdir(nifti_dir)
    os.system(cmd_to_run)
    logging.info("Done")


def get_dimensions(nifti_file: str) -> int:
    """
    Get the dimensions of a NIFTI image file
    :param nifti_file: NIFTI file to check
    """
    nifti_img = SimpleITK.ReadImage(nifti_file)
    img_dim = nifti_img.GetDimension()
    return img_dim
