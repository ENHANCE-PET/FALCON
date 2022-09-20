#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ***********************************************************************************************************************
# File: fileOp.py
# Project: falcon
# Created: 27.01.2022
# Author: Lalith Kumar Shiyam Sundar
# Email: Lalith.Shiyamsundar@meduniwien.ac.at
# Institute: Quantitative Imaging and Medical Physics, Medical University of Vienna
# Description: Falcon (FALCON) is a tool for the performing dynamic PET motion correction. It is based on the greedy
# algorithm developed by the Paul Yushkevich. The algorithm is capable of performing fast rigid/affine/deformable
# registration.
# License: Apache 2.0
# **********************************************************************************************************************

import glob
import json
import os
import shutil
import natsort
from pathlib import Path
import pydicom as dicom
import SimpleITK as sitk
import numpy as np
from tqdm import tqdm

import pyfiglet


def display_logo():
    """
    Display Falcon logo
    :return:
    """
    print("\n")
    result = pyfiglet.figlet_format("Falcon v0.1", font="speed")
    print(result)

def display_citation():
    """
    Display manuscript citation
    :return:
    """
    print(" L. K. Shiyam Sundar et al. “Fully-automated motion correction of dynamic total-body [18F]FDG PET/CT images using greedy diffeomorphisms, To be submitted: JNM 2022")
    print(" Copyright 2022, Quantitative Imaging and Medical Physics Team, Medical University of Vienna")


def get_folders(dir_path: str) -> list:
    """
    Returns a list of all folders in a directory
    :param dir_path: Main directory containing all folders
    :return: List of folder paths
    """
    # Get a list of folders inside a directory using glob
    folders = glob.glob(os.path.join(dir_path, "*"))
    # Sort the list of folders by name
    folders = natsort.natsorted(folders)
    return folders


def get_files(dir_path: str, wildcard: str) -> list:
    """
    Returns a list of all files in a directory
    :param dir_path: Folder containing all files
    :param wildcard: Wildcard to filter files
    :return: List of file paths
    """
    # Get a list of files inside a directory using glob
    files = glob.glob(os.path.join(dir_path, wildcard))
    # Sort the list of files by name
    files = natsort.natsorted(files)
    return files


def make_dir(dir_path: str, dir_name: str) -> str:
    """
    Creates a new directory
    :param dir_path: Directory path to create the new directory in
    :param dir_name: Name of the new directory
    :return: Path to the new directory
    """
    # Create a directory with user specified name if it does not exist
    if not os.path.exists(os.path.join(dir_path, dir_name)):
        os.mkdir(os.path.join(dir_path, dir_name))

    return os.path.join(dir_path, dir_name)


def move_files(src_dir: str, dest_dir: str, wildcard: str) -> None:
    """
    Moves files from one directory to another
    :param src_dir: Source directory from which files are moved
    :param dest_dir: Target directory to which files are moved
    :param wildcard: Wildcard to filter files that are moved
    :return: None
    """
    # Get a list of files using wildcard
    files = get_files(src_dir, wildcard)
    # Move each file from source directory to destination directory
    for file in files:
        os.rename(file, os.path.join(dest_dir, os.path.basename(file)))


def copy_files(src_dir: str, dest_dir: str, wildcard: str) -> None:
    """
    Copies files from one directory to another
    :param src_dir: Source directory from which files are copied
    :param dest_dir: Target directory to which files are copied
    :param wildcard: Wildcard to filter files that are copied
    :return: None
    """
    # Get a list of files using wildcard
    files = get_files(src_dir, wildcard)
    # Copy each file from source directory to destination directory
    for file in files:
        shutil.copy(file, dest_dir)


def delete_files(dir_path: str, wildcard: str) -> None:
    """
    Deletes files from a directory
    :param dir_path: Path to the directory from which files are deleted
    :param wildcard: Wildcard to filter files that are deleted
    :return: None
    """
    # Get a list of files using wildcard
    files = get_files(dir_path, wildcard)
    # Delete each file from directory
    for file in files:
        os.remove(file)


def compress_files(dir_path: str, wildcard: str) -> None:
    """
    Compresses files using pigz
    :param dir_path: Directory containing files to be compressed
    :param wildcard: Wildcard to filter files that are compressed
    :return: None
    """
    # Get a list of files using wildcard
    files = get_files(dir_path, wildcard)
    # Compress each file using pigz
    for file in files:
        os.system("pigz " + file)


def read_json(file_path: str) -> dict:
    """
    Reads a json file and returns a dictionary
    :param file_path: Path to the json file
    :return: Dictionary
    """
    # Open the json file
    with open(file_path, "r") as json_file:
        # Read the json file and return the dictionary
        return json.load(json_file)


def organise_nii_files_in_folders(dir_path: str, json_files: list) -> None:
    """
    Organises the nifti files in their respective 'modality' folders
    :param dir_path: Directory containing nifti files
    :param json_files: Path to the JSON file
    :return: None
    """
    os.chdir(dir_path)
    for json_file in json_files:
        nifti_file = Path(json_file).stem + ".nii"
        if os.path.exists(nifti_file):
            # Get the modality from the json file
            modality = read_json(json_file)["modality"]
            # Create a new directory for the modality if it does not exist
            make_dir(dir_path, modality)
            # Move the nifti file to the new directory
            move_files(src_dir=dir_path, dest_dir=os.path.join(dir_path, modality), wildcard=nifti_file)

            
            
def push_nii_pixel_data_to_dcm(nifti_file: str, dicom_dir: str, out_dir: str) -> str:
    """
    Pushes the pixel data from a nifti file to the DICOM files in a directory. The DICOM tags are preserved while the
    pixel data is replaced.
    :param nifti_file: Path to the nifti file
    :param dicom_dir: Path to the directory containing DICOM files
    :param out_dir: Path to the output directory
    :return out_dir: Path to the output directory
    """
    print("Reading nifti file as int16...")
    nii_img = sitk.ReadImage(nifti_file, sitk.sitkInt16)
    print("Flipping the nifti image to match the dicom orientation...")
    nii_img = sitk.Flip(nii_img, [True, True, True])
    nii_array = sitk.GetArrayFromImage(nii_img)
    dicom_files = get_files(dicom_dir, "*.dcm")
    # if dicom_files empty use different wildcard
    if not dicom_files:
        dicom_files = get_files(dicom_dir, "*.IMA")
    if np.shape(nii_array)[0] != len(dicom_files):
        raise Exception("Number of slices in nifti file and dicom directory do not match")

    counter = 0
    for dicom_file in tqdm(dicom_files):
        dcm = dicom.read_file(dicom_file)
        dicom_file_name = Path(dicom_file).name
        # inverse rescale slope and intercept
        nii_array[counter, :, :] = np.subtract(nii_array[counter, :, :], int(dcm.RescaleIntercept))
        nii_array[counter, :, :] = np.divide(nii_array[counter, :, :], int(dcm.RescaleSlope))
        # push pixel data to dicom file as int16 stream
        dcm['PixelData'].VR = 'OW'
        dcm.PixelData = nii_array[counter, :, :].astype('uint16').tobytes()
        dcm.save_as(os.path.join(out_dir, dicom_file_name))
        counter += 1

    print("Pushing pixel data to dicom files complete!")
    print("Output DICOM directory: " + out_dir)

    return out_dir
