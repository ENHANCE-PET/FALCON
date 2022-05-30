#!/usr/bin/env python
# -*- coding: utf-8 -*-


# **********************************************************************************************************************
# File: preProcessing.py
# Project: FALCON
# Created: 30.05.2022
# Author: Lalith Kumar Shiyam Sundar
# Email: lalith.shiyamsundar@meduniwien.ac.at
# Institute: Quantitative Imaging and Medical Physics, Medical University of Vienna
# Description: Library for preprocessing operations such as determining starting frame in a 4D series based on MI.
# License: Apache 2.0
# **********************************************************************************************************************


import subprocess
import os
import SimpleITK as sitk
import fileOp as fop


def blur_image_c3d(input_image: str, output_image: str, shrink_factor: int) -> None:
    """
    Blurs an image with a shrink factor parameter based kernel
    :param input_image: path to input image
    :param output_image: path to output image
    :param shrink_factor: kernel modifier
    """
    gauss_variance = (shrink_factor / 2) ** 2
    gauss_variance = int(gauss_variance)
    cmd_to_smooth = f"c3d {input_image} " \
                    f"-smooth-fast {gauss_variance}x{gauss_variance}x{gauss_variance}vox " \
                    f"-o {output_image}"
    subprocess.run(cmd_to_smooth, shell=True, capture_output=True)


def resample_image_c3d(input_image: str, output_image: str, shrink_factor: int) -> None:
    """
    Resamples an image based on a shrink factor
    :param input_image: path to input image
    :param output_image: path to output image
    :param shrink_factor: kernel modifier
    """
    shrink_percentage = str(int(100 / shrink_factor))
    cmd_to_run = f"c3d {input_image} " \
                 f"-resample {shrink_percentage}x{shrink_percentage}x{shrink_percentage}% " \
                 f"-o {output_image}"

    subprocess.run(cmd_to_run, shell=True, capture_output=True)


def computeMI(image1: str, image2: str) -> float:
    """
    Compares two images and computes their mutual information
    :param image1: first image of image pair to compare
    :param image2: second image of image pair to compare
    :return: Computed mutual information as float
    :rtype: float
    """
    # SimpleITK
    img1 = sitk.ReadImage(image1)
    img2 = sitk.ReadImage(image2)
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation()
    MI = registration_method.MetricEvaluate(img1, img2)
    return MI


def determine_starting_frame_by_threshold(folder: str) -> int:
    """
    Determines the starting frame of a 4D series by a thresholding approach.
    :param folder: Folder where multiple 3D volumes of a 4D series are located.
    :return: Index of starting frame
    :rtype: int
    """

    # get files
    files = fop.get_files(folder, "*.nii*")

    # create pyramid folder to dump images to
    pyramid_path = os.path.join(folder, "pyramid")
    if not os.path.exists(pyramid_path):
        os.mkdir(pyramid_path)

    # blur and resample the reference frame
    file_index_reference = len(files) - 1
    reference_image = os.path.join(folder, files[file_index_reference])
    reference_image_blurred = os.path.join(pyramid_path, f"blurred_{files[file_index_reference]}")
    blur_image_c3d(reference_image, reference_image_blurred, 4)
    reference_image_resampled = os.path.join(pyramid_path, f"resampled_{files[file_index_reference]}")
    resample_image_c3d(reference_image_blurred, reference_image_resampled, 4)

    # get threshold from MIs of original files
    sample_size = 4
    sample_stop = len(files)
    sample_start = sample_stop - sample_size
    print(f"Computing threshold between file {files[sample_start]} and {files[sample_stop - 1]}")

    # calculate the reference MI
    reference_MI_sum = 0
    for sample_index in range(sample_start, sample_stop):
        current_image = os.path.join(folder, files[sample_index])
        current_MI = computeMI(reference_image, current_image)
        reference_MI_sum = reference_MI_sum + current_MI
    MI_threshold = reference_MI_sum / sample_size
    print(f"MI threshold: {MI_threshold}")

    # search for starting frame
    starting_frame = 0
    for file_index in range(len(files)):
        current_image = os.path.join(folder, files[file_index])
        # Blur and resample the frame to investigate
        current_image_blurred = os.path.join(pyramid_path, f"blurred_{files[file_index]}")
        blur_image_c3d(current_image, current_image_blurred, 4)
        current_image_resampled = os.path.join(pyramid_path, f"resampled_{files[file_index]}")
        resample_image_c3d(current_image_blurred, current_image_resampled, 4)

        # Compute MI
        current_MI = computeMI(reference_image_resampled, current_image_resampled)

        if current_MI < MI_threshold:
            starting_frame = file_index
            print(f"Threshold: Starting frame found at index {starting_frame}, file {files[starting_frame]}")
            break

    return starting_frame
