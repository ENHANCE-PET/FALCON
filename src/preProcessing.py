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
import logging
import os
import re
import subprocess
from statistics import mean
import pathlib
import SimpleITK as sitk
from halo import Halo
from mpire import WorkerPool
import constants as c
import fileOp as fop
from skimage.metrics import structural_similarity as ssim


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
    cmd_to_smooth = f"c3d {re.escape(input_image)} -smooth-fast {gauss_variance}x{gauss_variance}x{gauss_variance}vox -o" \
                    f" {re.escape(input_image_blurred)} "
    subprocess.run(cmd_to_smooth, shell=True, capture_output=True)
    # Resample the smoothed input image later
    input_image_downscaled = os.path.join(output_dir, f"{shrink_factor}x_downscaled_{input_image_name}")
    shrink_percentage = str(int(100 / shrink_factor))
    cmd_to_downscale = f"c3d {re.escape(input_image_blurred)} -resample {shrink_percentage}x{shrink_percentage}x" \
                       f"{shrink_percentage}% -o {re.escape(input_image_downscaled)}"
    subprocess.run(cmd_to_downscale, shell=True, capture_output=True)
    return input_image_downscaled


# Calculate the mean intensity of an image using SimpleITK
def calc_mean_intensity(image: str) -> float:
    """
    Calculates the mean intensity of an image using SimpleITK
    :param image: path to the image
    :return: mean intensity of the image
    :rtype: float
    """
    image = sitk.ReadImage(image, sitk.sitkFloat32)
    return sitk.GetArrayFromImage(image).mean()


def calc_voxelwise_ncc_images(image1: str, image2: str, output_dir: str) -> str:
    """
    Calculates voxelwise normalized cross correlation between two images and writes it to the output directory
    :param image1: path to the first image
    :param image2: path to the second image
    :param output_dir: path to the output directory
    :return: path to the voxelwise ncc image
    """
    # get the image names without the extension '.nii.gz'
    image1_name = os.path.basename(image1).split(".")[0]
    image2_name = os.path.basename(image2).split(".")[0]
    output_image = os.path.join(output_dir, f"ncc_{image2_name}.nii.gz")
    c3d_cmd = f"c3d {re.escape(image1)} {re.escape(image2)} -ncc {c.NCC_RADIUS} -o {re.escape(output_image)}"
    subprocess.run(c3d_cmd, shell=True, capture_output=True)
    # clip the negative correlations to zero
    c3d_cmd = f"c3d {re.escape(output_image)} -clip 0 inf -o {re.escape(output_image)}"
    subprocess.run(c3d_cmd, shell=True, capture_output=True)
    return output_image


def determine_candidate_frames(pet_files: list, ref_frame_index: int, njobs: int) -> int:
    """
    Determines the candidate frames of a 4D PET series on which motion correction can be performed effectively
    :param pet_files: list of 3D PET files
    :param ref_frame_index: index of the reference frame
    :param njobs: number of jobs to run in parallel
    :return:  Index of the starting frame from which motion correction can be performed
    :rtype: int
    """
    # Get the parent directory for pet_files
    pet_folder = os.path.dirname(pet_files[0])

    # Create the folder to dump the ncc images
    ncc_dir = fop.make_dir(pet_folder, "ncc-images")

    # isolate the reference frame from the list of PET files
    ref_frame = pet_files[ref_frame_index]

    # store the remaining pet_files without the ref_frame_index as the moving frames
    mov_frames = pet_files[:ref_frame_index] + pet_files[ref_frame_index + 1:]

    # using mpire to run the ncc calculation in parallel
    with WorkerPool(njobs) as pool:
        ncc_images = pool.map(calc_voxelwise_ncc_images, [(ref_frame, file, ncc_dir) for file in mov_frames])

    ncc_images = fop.get_files(ncc_dir, "ncc_*.nii.gz")

    # calculate the mean intensity of files in the ncc folder and store it as mean_intensities
    mean_intensities = [calc_mean_intensity(ncc_image) for ncc_image in ncc_images]
    print(f"Mean intensities of the ncc images: {mean_intensities}")

    # calculate the average value of the top 3 mean intensities
    max_observed_ncc = sum(sorted(mean_intensities, reverse=True)[:3]) / 3
    print(f"Max observed ncc: {max_observed_ncc}")
    # Identify the indices of the frames with mean intensity greater than c.NCC_THRESHOLD * max_observed_ncc
    candidate_frames = [i for i, mean_intensity in enumerate(mean_intensities) if
                        mean_intensity > c.NCC_THRESHOLD * max_observed_ncc]
    print(f"Candidate frames: {candidate_frames}")
    print(f"Candidate frames selected : {candidate_frames[0]}")
    # return the index of the first frame from the candidate frames
    return candidate_frames[0]
