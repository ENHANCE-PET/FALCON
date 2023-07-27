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
# This module handles image processing for the falconz.
#
# Usage:
# The functions in this module can be imported and used in other modules within the falconz to perform image conversion.
#
# ----------------------------------------------------------------------------------------------------------------------

import os
import pathlib
import re
import subprocess
import logging
import multiprocessing
from tqdm import tqdm
import SimpleITK
import nibabel
import pandas as pd
from nilearn.input_data import NiftiMasker


class GreedyException(Exception):
    pass


class GreedyCommand:
    def __init__(self, cmd_name, fixed_img, moving_img, cost_function, multi_resolution_iterations, dof, out_file):
        self.cmd_name = cmd_name
        self.fixed_img = fixed_img
        self.moving_img = moving_img
        self.cost_function = cost_function
        self.multi_resolution_iterations = multi_resolution_iterations
        self.dof = dof
        self.out_file = out_file

    def _generate_command(self):
        return f"greedy -d 3 -a -i {re.escape(self.fixed_img)} {re.escape(self.moving_img)} -ia-image-centers -dof {self.dof} -o {re.escape(self.out_file)} -n {self.multi_resolution_iterations} -m {self.cost_function}"

    def run(self):
        cmd = self._generate_command()
        result = subprocess.run(cmd, shell=True, capture_output=True)

        if result.returncode != 0:
            raise GreedyException(f"Command '{cmd}' failed with error: {result.stderr}")

        logging.info(
            f"{self.cmd_name} alignment: {pathlib.Path(self.moving_img).name} -> {pathlib.Path(self.fixed_img).name} | Aligned image: moco-{pathlib.Path(self.moving_img).name} | Cost function: {self.cost_function} | Initial alignment: Image centers | Transform file: {pathlib.Path(self.out_file).name}")

        return self.out_file


class Registration:
    def __init__(self, fixed_img, moving_img, cost_function, multi_resolution_iterations):
        self.fixed_img = fixed_img
        self.moving_img = moving_img
        self.cost_function = cost_function
        self.multi_resolution_iterations = multi_resolution_iterations
        self.out_dir = pathlib.Path(moving_img).parent
        self.moving_img_filename = pathlib.Path(moving_img).name

    def register(self):
        raise NotImplementedError


class RigidRegistration(Registration):
    def register(self):
        rigid_transform_file = os.path.join(self.out_dir, f"{self.moving_img_filename}_rigid.mat")
        cmd = GreedyCommand("Rigid", self.fixed_img, self.moving_img, self.cost_function,
                            self.multi_resolution_iterations, 6, rigid_transform_file)
        return cmd.run()


class AffineRegistration(Registration):
    def register(self):
        affine_transform_file = os.path.join(self.out_dir, f"{self.moving_img_filename}_affine.mat")
        cmd = GreedyCommand("Affine", self.fixed_img, self.moving_img, self.cost_function,
                            self.multi_resolution_iterations, 12, affine_transform_file)
        return cmd.run()


class DeformableRegistration(Registration):
    def register(self):
        warp_file = os.path.join(self.out_dir, f"{self.moving_img_filename}_warp.nii.gz")
        inverse_warp_file = os.path.join(self.out_dir, f"{self.moving_img_filename}_inverse_warp.nii.gz")
        affine_transform_file = AffineRegistration(self.fixed_img, self.moving_img, self.cost_function,
                                                   self.multi_resolution_iterations).register()
        cmd = GreedyCommand("Deformable", self.fixed_img, self.moving_img, self.cost_function,
                            self.multi_resolution_iterations, 6, warp_file)
        return cmd.run()


class ImageResampler:
    def __init__(self, fixed_img, moving_img, resampled_moving_img, registration_type, segmentation="",
                 resampled_seg=""):
        self.fixed_img = fixed_img
        self.moving_img = moving_img
        self.resampled_moving_img = resampled_moving_img
        self.registration_type = registration_type
        self.segmentation = segmentation
        self.resampled_seg = resampled_seg
        self.out_dir = pathlib.Path(moving_img).parent
        self.moving_img_file = pathlib.Path(moving_img).name

    def resample(self):
        if self.registration_type == 'rigid':
            transform_file = os.path.join(self.out_dir, f"{self.moving_img_file}_rigid.mat")
        elif self.registration_type == 'affine':
            transform_file = os.path.join(self.out_dir, f"{self.moving_img_file}_affine.mat")
        elif self.registration_type == 'deformable':
            transform_file = os.path.join(self.out_dir, f"{self.moving_img_file}_warp.nii.gz")
        else:
            raise GreedyException("Registration type not supported!")

        if self.segmentation and self.resampled_seg:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(self.fixed_img)} -ri LINEAR -rm {re.escape(self.moving_img)} " \
                         f"{re.escape(self.resampled_moving_img)} -ri LABEL 0.2vox -rm {re.escape(self.segmentation)} " \
                         f"{re.escape(self.resampled_seg)} -r {re.escape(transform_file)}"
        else:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(self.fixed_img)} -ri LINEAR -rm {re.escape(self.moving_img)} " \
                         f"{re.escape(self.resampled_moving_img)} -r {re.escape(transform_file)}"

        subprocess.run(cmd_to_run, shell=True, capture_output=True)


