#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: image_conversion
   :platform: Unix, Windows
   :synopsis: A module to handle image conversion for falconz.

.. moduleauthor:: Lalith Kumar Shiyam Sundar

This module handles image conversion for the falconz.

Usage:
    The functions in this module can be imported and used in other modules within the falconz to perform image conversion.

"""
import logging
import os
import pathlib
import shutil
import subprocess
from typing import List

import dask
import nibabel as nib
import pydicom
from dask import delayed
from falconz.constants import C3D_PATH, VALID_EXTENSIONS, DCM2NIIX_PATH

from falconz import file_utilities as fop


class NiftiConverter:
    """
    A utility for converting various medical image formats in a directory into 3D NIFTI files.

    Attributes:
        input_directory (str): Path to the directory containing input images.
        output_directory (str): Path to the directory where the converted images will be saved.
    """

    def __init__(self, input_directory: str, output_directory: str = None):
        """
        Initializes the NiftiConverter.

        :param str input_directory: Directory containing input images.
        :param str output_directory: Directory for converted images. Defaults to 'converted' in input_directory.
        :raises NiftiConverterError: If the input directory is not accessible or does not exist.
        """
        if not os.path.exists(input_directory):
            raise NiftiConverterError(f"Input directory '{input_directory}' does not exist or is not accessible.")
        self.VALID_EXTENSIONS = VALID_EXTENSIONS
        self.input_directory = input_directory
        self.output_directory = output_directory if output_directory else os.path.join(input_directory, 'converted')
        self._ensure_output_directory_exists()
        self._process_input_directory()

    def _ensure_output_directory_exists(self):
        """Ensures the output directory exists, creating it if necessary."""
        try:
            if not os.path.exists(self.output_directory):
                os.makedirs(self.output_directory)
        except Exception as e:
            raise NiftiConverterError(f"Error creating output directory: {e}")

    def _process_input_directory(self):
        """Processes the input directory based on the image types present."""
        try:
            file_list = [f for f in os.listdir(self.input_directory) if
                         os.path.isfile(os.path.join(self.input_directory, f))]
        except Exception as e:
            raise NiftiConverterError(f"Error processing input directory: {e}")

        if self._contains_dicom_images(file_list):
            self._convert_dicom_series()
        elif len(file_list) == 1:
            self._process_single_image_file(file_list[0])
        else:
            self._process_multiple_image_files(file_list)

    def _contains_dicom_images(self, file_list):
        """
        Checks if the directory contains DICOM images.

        :param list file_list: List of filenames.
        :return: True if DICOM images are detected, False otherwise.
        :rtype: bool
        """
        return any(self._is_dicom(os.path.join(self.input_directory, file)) for file in file_list)

    def _convert_dicom_series(self):
        """Converts DICOM series in the directory to 3D NIFTI files."""
        self.dcm2niix(self.input_directory, self.output_directory)
        # remove the json file
        json_file = [f for f in os.listdir(self.output_directory) if f.endswith('.json')]
        if len(json_file) > 0:
            os.remove(os.path.join(self.output_directory, json_file[0]))

        # Scan the output directory for the generated nifti files
        converted_files = [f for f in os.listdir(self.output_directory) if f.endswith('.nii.gz')]

        for nifti_file in converted_files:
            file_path = os.path.join(self.output_directory, nifti_file)

            # Check if the file is 4D and needs to be split
            if self._is_4d_image(file_path):
                self._split_4d_image(file_path)
                os.remove(file_path)

    def _process_single_image_file(self, file_name):
        """
        Processes a single image file in the directory.

        :param str file_name: Name of the image file.
        """
        full_path = os.path.join(self.input_directory, file_name)
        if not self._has_valid_extension(file_name):
            raise NiftiConverterError(f"Unsupported file format: {file_name}")

        if self._is_4d_image(full_path):
            self._split_4d_image(full_path)
        else:
            raise NiftiConverterError("Only a single 3D volume provided. Expecting a 4D volume or multiple 3D volumes.")

    def _process_multiple_image_files(self, file_list):
        tasks = []  # List to hold delayed tasks
        for file_name in file_list:
            full_path = os.path.join(self.input_directory, file_name)
            if file_name.endswith(('.nii', '.nii.gz')):
                shutil.copy(full_path, self.output_directory)
            elif self._has_valid_extension(file_name):
                # Add the task to the list
                tasks.append(self._convert_to_nifti_format(full_path))

        # Compute the tasks in parallel
        dask.compute(*tasks)

    def _has_valid_extension(self, file_name):
        """
        Checks if a file has a valid image extension.

        :param str file_name: Name of the file.
        :return: True if valid, False otherwise.
        :rtype: bool
        """
        return any(file_name.endswith(ext) for ext in self.VALID_EXTENSIONS)

    def _is_4d_image(self, image_path):
        """
        Checks if a given image is 4D.

        :param str image_path: Path to the image file.
        :return: True if the image is 4D, False otherwise.
        :rtype: bool
        """
        try:
            img = nib.load(image_path)
            return img.ndim == 4
        except:
            return False

    def _is_dicom(self, file_path):
        """
        Checks if a given file is a DICOM image.

        :param str file_path: Path to the file.
        :return: True if the file is a DICOM image, False otherwise.
        :rtype: bool
        """
        try:
            _ = pydicom.dcmread(file_path)
            return True
        except:
            return False

    def _split_4d_image(self, image_path):
        """
        Splits a 4D image into multiple 3D NIFTI volumes.

        :param str image_path: Path to the 4D image file.
        """
        try:
            split_nifti_files = nib.funcs.four_to_three(nib.funcs.squeeze_image(nib.load(image_path)))
            for i, file in enumerate(split_nifti_files):
                # file name should start with vol, with 4 digits, using leading zeros (zfill)
                file_name = 'vol_' + str(i).zfill(4) + '.nii.gz'
                output_path = os.path.join(self.output_directory, file_name)
                nib.save(file, output_path)
        except Exception as e:
            raise NiftiConverterError(f"Error splitting 4D image: {e}")

    @delayed
    def _convert_to_nifti_format(self, image_path):
        try:
            output_path = os.path.join(self.output_directory, f"{pathlib.Path(image_path).stem}.nii.gz")
            cmd_to_run = f"{C3D_PATH} {image_path} -o {output_path}"
            cmd_to_run = cmd_to_run.replace("\n", " ").strip()
            subprocess.run(cmd_to_run, shell=True, check=True)
        except Exception as e:
            raise NiftiConverterError(f"Error converting image to NIFTI: {e}")

    def dcm2niix(self, input_path: str, output_dir: str) -> str:
        """
        Converts DICOM files to NIfTI format using dcm2niix.

        Args:
            input_path (str): The path to the input directory.
            output_dir (str): The path to the output directory.

        Returns:
            str: The path to the output directory.

        Raises:
            NiftiConverterError: If there's an error during DICOM to NIFTI conversion.
        """
        cmd_to_run: List[str] = [DCM2NIIX_PATH, '-z', 'y', '-o', output_dir, input_path]

        try:
            subprocess.run(cmd_to_run, capture_output=True, check=True)
        except subprocess.CalledProcessError:
            raise NiftiConverterError(f"Error during DICOM to NIFTI conversion using dcm2niix.")

        return output_dir


class NiftiConverterError(Exception):
    pass


def merge3d(nifti_dir: str, wild_card: str, nifti_outfile: str) -> None:
    """
    Merge 3D NIFTI files into a 4D NIFTI file using nibabel
    :param nifti_dir: Directory containing the 3D NIFTI files
    :param wild_card: Wildcard to use to find the 3D NIFTI files
    :param nifti_outfile: User-defined output file name for the 4D NIFTI file
    """
    logging.info(f"Merging 3D nifti files in {nifti_dir} with wildcard {wild_card}")
    files_to_merge = fop.get_files(nifti_dir, wild_card)
    nib.save(nib.funcs.concat_images(files_to_merge, False), nifti_outfile)
    os.chdir(nifti_dir)
    logging.info("Done")
