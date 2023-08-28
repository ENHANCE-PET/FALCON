#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# Author: Lalith Kumar Shiyam Sundar
#
# Institution: Medical University of Vienna
# Research Group: Quantitative Imaging and Medical Physics (QIMP) Team
# Date: 07.07.2023
# Version: 2.0.0
#
# Description:
# This module handles image conversion for the falconz.
#
# Usage:
# The functions in this module can be imported and used in other modules within the falconz to perform image conversion.
#
# ----------------------------------------------------------------------------------------------------------------------

import os
import SimpleITK
import pydicom
import dicom2nifti
import nibabel as nib
import re
import unicodedata
import contextlib
import io
from typing import Optional
import dcm2niix


class ImageConverter:
    def __init__(self, input_directory: str, output_directory: str):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.split_nifti_directory = os.path.join(self.output_directory, 'split-nifti-files')

        if not os.path.exists(self.split_nifti_directory):
            os.makedirs(self.split_nifti_directory)

    def non_nifti_to_nifti(self, input_path: str, output_directory: Optional[str] = None) -> None:
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
        try:
            unicode_filename = str(unicode_filename).replace(" ", "_")
            cleaned_filename = unicodedata.normalize('NFKD', unicode_filename).encode('ASCII', 'ignore').decode('ASCII')
            cleaned_filename = re.sub(r'[^\w\s-]', '', cleaned_filename.strip().lower())
            cleaned_filename = re.sub(r'[-\s]+', '-', cleaned_filename)
            return cleaned_filename
        except:
            return unicode_filename

    def is_dicom_file(self, filename):
        try:
            pydicom.dcmread(filename)
            return True
        except pydicom.errors.InvalidDicomError:
            return False

    def create_dicom_lookup(self, dicom_dir):
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
        for filename in os.listdir(nifti_dir):
            if filename.endswith('.nii'):
                modality = dicom_info.get(filename, '')
                if modality:
                    new_filename = f"{modality}_{filename}"
                    os.rename(os.path.join(nifti_dir, filename), os.path.join(nifti_dir, new_filename))
                    del dicom_info[filename]

    def split4d(self, nifti_file: str, out_dir: str) -> None:
        split_nifti_files = nib.funcs.four_to_three(nib.funcs.squeeze_image(nib.load(nifti_file)))
        i = 0
        for file in split_nifti_files:
            nib.save(file, os.path.join(out_dir, 'vol' + str(i) + '.nii'))
            i += 1

    def convert(self):
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
