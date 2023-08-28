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
import SimpleITK
import contextlib
import dcm2niix
import dicom2nifti
import io
import logging
import nibabel as nib
import os
import pydicom
import re
import unicodedata
from typing import Optional

from falconz import file_utilities as fop


class ImageConverter:
    def __init__(self, input_directory: str, output_directory: str):
        """
        Initializes an ImageConverter object.

        :param input_directory: The path to the input directory.
        :type input_directory: str
        :param output_directory: The path to the output directory.
        :type output_directory: str
        """
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.split_nifti_directory = os.path.join(self.output_directory, 'split-nifti-files')

        if not os.path.exists(self.split_nifti_directory):
            os.makedirs(self.split_nifti_directory)

    def non_nifti_to_nifti(self, input_path: str, output_directory: Optional[str] = None) -> None:
        """
        Converts non-NIfTI files to NIfTI format.

        :param input_path: The path to the input file or directory.
        :type input_path: str
        :param output_directory: The path to the output directory.
        :type output_directory: str
        :return: None
        """
        if not os.path.exists(input_path):
            print(f"Input path {input_path} does not exist.")
            return

        if os.path.isdir(input_path):
            dicom_info = self.create_dicom_lookup(input_path)
            nifti_dir = self.dcm2niix(input_path, output_directory)
            self.rename_nifti_files(nifti_dir, dicom_info)
            return

        if os.path.isfile(input_path):
            _, filename = os.path.split(input_path)
            if filename.startswith('.') or filename.endswith(('.nii.gz', '.nii')):
                return
            else:
                output_image = SimpleITK.ReadImage(input_path)
                output_image_basename = f"{os.path.splitext(filename)[0]}.nii"

        if output_directory is None:
            output_directory = os.path.dirname(input_path)

        output_image_path = os.path.join(output_directory, output_image_basename)
        SimpleITK.WriteImage(output_image, output_image_path)

    def dcm2niix(self, input_path: str, output_dir: str) -> str:
        """
        Converts DICOM files to NIfTI format using dcm2niix.

        :param input_path: The path to the input directory.
        :type input_path: str
        :param output_dir: The path to the output directory.
        :type output_dir: str
        :return: The path to the output directory.
        :rtype: str
        """
        # Save the original stdout and stderr file descriptors.
        original_stdout_fd = os.dup(1)
        original_stderr_fd = os.dup(2)

        # Open a null file to redirect the output.
        with open(os.devnull, 'w') as null_file:
            null_fd = null_file.fileno()

            # Redirect stdout and stderr to the null file.
            os.dup2(null_fd, 1)
            os.dup2(null_fd, 2)

            try:
                dcm2niix.main(['-z', 'y', '-o', output_dir, input_path])
            finally:
                # Restore the original stdout and stderr file descriptors.
                os.dup2(original_stdout_fd, 1)
                os.dup2(original_stderr_fd, 2)
                os.close(original_stdout_fd)
                os.close(original_stderr_fd)

        return output_dir

    def remove_accents(self, unicode_filename):
        """
        Removes accents from a Unicode filename.

        :param unicode_filename: The Unicode filename to remove accents from.
        :type unicode_filename: str
        :return: The filename without accents.
        :rtype: str
        """
        try:
            unicode_filename = str(unicode_filename).replace(" ", "_")
            cleaned_filename = unicodedata.normalize('NFKD', unicode_filename).encode('ASCII', 'ignore').decode('ASCII')
            cleaned_filename = re.sub(r'[^\w\s-]', '', cleaned_filename.strip().lower())
            cleaned_filename = re.sub(r'[-\s]+', '-', cleaned_filename)
            return cleaned_filename
        except:
            return unicode_filename

    def is_dicom_file(self, filename):
        """
        Determines if a file is a DICOM file.

        :param filename: The name of the file to check.
        :type filename: str
        :return: True if the file is a DICOM file, False otherwise.
        :rtype: bool
        """
        try:
            pydicom.dcmread(filename)
            return True
        except pydicom.errors.InvalidDicomError:
            return False

    def create_dicom_lookup(self, dicom_dir):
        """
        Creates a dictionary of DICOM file information.

        :param dicom_dir: The path to the directory containing DICOM files.
        :type dicom_dir: str
        :return: A dictionary of DICOM file information.
        :rtype: dict
        """
        dicom_info = {}
        for filename in os.listdir(dicom_dir):
            full_path = os.path.join(dicom_dir, filename)
            if self.is_dicom_file(full_path):
                ds = pydicom.dcmread(full_path)
                series_number = ds.SeriesNumber if 'SeriesNumber' in ds else None
                series_description = ds.SeriesDescription if 'SeriesDescription' in ds else None
                sequence_name = ds.SequenceName if 'SequenceName' in ds else None
                protocol_name = ds.ProtocolName if 'ProtocolName' in ds else None
                series_instance_UID = ds.SeriesInstanceUID if 'SeriesInstanceUID' in ds else None
                if ds.Modality == 'PT':
                    modality = 'PET'
                else:
                    modality = ds.Modality

                if series_number is not None:
                    base_filename = self.remove_accents(series_number)
                    if series_description is not None:
                        anticipated_filename = f"{base_filename}_{self.remove_accents(series_description)}.nii"
                    elif sequence_name is not None:
                        anticipated_filename = f"{base_filename}_{self.remove_accents(sequence_name)}.nii"
                    elif protocol_name is not None:
                        anticipated_filename = f"{base_filename}_{self.remove_accents(protocol_name)}.nii"
                else:
                    anticipated_filename = f"{self.remove_accents(series_instance_UID)}.nii"

                dicom_info[anticipated_filename] = modality
        return dicom_info

    def rename_nifti_files(self, nifti_dir, dicom_info):
        """
        Renames NIfTI files based on DICOM file information.

        :param nifti_dir: The path to the directory containing NIfTI files.
        :type nifti_dir: str
        :param dicom_info: A dictionary of DICOM file information.
        :type dicom_info: dict
        :return: None
        """
        for filename in os.listdir(nifti_dir):
            if filename.endswith('.nii'):
                modality = dicom_info.get(filename, '')
                if modality:
                    new_filename = f"{modality}_{filename}"
                    os.rename(os.path.join(nifti_dir, filename), os.path.join(nifti_dir, new_filename))
                    del dicom_info[filename]

    def split4d(self, nifti_file: str, out_dir: str) -> None:
        """
        Splits a 4D NIfTI file into 3D NIfTI files.

        :param nifti_file: The path to the 4D NIfTI file.
        :type nifti_file: str
        :param out_dir: The path to the output directory.
        :type out_dir: str
        :return: None
        """
        split_nifti_files = nib.funcs.four_to_three(nib.funcs.squeeze_image(nib.load(nifti_file)))
        i = 0
        for file in split_nifti_files:
            # vol should be named as vol0000.nii, vol0001.nii, etc.

            nib.save(file, os.path.join(out_dir, 'vol' + str(i).zfill(4) + '.nii.gz'))
            i += 1

    def convert(self):
        """
        Converts input files to NIfTI format and splits 4D NIfTI files into 3D NIfTI files.

        :return: The path to the directory containing the split NIfTI files.
        :rtype: str
        """
        if os.path.isdir(self.input_directory):
            self.non_nifti_to_nifti(self.input_directory, self.output_directory)
        else:
            print(f"Input {self.input_directory} is not a directory.")
            return

        nifti_files = []
        for root, dirs, files in os.walk(self.output_directory):
            for file in files:
                if file.endswith(('.nii', '.nii.gz')):
                    nifti_files.append(os.path.join(root, file))

        for file in nifti_files:
            nifti_image = nib.load(file)
            if len(nifti_image.shape) == 4:
                self.split4d(file, self.split_nifti_directory)
                nifti_files.remove(file)

        if len(nifti_files) == 1:
            print(" Error: Motion correction cannot be performed on a single 3D image.")

        return self.split_nifti_directory


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
