#!/usr/bin/env python
# -*- coding: utf-8 -*-


# **********************************************************************************************************************
# File: preProcessing.py
# Project: FALCON
# Created: 30.05.2022
# Author: Sebastian Gutschmayer, M.Sc. | Lalith Kumar Shiyam Sundar Ph.D.
# Email: Sebastian.Gutschmayer@meduniwien.ac.at | lalith.shiyamsundar@meduniwien.ac.at
# Institute: Quantitative Imaging and Medical Physics, Medical University of Vienna
# Description: Library for preprocessing operations such as determining starting frame in a 4D series based on MI.
# License: Apache 2.0
# **********************************************************************************************************************


import subprocess
import os
import SimpleITK as sitk
import fileOp as fop
from mpire import WorkerPool
import constants as c
from statistics import mean


def downscale_image(downscale_param: tuple, input_image: str) -> str:
    """
    Downscales an image based on the shrink factor and writes it to the output directory
    :param downscale_param: output_dir (str), shrink_factor (int) packed in a tuple
    :param input_image: input image to downscale
    :return: path to downscaled image
    """
    output_dir, shrink_factor = downscale_param
    input_image_name = os.path.basename(input_image)
    # Blur the input image first
    input_image_blurred = os.path.join(output_dir, f"{shrink_factor}x_blurred_{input_image_name}")
    gauss_variance = (shrink_factor / 2) ** 2
    gauss_variance = int(gauss_variance)
    cmd_to_smooth = f"c3d {input_image} -smooth-fast {gauss_variance}x{gauss_variance}x{gauss_variance}vox -o" \
                    f" {input_image_blurred} "
    subprocess.run(cmd_to_smooth, shell=True, capture_output=True)
    # Resample the smoothed input image later
    input_image_downscaled = os.path.join(output_dir, f"{shrink_factor}x_downscaled_{input_image_name}")
    shrink_percentage = str(int(100 / shrink_factor))
    cmd_to_downscale = f"c3d {input_image_blurred} -resample {shrink_percentage}x{shrink_percentage}x" \
                       f"{shrink_percentage}% -o {input_image_downscaled}"
    subprocess.run(cmd_to_downscale, shell=True, capture_output=True)
    return input_image_downscaled


def compute_mi(image1: str, image2: str) -> float:
    """
    Compares two images and computes their mutual information
    :param image1: first image of image pair to compare
    :param image2: second image of image pair to compare
    :return: Computed mutual information as float
    :rtype: float
    """
    sitk_img1 = sitk.ReadImage(image1)
    sitk_img2 = sitk.ReadImage(image2)
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation()
    mi = abs(registration_method.MetricEvaluate(sitk_img1, sitk_img2))
    return mi


def determine_starting_frame(pet_files: list, njobs) -> int:
    """
    Determines the starting frame of a 4D PET series from which motion correction can be performed by using mutual
    information.
    :param pet_files: list of 3D PET files
    :param njobs: number of jobs to run in parallel
    :return:  Index of the starting frame from which motion correction can be performed
    :rtype: int
    """

    pet_folder = os.path.dirname(pet_files[0])

    # Create the folder to dump the gaussian pyramid images
    pyramid_dir = fop.make_dir(pet_folder, "pyramid")

    # Downscale the 3d pet files to a lower resolution (1/4x)

    with WorkerPool(n_jobs=njobs, shared_objects=(pyramid_dir, c.SHRINK_LEVEL_4x),
                    start_method='fork', ) as pool:
        pool.map(downscale_image, pet_files, progress_bar=False)

    # Compute mutual information between the last 20% of the original PET images and the last frame.

    mi_list = []
    for i in range(int(len(pet_files) * c.MI_REFERENCE_PERCENTAGE), len(pet_files) - 1):
        mi_list.append(compute_mi(pet_files[i], pet_files[-1]))
    mi_threshold = mean(mi_list)

    # Find the starting frame from which motion correction can be performed

    downscaled_pet_files = fop.get_files(pyramid_dir, "*downscaled*nii*")

    for i in range(len(downscaled_pet_files) - 1):
        if compute_mi(downscaled_pet_files[i], downscaled_pet_files[-1]) > mi_threshold:
            return i