class ImageAligner:
    def __init__(self, n_jobs):
        self.n_jobs = n_jobs

    def align(self, fixed_img, moving_imgs, registration_type, multi_resolution_iterations, moco_dir):
        logging.info("Aligning images...")

        with multiprocessing.Pool(self.n_jobs) as p:
            max_ = len(moving_imgs)
            with tqdm(total=max_, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}', ncols=70, colour='violet') as pbar:
                for i, _ in tqdm(enumerate(p.imap_unordered(self.align_single, [
                    (fixed_img, img, registration_type, multi_resolution_iterations, moco_dir) for img in
                    moving_imgs]))):
                    pbar.update()
                    if pbar.n == max_:
                        pbar.colour = 'green'

    def align_single(self, align_param):
        fixed_img, moving_img, registration_type, multi_resolution_iterations, moco_dir = align_param

        if registration_type == 'rigid':
            registration = RigidRegistration(fixed_img, moving_img, 'NMI', multi_resolution_iterations)
        elif registration_type == 'affine':
            registration = AffineRegistration(fixed_img, moving_img, 'NMI', multi_resolution_iterations)
        elif registration_type == 'deformable':
            registration = DeformableRegistration(fixed_img, moving_img, 'NCC 2x2x2', multi_resolution_iterations)
        else:
            raise GreedyException("Registration type not supported!")

        registration.register()

        resampler = ImageResampler(fixed_img, moving_img,
                                   os.path.join(moco_dir, 'moco-' + pathlib.Path(moving_img).name), registration_type)
        resampler.resample()


def get_dimensions(nifti_file: str) -> int:
    """
    Get the dimensions of a NIFTI image file
    :param nifti_file: NIFTI file to check
    """
    nifti_img = SimpleITK.ReadImage(nifti_file)
    img_dim = nifti_img.GetDimension()
    return img_dim


def get_pixel_id_type(nifti_file: str) -> str:
    """
    Get the pixel id type of a NIFTI image file
    :param nifti_file: NIFTI file to check
    """
    nifti_img = SimpleITK.ReadImage(nifti_file)
    pixel_id_type = nifti_img.GetPixelIDTypeAsString()
    return pixel_id_type


def get_intensity_statistics(nifti_file: str, multi_label_file: str) -> object:
    """
    Get the intensity statistics of a NIFTI image file
    :param nifti_file: NIFTI file to check
    :param multi_label_file: Multilabel file that is used to calculate the intensity statistics from nifti_file
    :return: stats_df, a dataframe with the intensity statistics
    """
    nifti_img = SimpleITK.ReadImage(nifti_file)
    multi_label_img = SimpleITK.ReadImage(multi_label_file)
    intensity_statistics = SimpleITK.LabelIntensityStatisticsImageFilter()
    intensity_statistics.Execute(multi_label_img, nifti_img)
    stats_list = [(intensity_statistics.GetMean(i), intensity_statistics.GetStandardDeviation(i),
                   intensity_statistics.GetMedian(i), intensity_statistics.GetMaximum(i),
                   intensity_statistics.GetMinimum(i)) for i in intensity_statistics.GetLabels()]
    columns = ['Mean', 'Standard Deviation', 'Median', 'Maximum', 'Minimum']
    stats_df = pd.DataFrame(data=stats_list, index=intensity_statistics.GetLabels(), columns=columns)
    return stats_df


def get_body_mask(nifti_file: str, mask_file: str) -> str:
    """
    Get time activity curves from a 4d nifti file
    :param nifti_file: 4d nifti file to get the time activity curves from
    :param mask_file: Name of the mask file that is derived from the 4d nifti file.
    :return: path of the mask file
    """
    nifti_masker = NiftiMasker(mask_strategy='epi', memory="nilearn_cache", memory_level=2, smoothing_fwhm=8)
    nifti_masker.fit(nifti_file)
    nibabel.save(nifti_masker.mask_img_, mask_file)
    return mask_file


def mask_img(nifti_file: str, mask_file: str, masked_file: str) -> str:
    """
    Mask a NIFTI image file with a mask file
    :param nifti_file: NIFTI file to mask
    :param mask_file: Mask file to mask the nifti_file with
    :param masked_file: Name of the masked file
    :return: path of the masked nifti file
    """
    img = SimpleITK.ReadImage(nifti_file)
    mask = SimpleITK.ReadImage(mask_file, SimpleITK.sitkFloat32)
    masked_img = SimpleITK.Compose(
        [SimpleITK.Multiply(SimpleITK.VectorIndexSelectionCast(img, i), mask) for i in
         range(img.GetNumberOfComponentsPerPixel())])
    SimpleITK.WriteImage(SimpleITK.Cast(masked_img, SimpleITK.sitkVectorFloat32), masked_file)
    return masked_file
