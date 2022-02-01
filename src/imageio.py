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


import os
import pathlib
import re

import SimpleITK
from halo import Halo

import fileop as fop


# Function to check the number of unique file extensions in a directory by getting all the file extensions

def check_unique_extensions(directory):
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


# Function to check if a given extension is nifti, dicom, analyze or metaimage in a given directory

def check_image_type(file_extension):
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


# Function to convert non-nifti files in a given directory to nifti format using convert3d and store it in a new
# directory

def nondcm2nii(medimg_dir, file_extension, new_dir):
    non_dcm_files = fop.get_files(medimg_dir, wildcard='*' + file_extension)
    for file in non_dcm_files:
        file_stem = pathlib.Path(file).stem
        nifti_file = os.path.join(new_dir, file_stem + ".nii.gz")
        cmd_to_run = f"c3d {file} -o {nifti_file}"
        print(f"Converting {file} to {nifti_file}")
        spinner = Halo(text=f"Running command: {cmd_to_run}", spinner='dots')
        spinner.start()
        os.system(cmd_to_run)
        spinner.succeed()
        print("Done")


# Function to convert a given DICOM series into a nifti file using dcm2niix

def dcm2nii(dicom_dir):
    cmd_to_run = f"dcm2niix {re.escape(dicom_dir)}"
    print(f"Converting DICOM images in {dicom_dir} to NIFTI")
    spinner = Halo(text=f"Running command: {cmd_to_run}", spinner='dots')
    spinner.start()
    os.system(cmd_to_run)
    spinner.succeed()
    print("Done")


# Function to split a given 4D nifti file into 3D nifti files

def split4d(nifti_file):
    nifti_file_escaped = re.escape(nifti_file)
    cmd_to_run = f"fslsplit {nifti_file_escaped}"
    print(f"Splitting {nifti_file} into 3D nifti files")
    spinner = Halo(text=f"Running command: {cmd_to_run}", spinner='dots')
    spinner.start()
    os.chdir(pathlib.Path(nifti_file).parent)
    os.system(cmd_to_run)
    spinner.succeed()
    print("Done")


# Function to merge 3D nifti files using wildcard and writing out a single 4D nifti file with a user defined name

def merge3d(nifti_dir, wild_card, nifti_outfile):
    os.chdir(nifti_dir)
    cmd_to_run = f"fslmerge -t {nifti_outfile} {wild_card}"
    print(f"Merging 3D nifti files in {nifti_dir} with wildcard {wild_card}")
    print(f"Running command: {cmd_to_run}")
    os.chdir(nifti_dir)
    os.system(cmd_to_run)
    print("Done")


# Function to check image dimensions of a given nifti file using simpleitk

def check_dimensions(nifti_file):
    nifti_img = SimpleITK.ReadImage(nifti_file)
    img_dim = nifti_img.GetDimension()
    return img_dim
