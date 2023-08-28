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

import SimpleITK as sitk
import logging
import multiprocessing
import nibabel
import os
import pandas as pd
import pathlib
import re
import subprocess
from halo import Halo
from mpire import WorkerPool
from nilearn.input_data import NiftiMasker
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm

from falconz import constants
from falconz import file_utilities as fop
from dask import delayed, compute

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
    nifti_img = sitk.ReadImage(nifti_file)
    img_dim = nifti_img.GetDimension()
    return img_dim


def get_pixel_id_type(nifti_file: str) -> str:
    """
    Get the pixel id type of a NIFTI image file
    :param nifti_file: NIFTI file to check
    """
    nifti_img = sitk.ReadImage(nifti_file)
    pixel_id_type = nifti_img.GetPixelIDTypeAsString()
    return pixel_id_type


def get_intensity_statistics(nifti_file: str, multi_label_file: str) -> object:
    """
    Get the intensity statistics of a NIFTI image file
    :param nifti_file: NIFTI file to check
    :param multi_label_file: Multilabel file that is used to calculate the intensity statistics from nifti_file
    :return: stats_df, a dataframe with the intensity statistics
    """
    nifti_img = sitk.ReadImage(nifti_file)
    multi_label_img = sitk.ReadImage(multi_label_file)
    intensity_statistics = sitk.LabelIntensityStatisticsImageFilter()
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
    img = sitk.ReadImage(nifti_file)
    mask = sitk.ReadImage(mask_file, sitk.sitkFloat32)
    masked_img = sitk.Compose(
        [sitk.Multiply(sitk.VectorIndexSelectionCast(img, i), mask) for i in
         range(img.GetNumberOfComponentsPerPixel())])
    sitk.WriteImage(sitk.Cast(masked_img, sitk.sitkVectorFloat32), masked_file)
    return masked_file


class FrameSelector:

    def __init__(self, n_jobs, ncc_radius=constants.NCC_RADIUS, ncc_threshold=constants.NCC_THRESHOLD):
        self.n_jobs = n_jobs
        self.ncc_radius = ncc_radius
        self.ncc_threshold = ncc_threshold

    def _gaussian_smoothing(self, image, variance):
        """Smooth the image using Gaussian blur."""
        return sitk.SmoothingRecursiveGaussian(image, variance)

    def downscale_image(self, downscale_param: tuple, input_image: str) -> str:
        output_dir, shrink_factor = downscale_param
        input_image_name = os.path.basename(input_image)
        input_image_sitk = sitk.ReadImage(input_image)

        # Blur the input image first
        input_image_blurred = self._gaussian_smoothing(input_image_sitk, (shrink_factor / 2) ** 2)
        blurred_path = os.path.join(output_dir, f"{shrink_factor}x_blurred_{input_image_name}")
        sitk.WriteImage(input_image_blurred, blurred_path)

        # Resample the smoothed input image
        resample_factor = [1.0 / shrink_factor] * input_image_sitk.GetDimension()
        resampler = sitk.ResampleImageFilter()
        resampler.SetSize([int(sz * rf) for sz, rf in zip(input_image_sitk.GetSize(), resample_factor)])
        resampler.SetOutputSpacing([sp * rf for sp, rf in zip(input_image_sitk.GetSpacing(), resample_factor)])
        input_image_downscaled = resampler.Execute(input_image_blurred)
        downscaled_path = os.path.join(output_dir, f"{shrink_factor}x_downscaled_{input_image_name}")
        sitk.WriteImage(input_image_downscaled, downscaled_path)

        return downscaled_path

    @delayed
    def calc_mean_intensity(self, image: str) -> float:
        image_sitk = sitk.ReadImage(image)
        return sitk.GetArrayViewFromImage(image_sitk).mean()


    @delayed
    def calc_voxelwise_ncc_images(self, image1: str, image2: str, output_dir: str) -> str:
        # Get the names of the images without extensions
        image1_name = os.path.basename(image1).split(".")[0]
        image2_name = os.path.basename(image2).split(".")[0]

        # Specify the output path for the resulting NCC image
        output_image = os.path.join(output_dir, f"ncc_{image2_name}.nii.gz")

        # Load the images using SimpleITK
        image1_sitk = sitk.ReadImage(image1)
        image2_sitk = sitk.ReadImage(image2)

        # Create a filter to calculate NCC and set the radius
        ncc_filter = sitk.NormalizedCorrelationImageFilter()
        # Execute the filter to get the NCC image
        ncc_image = ncc_filter.Execute(image1_sitk, image2_sitk, image1_sitk)
        # Clamp the image to remove negative values
        ncc_image = sitk.Clamp(ncc_image, lowerBound=0)

        # Save the result
        sitk.WriteImage(ncc_image, output_image)

        return output_image

    def determine_candidate_frames(self, candidate_files: list, reference_file: str, output_dir: str) -> int:
        ncc_dir = os.path.join(output_dir, "ncc-images")
        fop.create_directory(ncc_dir)
        print(ncc_dir)

        ncc_images = [self.calc_voxelwise_ncc_images(reference_file, file, ncc_dir) for file in candidate_files]
        ncc_images = compute(*ncc_images)  # Execute parallel computation

        mean_intensities = [self.calc_mean_intensity(ncc_image) for ncc_image in ncc_images]
        mean_intensities = compute(*mean_intensities)  # Execute parallel computation

        max_observed_ncc = sum(sorted(mean_intensities, reverse=True)[:3]) / 3
        candidate_frames = [i for i, mean_intensity in enumerate(mean_intensities) if
                            mean_intensity > self.ncc_threshold * max_observed_ncc]

        return candidate_frames[0]
