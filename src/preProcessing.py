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
import mpire


def blur_image_c3d(input_image: str, output_image: str, shrink_factor: int) -> None:
    """
    Blurs an image with a shrink factor parameter based kernel
    :param input_image: path to input image
    :param output_image: path to output image
    :param shrink_factor: kernel modifier
    """
    gauss_variance = (shrink_factor / 2) ** 2
    gauss_variance = int(gauss_variance)
    run_cmd = f"c3d {input_image} " \
              f"-smooth-fast {gauss_variance}x{gauss_variance}x{gauss_variance}vox " \
              f"-o {output_image}"
    subprocess.run(run_cmd, shell=True, capture_output=True)


def resample_image_c3d(input_image: str, output_image: str, shrink_factor: int) -> None:
    """
    Resamples an image based on a shrink factor
    :param input_image: path to input image
    :param output_image: path to output image
    :param shrink_factor: kernel modifier
    """
    shrink_percentage = str(int(100 / shrink_factor))
    run_cmd = f"c3d {input_image} " \
              f"-resample {shrink_percentage}x{shrink_percentage}x{shrink_percentage}% " \
              f"-o {output_image}"

    subprocess.run(run_cmd, shell=True, capture_output=True)


def downsample_image(input_image: str, output_directory: str, shrink_factor: int) -> str:
    """
    Creates a downsampled version of the input image based on the downsampling_factor
    :param input_image: image to downsample
    :param output_directory: folder to write files to
    :param shrink_factor: shrink factor to downsample image by
    :return: path to the downsampled input_image
    """
    input_image_name = os.path.basename(input_image)

    # Blur and resample the input image
    input_image_blurred = os.path.join(output_directory, f"{shrink_factor}x_blurred_{input_image_name}")
    blur_image_c3d(input_image, input_image_blurred, shrink_factor)
    input_image_downsampled = os.path.join(output_directory, f"{shrink_factor}x_resampled_{input_image_name}")
    resample_image_c3d(input_image_blurred, input_image_downsampled, shrink_factor)

    return input_image_downsampled


def compute_MI(image1: str, image2: str) -> float:
    """
    Compares two images and computes their mutual information
    :param image1: first image of image pair to compare
    :param image2: second image of image pair to compare
    :return: Computed mutual information as float and absolute value (only positive)
    :rtype: float
    """
    # SimpleITK
    sitk_image1 = sitk.ReadImage(image1)
    sitk_image2 = sitk.ReadImage(image2)
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation()
    MI = abs(registration_method.MetricEvaluate(sitk_image1, sitk_image2))
    return MI


def find_start_frame(folder: str) -> int:
    """
    Determines the starting frame of a 4D series by a thresholding approach.
    :param folder: Folder where multiple 3D volumes of a 4D series are located.
    :return: Index of starting frame
    :rtype: int
    """

    # get files
    files = fop.get_files(folder, "*.nii*")

    # create pyramid folder to dump images to
    pyramid_path = fop.make_dir(folder, "pyramid")

    # blur and resample the reference frame
    file_index_reference = len(files) - 1
    reference_image = os.path.join(folder, files[file_index_reference])
    reference_image_resampled = downsample_image(reference_image, pyramid_path, 4)

    # get threshold from MIs of original files
    sample_stop = len(files)
    sample_size = int(sample_stop * 0.20)
    sample_start = sample_stop - sample_size
    print(f"Computing threshold between file {files[sample_start]} and {files[sample_stop - 1]}")

    # calculate the reference MI
    reference_MI_sum = 0
    for sample_index in range(sample_start, sample_stop):
        current_image = os.path.join(folder, files[sample_index])
        current_MI = compute_MI(reference_image, current_image)
        reference_MI_sum = reference_MI_sum + current_MI
    MI_threshold = reference_MI_sum / sample_size
    print(f"MI threshold: {MI_threshold}")

    # search for starting frame
    starting_frame = 0
    for file_index in range(len(files)):
        current_image = os.path.join(folder, files[file_index])
        # Blur and resample the frame to investigate
        current_image_resampled = downsample_image(current_image, pyramid_path, 4)

        # Compute MI
        current_MI = compute_MI(reference_image_resampled, current_image_resampled)

        if current_MI > MI_threshold:
            starting_frame = file_index
            print(f"Threshold: Starting frame found at index {starting_frame}, file {files[starting_frame]}")
            break

    return starting_frame
